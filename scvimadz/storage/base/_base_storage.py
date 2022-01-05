from abc import ABC, abstractmethod
from typing import List


class BaseStorage(ABC):
    """
    Base class for Storage classes. These classes represent different kinds of storage backends
    for the models and datasets. For example we can have a Zenodo storage backend (remote) or a
    file system directory backend (local). The storage recognizes objects via their keys, which
    are unique object identifiers. Typically these are file names (incl. file extension).

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
