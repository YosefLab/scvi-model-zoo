import importlib
import io
import os
import shutil
import uuid
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional, Type, Union

import anndata
import pandas as pd
import rich_dataframe
from anndata import AnnData
from scvi.model.base import BaseModelClass

from scvimadz.storage.base import BaseStorage, FileToUpload


class _Obj_Type(Enum):
    MODEL = "model"
    DATASET = "dataset"


class _Metadata_File(Enum):
    MODELS_METADATA_FILE = "models_metadata.csv"
    DATASETS_METADATA_FILE = "datasets_metadata.csv"


# TODO move these two into a MetadataManager class that takes an instance of the backend store
# and encapsulates metada retrieval/update logic. It can then be overridden independently
# of the rest if needed
class DatasetMetadata:
    def __init__(self, cell_count: int, is_cite: bool) -> None:
        self._cell_count = cell_count
        self._is_cite = "Yes" if is_cite else "No"

    @property
    def cell_count(self) -> int:
        return self._cell_count

    @property
    def is_cite(self) -> bool:
        return self._is_cite


# TODO in progress...
class ModelMetadata:
    def __init__(self, hyperparameter_alpha: str) -> None:
        self._hyperparameter_alpha = hyperparameter_alpha

    @property
    def hyperparameter_alpha(self) -> str:
        return self._hyperparameter_alpha


