import io
from abc import ABC, abstractmethod
from typing import List, Optional, Union


class FileToUpload:
    """
    Class that represents a file to upload.

    Parameters
    ----------
    data
        Data stream or path to the file to upload
    upload_as
        Name under which to upload the data
    """

    def __init__(self, data: Union[str, io.StringIO], upload_as: str) -> None:
        self._data = data
        self._upload_as = upload_as

    @property
    def data(self) -> Union[str, io.StringIO]:
        return self._data

    @property
    def upload_as(self) -> str:
        return self._upload_as


class BaseStorage(ABC):
    """
    Base class for Storage classes, which represent different kinds of storage backends for the data.

    For example we can have a Zenodo storage backend (remote) or a file system directory backend (local).
    The storage recognizes objects via their keys, which are unique object identifiers. Typically these are
    file names (incl. file extension).
    """

    @abstractmethod
    def list_keys(self) -> List[str]:
        """Returns all keys in this storage."""
        pass

    @abstractmethod
    def download_file(self, key: str) -> str:
        """
        Downloads the file with the given id to the path rooted at the user-provided `data_dir`, else raises an error.

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
    def upload_files(
        self,
        files: List[FileToUpload],
        token: Optional[str],
        ok_to_reversion_datastore: Optional[bool],
    ) -> None:
        """
        Uploads the given files.

        Uploads files in a single transaction and bumps the store version if all uploads succeed, else discards the new version draft.

        Parameters
        ----------
        files
            List of files to upload.
        token
            Access token to use for the upload. If not applicable to this backend, pass None.
        ok_to_reversion_datastore
            Whether it is ok to bump the store version. If not applicable to this backend, pass None.
        """
        pass
