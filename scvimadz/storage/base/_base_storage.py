from abc import ABC, abstractmethod
from typing import List


class BaseStorage(ABC):
    @abstractmethod
    def list_files(self) -> List[str]:
        """ Returns all files in this storage """
        pass

    @abstractmethod
    def list_keys(self) -> List[str]:
        """ Returns all keys in this storage """
        pass

    @abstractmethod
    def load_file(self, key: str) -> str:  # return type TBD
        """
        Loads the file with the given id if it exists, else raises an error.

        Parameters
        ----------
        key
            key of the file to load
        """
        pass
