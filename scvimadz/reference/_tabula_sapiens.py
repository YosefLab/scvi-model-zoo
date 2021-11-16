from typing import Type

from storage import ZenodoStorage
from storage.base import BaseStorage

from .base import BaseReference


class TabulaSapiensReference(BaseReference):
    def __init__(self, data_dir: str):
        # TODO replace 961966 (our sandbox record id) with our real repo id's
        self._model_store = ZenodoStorage("961966", data_dir)
        self._data_store = ZenodoStorage("961966", data_dir)
        super().__init__()

    @property
    def reference_name(self) -> str:
        return "tabula_sapiens"

    @property
    def model_store(self) -> Type[BaseStorage]:
        return self._model_store

    @property
    def data_store(self) -> Type[BaseStorage]:
        return self._data_store
