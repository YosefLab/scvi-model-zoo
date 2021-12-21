import os
from typing import List

import requests

from .base import BaseStorage


class ZenodoStorage(BaseStorage):
    def __init__(self, record_id: str, data_dir: str, sandbox: bool = False):
        self._record_id = record_id
        self._data_dir = data_dir
        if not os.path.isdir(data_dir):
            raise ValueError(f"Error: {data_dir} is not a valid directory")
        # zenodo urls
        self._zenodo_base_url = (
            "https://zenodo.org/" if not sandbox else "https://sandbox.zenodo.org/"
        )
        self._zenodo_record_url_template = (
            f"{self._zenodo_base_url}record/{{}}/files/{{}}"
        )
        self._zenodo_api_base_url = f"{self._zenodo_base_url}api/"
        self._zenodo_api_records_url = f"{self._zenodo_api_base_url}records/"

    def list_keys(self) -> List[str]:
        """Returns all keys in this storage"""
        response = requests.get(self._zenodo_api_records_url + self._record_id)
        # for the status codes Zenodo uses, see https://developers.zenodo.org/#responses
        response.raise_for_status()
        # if the call above didn't throw the response was "ok" (code < 400)
        response_json = response.json()
        keys = [elem["key"] for elem in response_json["files"]]
        return keys

    def download_file(self, key: str) -> str:
        """
        Downloads the file with the given id to the path rooted at the user-provided `data_dir`,
        else raises an error. Returns the full path to the downloaded file.

        Parameters
        ----------
        key
            key of the file to download
        """
        if key not in self.list_keys():
            raise ValueError(f"Key {key} not found.")
        file_url = self._zenodo_record_url_template.format(self._record_id, key)
        response = requests.get(file_url)
        response.raise_for_status()
        # save response to file and return its full path
        file_path = os.path.join(self._data_dir, key)
        with open(file_path, "wb") as f:
            f.write(response.content)
        return file_path
