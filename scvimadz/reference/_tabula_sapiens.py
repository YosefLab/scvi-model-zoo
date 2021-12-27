from typing import Type

from scvimadz.storage import ZenodoStorage
from scvimadz.storage.base import BaseStorage

from .base import BaseReference


class TabulaSapiensReference(BaseReference):
    def __init__(self, data_dir: str):
        # TODO replace our test record id's with our real repo id's
        self._model_store = ZenodoStorage("5805554", data_dir)
        self._data_store = ZenodoStorage("5805615", data_dir)

    @property
    def reference_name(self) -> str:
        return "tabula_sapiens"

    @property
    def model_store(self) -> Type[BaseStorage]:
        return self._model_store

    @property
    def data_store(self) -> Type[BaseStorage]:
        return self._data_store
