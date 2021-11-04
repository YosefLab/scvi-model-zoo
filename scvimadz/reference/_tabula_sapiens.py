# import importlib
from reference.base import BaseReference
from storage import ZenodoStorage


class TabulaSapiensReference(BaseReference):
    def __init__(self):
        name = "tabula_sapiens"
        model_store = ZenodoStorage("test_model_url")
        dataset_store = ZenodoStorage("test_dataset_url")
        super().__init__(name, model_store, dataset_store)
