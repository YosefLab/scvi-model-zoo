from typing import List

from storage.base import BaseStorage


class ZenodoStorage(BaseStorage):
    def __init__(self, url: str):
        self._url = url

    def list_model_keys(self) -> List[str]:
        """ Returns the id's of all models stored """
        raise NotImplementedError

    def list_dataset_keys(self) -> List[str]:
        """ Returns the id's of all datasets stored """
        raise NotImplementedError

    def load_model(self, key: str) -> str:
        """
        Loads the model with the given id if it exists, else raises an error.

        Parameters
        ----------
        model_id
            id of the model to load
        """
        pass
