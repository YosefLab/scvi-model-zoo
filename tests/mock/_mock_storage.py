import os
import shutil
from pathlib import Path
from typing import List

from scvimadz.storage.base import BaseStorage


class MockStorage(BaseStorage):
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
