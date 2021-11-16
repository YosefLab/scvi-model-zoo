import os
from typing import List

import requests
from base import BaseStorage

_ZENODO_API_BASE_URL = "https://zenodo.org/api/"
_ZENODO_API_RECORDS_URL = _ZENODO_API_BASE_URL + "records/"
_ZENODO_RECORD_URL = "https://zenodo.org/record/{}/files/{}"


class ZenodoStorage(BaseStorage):
    def __init__(self, record_id: str, data_dir: str):
        self._record_id = record_id
        self._data_dir = data_dir

    def list_keys(self) -> List[str]:
        """ Returns all keys in this storage """
        response = requests.get(_ZENODO_API_RECORDS_URL + self._record_id)
        # for the status codes Zenodo uses, see https://developers.zenodo.org/#responses
        response.raise_for_status()
        # if the call above didn't throw the response was "ok" (code < 400)
        response_json = response.json()
        keys = [elem["key"] for elem in response_json["files"]]
        return keys

    def download_file(self, key: str) -> str:
        """
        Downloads the file with the given id if it exists to a temp location, else raises an error.
        Returns the contents of the downloaded file as text.

        Parameters
        ----------
        key
            key of the file to download
        """
        if key not in self.list_keys():
            raise ValueError(f"Key {key} not found.")
        file_url = _ZENODO_RECORD_URL.format(self._record_id, key)
        response = requests.head(file_url)
        response.raise_for_status()
        # if "Content-Length" not in response.headers or int(response.headers["Content-Length"]) > 500 * 10**9:
        #     raise NotImplementedError
        response = requests.get(file_url)
        with open(os.path.join(self._data_dir, key), "wb") as f:
            f.write(response)
        return response.text
