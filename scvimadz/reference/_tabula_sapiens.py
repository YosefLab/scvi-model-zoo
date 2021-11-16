from storage import ZenodoStorage

from .base import BaseReference


class TabulaSapiensReference(BaseReference):
    def __init__(self):
        name = "tabula_sapiens"
        model_store = ZenodoStorage("test_model_record_id")
        dataset_store = ZenodoStorage("test_dataset_record_id")
        super().__init__(name, model_store, dataset_store)
