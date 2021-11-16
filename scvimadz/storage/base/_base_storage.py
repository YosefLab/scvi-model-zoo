from abc import ABC, abstractmethod
from typing import List


class BaseStorage(ABC):
    @abstractmethod
    def list_keys(self) -> List[str]:
        """ Returns all keys in this storage """
        pass

    @abstractmethod
    def download_file(self, key: str) -> str:
        """
        Downloads the file with the given id if it exists to a temp location, else raises an error.
        Returns the contents of the downloaded file as text.

        Parameters
        ----------
        key
            key of the file to download
        """
        pass
