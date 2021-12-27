import os
import shutil
from pathlib import Path

# from posixpath import dirname
from typing import List, Optional

from scvimadz.storage.base import BaseStorage


class MockStorage(BaseStorage):
    def __init__(self, data_type: str, save_path: Optional[str] = None) -> None:
        if data_type not in ["datasets", "models"]:
            raise ValueError(
                'Unrecognized data_type: {}. Must be one of: "datasets", "models".'.format(
                    data_type
                )
            )
        dir_name = "datasets" if data_type == "datasets" else "models"
        self._data_dir = os.path.join(Path(__file__).parent.absolute(), dir_name)
        self._save_path = save_path

        # for datasets, we store them in zip format to save space on Git. Unzip those here
        if data_type == "datasets":
            for elem in os.listdir(self._data_dir):
                if elem.endswith(".zip"):
                    elem_path = os.path.join(self._data_dir, elem)
                    shutil.unpack_archive(elem_path)
                    os.remove(elem_path)

    def list_keys(self) -> List[str]:
        return os.listdir(self._data_dir)

    def download_file(self, key: str) -> str:
        if key not in self.list_keys():
            raise ValueError(f"Key {key} not found.")
        file_path = os.path.join(self._data_dir, key)
        if self._save_path:
            dest = os.path.join(self._save_path, file_path.split("/")[-1])
            shutil.copy(file_path, dest)
            return dest
        return file_path
