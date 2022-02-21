import os
from typing import List, Optional

import requests

from .base import BaseStorage


class ZenodoStorage(BaseStorage):
    def __init__(self, record_id: str, data_dir: str, sandbox: bool = False):
        self._record_id = record_id
        self._data_dir = data_dir
        self._sandbox = sandbox
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
        self._zenodo_api_depositions_url = f"{self._zenodo_api_base_url}depositions/"

    def list_keys(self) -> List[str]:
        """Returns all keys in this storage."""
        response = requests.get(self._zenodo_api_records_url + self._record_id)
        # for the status codes Zenodo uses, see https://developers.zenodo.org/#responses
        response.raise_for_status()
        # if the call above didn't throw the response was "ok" (code < 400)
        response_json = response.json()
        keys = [elem["key"] for elem in response_json["files"]]
        return keys

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

    def upload_file(self, path: str, filename: str, token: Optional[str]) -> str:
        """
        Uploads the file at the given path.

        Parameters
        ----------
        path
            full path to the file to upload
        """
        if self._sandbox:
            raise NotImplementedError()
        # Query all depositions using the generic depositions url
        params = {"access_token": token}
        response = requests.get(self._zenodo_api_depositions_url, params=params)
        response.raise_for_status()
        # Grab the deposition corresponding to the self's record_id
        response_json = response.json()
        depositions = [
            elem for elem in response_json if str(elem["id"]) == self._record_id
        ]
        if len(depositions) > 1:
            raise ValueError(
                f"More than one deposition found for the record id {self._record_id}"
            )
        deposition = depositions[0]
        # Get the bucket link for the deposition
        bucket_url = deposition["links"]["bucket"]
        # Upload file to the bucket link
        with open(path, "rb") as f:
            response = requests.put(f"{bucket_url}{filename}", data=f, params=params)
        # TODO publish if needed?
        # >>> r = requests.post('https://zenodo.org/api/deposit/depositions/%s/actions/publish' % deposition_id, params={'access_token': ACCESS_TOKEN} )
        pass
