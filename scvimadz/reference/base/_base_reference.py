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


class DatasetMetadata:
    def __init__(
        self, tissue: str, is_cite: bool, has_latent_embedding: bool, is_annotated: bool
    ) -> None:
        self._tissue = tissue
        if (
            not isinstance(is_cite, bool)
            or not isinstance(has_latent_embedding, bool)
            or not isinstance(is_annotated, bool)
        ):
            raise ValueError(
                "is_cite, has_latent_embedding, is_annotated must be booleans"
            )
        self._is_cite = is_cite
        self._has_latent_embedding = has_latent_embedding
        self._is_annotated = is_annotated

    @property
    def tissue(self) -> str:
        return self._tissue

    @property
    def is_cite(self) -> bool:
        return self._is_cite

    @property
    def has_latent_embedding(self) -> bool:
        return self._has_latent_embedding

    @property
    def is_annotated(self) -> bool:
        return self._is_annotated


class ModelMetadata:
    def __init__(
        self,
        cls_name: str,
        train_dataset: str,
        n_hidden: int,
        n_layers: int,
        n_latent: int,
        use_observed_lib_size: bool,
        init_params: str,
    ) -> None:
        self._cls_name = cls_name
        self._train_dataset = train_dataset
        self._n_hidden = n_hidden
        self._n_layers = n_layers
        self._n_latent = n_latent
        self._use_observed_lib_size = use_observed_lib_size
        self._init_params = init_params

    @property
    def cls_name(self) -> str:
        return self._cls_name

    @property
    def train_dataset(self) -> str:
        return self._train_dataset

    @property
    def n_hidden(self) -> int:
        return self._n_hidden

    @property
    def n_layers(self) -> int:
        return self._n_layers

    @property
    def n_latent(self) -> int:
        return self._n_latent

    @property
    def use_observed_lib_size(self) -> bool:
        return self._use_observed_lib_size

    @property
    def init_params(self) -> str:
        return self._init_params


class BaseReference(ABC):
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
            if all_keys or not key.endswith("_metadata.csv")
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

    def _augment_objects_df(
        self, obj_type: _Obj_Type, metadata_fn: _Metadata_File, new: dict
    ) -> pd.DataFrame:
        """Add the given record to the datasets or models dataframe and return the updated dataframe."""
        metadata_df = self._list_objects(obj_type, metadata_fn, all_keys=True)
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
        # get the cell that contains the class name for this model, it will be like: scvi.model.TOTALVI
        model_cls_name = models.loc[model_id, "class_name"]
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
            new_file = os.path.join(os.path.dirname(model_path), "model.pt")
            shutil.move(model_path, new_file)
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
            The path to the dataset to save
        token
            Some storage backends (such as Zenodo) require a token. This arg is
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
        dataset_id = f"{str(uuid.uuid4())}.h5ad"
        # Gather dataset metadata
        adata = anndata.read_h5ad(filepath)
        cell_count = adata.n_obs
        gene_count = adata.n_vars
        # Update the metadata csv file
        new = {
            "key": [dataset_id],
            "cell_count": [cell_count],
            "gene_count": [gene_count],
            "tissue": [metadata.tissue],
            "has_cite": [str(metadata.is_cite)],
            "has_latent_embedding": [str(metadata.has_latent_embedding)],
            "is_annotated": [str(metadata.is_annotated)],
        }
        new_metadata_df = self._augment_objects_df(
            _Obj_Type.DATASET, _Metadata_File.DATASETS_METADATA_FILE, new
        )
        new_metadata = io.StringIO(new_metadata_df.to_csv())
        # Upload both files in a single transaction
        files = [
            FileToUpload(filepath, dataset_id),
            FileToUpload(new_metadata, _Metadata_File.DATASETS_METADATA_FILE.value),
        ]
        self.data_store.upload_files(files, token, ok_to_reversion_datastore)
        print(f"Uploaded dataset successfully. Dataset_id is: {dataset_id}.")
        return dataset_id

    def save_model(
        self,
        filepath: str,
        token: Optional[str],
        ok_to_reversion_datastore: Optional[bool],
        metadata: ModelMetadata,
    ) -> str:
        """
        Saves the model at the given path and returns its corresponding model id.

        Parameters
        ----------
        filepath
            The path to the model to save
        token
            Some storage backends (such as Zenodo) require a token. This arg is
            required to remind users to provide an upload token if their backend
            requires one. Provide `None` if not applicable.
        ok_to_reversion_datastore
            Some storage backends (such as Zenodo) require creating a new version
            of the storage to create new files. This arg is required to ask users
            to provide their consent to this consequence. Provide `None` if this is
            not applicable to your storage backend.
        metadata
            Required metadata for this model

        Returns
        -------
        The corresponding model id if the model was saved successfully.
        """
        model_id = f"{str(uuid.uuid4())}.pt"
        # Update the metadata csv file
        new = {
            "key": [model_id],
            "class_name": [metadata.cls_name],
            "train_dataset": [metadata.train_dataset],
            "n_hidden": [str(metadata.n_hidden)],
            "n_layers": [str(metadata.n_layers)],
            "n_latent": [str(metadata.n_latent)],
            "use_observed_lib_size": [str(metadata._use_observed_lib_size)],
            "init_params": [metadata.init_params],
        }
        new_metadata_df = self._augment_objects_df(
            _Obj_Type.MODEL, _Metadata_File.MODELS_METADATA_FILE, new
        )
        new_metadata = io.StringIO(new_metadata_df.to_csv())
        # Upload both files in a single transaction
        files = [
            FileToUpload(filepath, model_id),
            FileToUpload(new_metadata, _Metadata_File.MODELS_METADATA_FILE.value),
        ]
        self.model_store.upload_files(files, token, ok_to_reversion_datastore)
        print(f"Uploaded model successfully. Model_id is: {model_id}.")
        return model_id
