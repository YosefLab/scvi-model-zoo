from abc import ABC, abstractmethod
from typing import Type

import pandas as pd
from scvi.model.base import BaseModelClass


class BaseReference(ABC):
    @abstractmethod
    def list_models(self) -> pd.DataFrame:
        """ Lists all available models associated with this reference """
        pass

    @abstractmethod
    def list_datasets(self) -> pd.DataFrame:
        """ Lists all available datasets associated with this reference """
        pass

    @abstractmethod
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
            Whether or not to load the dataset the model was trained on

        Returns
        -------
        An instance of :class:`~scvi.model.base.BaseModelClass` associated with the given model id.
        """
        pass
