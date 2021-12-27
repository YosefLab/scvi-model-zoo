import importlib
import shutil
from abc import ABC, abstractmethod
from typing import List, Optional, Type, Union

import anndata
import pandas as pd
import rich_dataframe
from anndata import AnnData
from scvi.model.base import BaseModelClass

from scvimadz._utils import dirname
from scvimadz.storage.base import BaseStorage

_OBJ_TYPE_MODEL = "model"
_OBJ_TYPE_DATASET = "dataset"
_MODELS_METADATA_FILE = "models_metadata.csv"
_DATASETS_METADATA_FILE = "datasets_metadata.csv"


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

    def _get_store_for_object(self, obj_type: str) -> Type[BaseStorage]:
        if obj_type not in [_OBJ_TYPE_MODEL, _OBJ_TYPE_DATASET]:
            raise ValueError(f"Unrecognized obj_type: {obj_type}")
        return self.model_store if obj_type == _OBJ_TYPE_MODEL else self.data_store

    def _get_object_keys(self, obj_type: str) -> List[str]:
        store = self._get_store_for_object(obj_type)
        keys = [
            key
            for key in store.list_keys()
            if key.startswith(self._get_reference_prefix())
        ]
        return keys

    def _list_objects(
        self, obj_type: str, metadata_fn: str, pretty_print: bool = False
    ) -> pd.DataFrame:
        keys = self._get_object_keys(obj_type)
        metadata_file = self._get_store_for_object(obj_type).download_file(metadata_fn)
        df = pd.read_csv(metadata_file, index_col="key").loc[keys]
        if pretty_print:
            rich_dataframe.prettify(
                df,
                row_limit=len(df),
                col_limit=len(df.columns),
                clear_console=False,
            )
        return df

    def list_models(self, pretty_print: bool = False) -> pd.DataFrame:
        """Lists all available models associated with this reference."""
        return self._list_objects(_OBJ_TYPE_MODEL, _MODELS_METADATA_FILE, pretty_print)

    def list_datasets(self, pretty_print: bool = False) -> pd.DataFrame:
        """Lists all available datasets associated with this reference."""
        return self._list_objects(
            _OBJ_TYPE_DATASET, _DATASETS_METADATA_FILE, pretty_print
        )

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
        models = self.list_models()
        # get the cell that contains the cls_name for this model, it will be like: scvi.model.TOTALVI
        model_cls_name = models.loc[model_id, "cls_name"]
        cls = model_cls_name.split(".")[-1]
        module = ".".join(model_cls_name.split(".")[:-1])
        if adata is None:
            model_adata = models.loc[model_id, "train_dataset"]
            adata = self.load_dataset(model_adata)
        model_cls = getattr(importlib.import_module(module), cls)
        model_path = self.model_store.download_file(model_id)
        if model_path.endswith(".zip"):
            shutil.unpack_archive(model_path, f"{dirname(model_path)}")
            model_path = model_path[:-4]  # strip the .zip
        else:
            model_path = dirname(model_path)
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
        data_file = self.data_store.download_file(dataset_id)
        return anndata.read_h5ad(data_file)
