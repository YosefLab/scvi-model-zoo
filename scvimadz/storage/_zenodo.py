from typing import List

from storage.base import BaseStorage


class ZenodoStorage(BaseStorage):
    def __init__(self, url: str):
        self._url = url

    def list_files(self) -> List[str]:
        """ Returns all files in this storage """
        raise NotImplementedError

    def list_keys(self) -> List[str]:
        """ Returns all keys in this storage """
        raise NotImplementedError

    def load_file(self, key: str) -> str:
        """
        Loads the file with the given id if it exists, else raises an error.

        Parameters
        ----------
        key
            key of the file to load
        """
        raise NotImplementedError
