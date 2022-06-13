from typing import Type

from scvimadz.storage.base import BaseStorage

from .base import BaseReference


class GenericReference(BaseReference):
    """
    Generic reference that can be specified to a given model/data store with the init parameters.

    Parameters
    ----------
    model_store
        BaseStorage for the model store
    data_store
        BaseStorage for the data store
    """

    def __init__(
        self,
        model_store: Type[BaseStorage],
        data_store: Type[BaseStorage],
    ):
        self._model_store = model_store
        self._data_store = data_store

    @property
    def model_store(self) -> Type[BaseStorage]:
        return self._model_store

    @property
    def data_store(self) -> Type[BaseStorage]:
        return self._data_store
