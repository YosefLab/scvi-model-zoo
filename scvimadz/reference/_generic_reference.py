from typing import Type

from scvimadz.storage.base import BaseStorage

from .base import BaseReference


class GenericReference(BaseReference):
    """
    Generic reference that can be specified to a given model/data store with the init parameters.

    Parameters
    ----------
    reference_name
        Name of the reference
    model_store
        BaseStorage for the model store
    data_store
        BaseStorage for the data store
    """

    def __init__(
        self,
        reference_name: str,
        model_store: Type[BaseStorage],
        data_store: Type[BaseStorage],
    ):
        self._reference_name = reference_name
        self._model_store = model_store
        self._data_store = data_store

    @property
    def reference_name(self) -> str:
        return self._reference_name

    @property
    def model_store(self) -> Type[BaseStorage]:
        return self._model_store

    @property
    def data_store(self) -> Type[BaseStorage]:
        return self._data_store
