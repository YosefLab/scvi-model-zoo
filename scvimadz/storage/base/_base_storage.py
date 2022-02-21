from abc import ABC, abstractmethod
from typing import List, Optional


class BaseStorage(ABC):
    """
    Base class for Storage classes, which represent different kinds of storage backends for the data.

    For example we can have a Zenodo storage backend (remote) or a file system directory backend (local).
    The storage recognizes objects via their keys, which are unique object identifiers. Typically these are
    file names (incl. file extension).

    Parameters
    ----------
    reference_name
        Name of the reference
    model_store
        BaseStorage for the model store
    data_store
        BaseStorage for the data store
    """

    @abstractmethod
    def list_keys(self) -> List[str]:
        """Returns all keys in this storage."""
        pass

    @abstractmethod
    def download_file(self, key: str) -> str:
        """
        Downloads the file with the given key if it exists to a temp location, else raises an error.

        Parameters
        ----------
        key
            key of the file to download

        Returns
        -------
        The full path to the downloaded file.
        """
        pass

    @abstractmethod
    def upload_file(self, path: str, filename: str, token: Optional[str]) -> str:
        """
        Uploads the file at the given path.

        Parameters
        ----------
        path
            full path to the file to upload
        """
        pass
