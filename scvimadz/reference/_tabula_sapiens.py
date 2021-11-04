# import importlib
from typing import List, Optional, Type, Union

import pandas as pd
from anndata import AnnData
from reference.base import BaseReference
from scvi.model.base import BaseModelClass
from storage import ZenodoStorage

RECORD_NAME_PREFIX = "tabula_sapiens_"


class TabulaSapiensReference(BaseReference):
    def __init__(self):
        self._model_store = ZenodoStorage("test_model_url")
        self._dataset_store = ZenodoStorage("test_dataset_url")

    def _get_object_keys(self, obj_type: str = "model") -> List[str]:
        assert obj_type in ["model", "dataset"]
        store = self._model_store if obj_type == "model" else self._dataset_store
        keys = [key for key in store.list_keys() if key.contains(RECORD_NAME_PREFIX)]
        return keys

    def list_models(self) -> pd.DataFrame:
        """ Lists all available models associated with this reference """
        model_keys = self._get_object_keys("model")
        metadata_file = self._model_store.load_file("models_metadata")
        return pd.read_csv(metadata_file, index_col="key").loc[model_keys]

    def print_models(self) -> None:
        # df = self.list_models()
        # TODO add rich_dataframe to toml
        # rich_dataframe.prettify(
        #     df,
        #     row_limit=len(df),
        #     col_limit=len(df.columns),
        #     clear_console=False,
        # )
        pass

    def list_datasets(self) -> pd.DataFrame:
        """ Lists all available datasets associated with this reference """
        raise NotImplementedError

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
        model_keys = self._get_object_keys("model")
        if model_id in model_keys:
            # model_file = self._model_store.load_file(model_id)
            models = self.list_models()
            # get the cell that contains the cls_name for this model, it will be like: scvi.model.TOTALVI
            # model_cls_name = models.loc[model_id, "cls_name"]
            # cls = model_cls_name.split(".")[-1]
            # module = model_cls_name.split(".")[:-1].join(".")
            # model_cls = getattr(importlib.import_module(module), cls)
            if adata is None:
                model_adata = models.loc[model_id, "train_dataset"]
                adata = self.load_dataset(model_adata)
            # model_cls.load(model_file, adata=adata, use_gpu=use_gpu) <- this doesn't work yet. We need to write a ``load``
            # method in scvi-tools that takes a str object. PyTorch supports it already. Also pin the corresponding scvi-tools
            # version once that's done. TODO
        else:
            raise KeyError(f"No model found with id {model_id}")

    def load_dataset(self, dataset_id: str) -> Type[AnnData]:
        """
        Loads the dataset with the given id if it exists, else raises an error.

        Parameters
        ----------
        dataset_id
            id of the dataset to load

        Returns
        -------
        An instance of :class:`~anndata.AnnData` associated with the given dataset id.
        """
        dataset_keys = self._get_object_keys("dataset")
        if dataset_id in dataset_keys:
            # data_file = self._dataset_store.load_file(dataset_id)
            # TODO how to load anndata from stream?
            pass
        else:
            raise KeyError(f"No dataset found with id {dataset_id}")
