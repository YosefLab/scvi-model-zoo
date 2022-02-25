import os
import shutil
from pathlib import Path
from typing import List, Optional

from scvimadz.storage.base import BaseStorage, FileToUpload


class MockStorage(BaseStorage):
    """
    Represents a file system-based storage used in tests to avoid network round trips.

    Parameters
    ----------
    data_type
        Nature of the data stored, one of "datasets" or "models"
    save_path
        Absolute path on the file system where the data lives
    """

    def __init__(self, data_type: str, save_path: str) -> None:
        if data_type not in ["datasets", "models"]:
            raise ValueError(
                'Unrecognized data_type: {}. Must be one of: "datasets", "models".'.format(
                    data_type
                )
            )
        self._save_path = save_path
        dir_name = "datasets" if data_type == "datasets" else "models"
        dir_path = os.path.join(Path(__file__).parent.absolute(), dir_name)

        # move data from the local dir over to the save_path dir since we will be doing file system topology
        # changes (removing/adding files)
        self._data_dir = os.path.join(self._save_path, dir_name)
        os.mkdir(self._data_dir)
        for elem in os.listdir(dir_path):
            src = os.path.join(dir_path, elem)
            dest = os.path.join(self._data_dir, elem)
            shutil.copy(src, dest)

    def list_keys(self) -> List[str]:
        return os.listdir(self._data_dir)

    def download_file(self, key: str) -> str:
        if key not in self.list_keys():
            raise ValueError(f"Key {key} not found.")
        return os.path.join(self._data_dir, key)

    def upload_files(
        self,
        files: List[FileToUpload],
        token: Optional[str],
        ok_to_reversion_datastore: Optional[bool],
    ) -> str:
        # TODO
        pass
