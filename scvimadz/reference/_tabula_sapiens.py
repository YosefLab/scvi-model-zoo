from typing import Type

import pandas as pd
from reference.base import BaseReference
from scvi.model.base import BaseModelClass
from storage import ZenodoStorage


class TabulaSapiensReference(BaseReference):
    def __init__(self, store: ZenodoStorage):
        self._store = store
        self._models = self._list_models()
        self._datasets = self._list_datasets()

    def list_models(self) -> pd.DataFrame:
        """ Lists all available models associated with this reference """
        return self._models

    def list_datasets(self) -> pd.DataFrame:
        """ Lists all available datasets associated with this reference """
        return self._datasets

    def _list_models(self) -> pd.DataFrame:
        """ Internal implementation of :meth:`~list_models` """
        # TODO update `if` condition depdending on how we will store the data on Zenodo
        model_keys = [
            key
            for key in self._store.list_model_keys()
            if key.contains("tabula_sapiens")
        ]
        for model_key in model_keys:
            self._store.load_model(model_key)
            # TODO add model to the dataframe

    def _list_datasets(self) -> pd.DataFrame:
        """ Internal implementation of :meth:`~list_datasets` """
        raise NotImplementedError

    def load_model(
        self, model_id: str, load_anndata: bool = False
    ) -> Type[BaseModelClass]:
        """
        Loads the model with the given id if it exists, else raises an error.

        Parameters
        ----------
        model_id
            id of the model to load
        load_anndata
            Whether or not to load the anndata dataset the model was trained on

        Returns
        -------
        An instance of :class:`~scvi.model.base.BaseModelClass` associated with the given model id.
        """
        raise NotImplementedError