class BaseReference(ABC):
    @property
    @abstractmethod
    def reference_name(self) -> str:
        """The name of this reference."""
        pass

    @property
    @abstractmethod
    def model_store(self) -> Type[BaseStorage]:
        """The backend store for models."""
        pass

    @property
    @abstractmethod
    def data_store(self) -> Type[BaseStorage]:
        """The backend store for datasets."""
        pass

    def _get_reference_prefix(self) -> str:
        return f"{self.reference_name}_"  # e.g. tabula_sapiens_

    def _get_store_for_object(self, obj_type: _Obj_Type) -> Type[BaseStorage]:
        if not isinstance(obj_type, _Obj_Type):
            raise ValueError(f"Unrecognized obj_type: {obj_type}")
        return self.model_store if obj_type is _Obj_Type.MODEL else self.data_store

    def _get_object_keys(
        self, obj_type: _Obj_Type, all_keys: bool = False
    ) -> List[str]:
        store = self._get_store_for_object(obj_type)
        keys = [
            key
            for key in store.list_keys()
            if all_keys or key.startswith(self._get_reference_prefix())
        ]
        return keys

    def _list_objects(
        self,
        obj_type: _Obj_Type,
        metadata_fn: _Metadata_File,
        pretty_print: bool = False,
        all_keys: bool = False,
    ) -> pd.DataFrame:
        keys = self._get_object_keys(obj_type, all_keys)
        metadata_file = self._get_store_for_object(obj_type).download_file(
            metadata_fn.value
        )
        df = pd.read_csv(metadata_file, index_col="key")
        df = df.loc[keys] if not all_keys else df
        if pretty_print:
            rich_dataframe.prettify(
                df,
                row_limit=len(df),
                col_limit=len(df.columns),
                clear_console=False,
            )
        return df

    def get_models_df(self, pretty_print: bool = False) -> pd.DataFrame:
        """Lists all available models associated with this reference."""
        return self._list_objects(
            _Obj_Type.MODEL, _Metadata_File.MODELS_METADATA_FILE, pretty_print
        )

    def get_datasets_df(self, pretty_print: bool = False) -> pd.DataFrame:
        """Lists all available datasets associated with this reference."""
        return self._list_objects(
            _Obj_Type.DATASET, _Metadata_File.DATASETS_METADATA_FILE, pretty_print
        )

    def _augment_datasets_df(self, new: dict) -> pd.DataFrame:
        """Add the given record to the datasets_metadata dataframe and return the updated dataframe."""
        if not new["key"][0].startswith(self._get_reference_prefix()):
            raise ValueError(
                f"Can only add new records for reference '{self.reference_name}'"
            )
        metadata_df = self._list_objects(
            _Obj_Type.DATASET, _Metadata_File.DATASETS_METADATA_FILE, all_keys=True
        )
        new_df = pd.DataFrame(new)
        metadata_df = metadata_df.reset_index().append(new_df).set_index("key")
        return metadata_df

    def load_model(
        self,
        model_id: str,
        adata: Optional[AnnData] = None,
        use_gpu: Optional[Union[str, int, bool]] = None,
    ) -> Type[BaseModelClass]:
        """
        Loads the model with the given id if it exists, else raises an error.

        Parameters
        ----------
        model_id
            id of the model to load
        adata
            AnnData object used to initialize the loaded model. If None, will check for and
            load the anndata saved with the model.
        use_gpu
            Load model on default GPU if available (if None or True), or index of GPU to use (if int),
            or name of GPU (if str), or use CPU (if False).

        Returns
        -------
        An instance of :class:`~scvi.model.base.BaseModelClass` associated with the given model id.
        """
        models = self.get_models_df()
        # get the cell that contains the cls_name for this model, it will be like: scvi.model.TOTALVI
        model_cls_name = models.loc[model_id, "cls_name"]
        cls = model_cls_name.split(".")[-1]
        module = ".".join(model_cls_name.split(".")[:-1])
        # We must have an anndata object to load the model with. If no adata is provided, then use
        # the model's metadata to determine where to fetch its associated train dataset from, and
        # use that to load the model
        if adata is None:
            model_adata = models.loc[model_id, "train_dataset"]
            adata = self.load_dataset(model_adata)
        model_cls = getattr(importlib.import_module(module), cls)
        model_path = self.model_store.download_file(model_id)
        if model_path.endswith(".zip"):
            shutil.unpack_archive(model_path, f"{os.path.dirname(model_path)}")
            model_path = model_path[:-4]  # strip the .zip
        else:
            model_path = os.path.dirname(model_path)
        return model_cls.load(model_path, adata=adata, use_gpu=use_gpu)

    def load_dataset(self, dataset_id: str) -> AnnData:
        """
        Loads the dataset with the given id if it exists.

        Parameters
        ----------
        dataset_id
            id of the dataset to load

        Returns
        -------
        An instance of :class:`~anndata.AnnData` associated with the given dataset id.
        """
        data_file_path = self.data_store.download_file(dataset_id)
        return anndata.read_h5ad(data_file_path)

    def save_dataset(
        self,
        filepath: str,
        token: Optional[str],
        ok_to_reversion_datastore: Optional[bool],
        metadata: DatasetMetadata,
    ) -> str:
        """
        Saves the dataset at the given path and returns its corresponding dataset id.

        Parameters
        ----------
        filepath
            the path to the dataset to save
        token
            some storage backends (such as Zenodo) require a token. This arg is
            required to remind users to provide an upload token if their backend
            requires one. Provide `None` if not applicable.
        ok_to_reversion_datastore
            Some storage backends (such as Zenodo) require creating a new version
            of the storage to create new files. This arg is required to ask users
            to provide their consent to this consequence. Provide `None` if this is
            not applicable to your storage backend.
        metadata
            Required metadata for this dataset

        Returns
        -------
        The corresponding dataset id if the dataset was saved successfully.
        """
        dataset_id = f"{self._get_reference_prefix()}dataset_{str(uuid.uuid4())}.h5ad"
        # Update the metadata csv file
        new = {
            "key": [dataset_id],
            "cell_count": [metadata.cell_count],
            "cite": [str(metadata.is_cite)],
        }
        new_metadata_df = self._augment_datasets_df(new)
        new_metadata = io.StringIO(new_metadata_df.to_csv())
        # Upload both files in a single transaction
        files = [
            FileToUpload(filepath, dataset_id),
            FileToUpload(new_metadata, _Metadata_File.DATASETS_METADATA_FILE.value),
        ]
        self.data_store.upload_files(files, token, ok_to_reversion_datastore)
        print(f"Uploaded dataset successfully. Dataset_id is: {dataset_id}.")
        return dataset_id
