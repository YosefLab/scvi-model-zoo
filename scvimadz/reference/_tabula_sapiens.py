from typing import Type

import pandas as pd
from reference.base import BaseReference
from scvi.model.base import BaseModelClass
from storage import ZenodoStorage


class TabulaSapiensReference(BaseReference):
    def __init__(self):
        self._store = ZenodoStorage("test")
        self._init_models()
        self._init_datasets()

    def _init_models(self) -> None:
        # TODO update `if` condition depdending on how we will store the data on Zenodo
        self._model_keys = [
            key
            for key in self._store.list_model_keys()
            if key.contains("tabula_sapiens")
        ]
        for model_key in self._model_keys:
            self.load_model(model_key)
            # TODO add model to the dataframe with some of its properties

    def _init_datasets(self) -> None:
        raise NotImplementedError

    def list_models(self) -> pd.DataFrame:
        """ Lists all available models associated with this reference """
        return self._models

    def list_datasets(self) -> pd.DataFrame:
        """ Lists all available datasets associated with this reference """
        return self._datasets

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
