import os
from typing import List, Optional

import requests

from .base import BaseStorage, FileToUpload


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
        self._zenodo_api_depositions_url = (
            f"{self._zenodo_api_base_url}deposit/depositions/"
        )

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

    def upload_files(
        self,
        files: List[FileToUpload],
        token: Optional[str],
        ok_to_reversion_datastore: Optional[bool],
    ) -> str:
        """
        Uploads the given files in a single transaction and bumps the version of the store if all uploads succeed, otherwise discards the new version draft.

        Parameters
        ----------
        TODO
        """
        if self._sandbox is True:
            raise NotImplementedError()
        if not ok_to_reversion_datastore:
            raise ValueError(
                "Uploading new files to a published Zenodo repository requires versioning it."
            )
        # Create a new version of the deposition corresponding to the current record_id
        # Only a single version can be open at a time, so if one already exists this will return that
        params = {"access_token": token}
        response = requests.post(
            f"{self._zenodo_api_depositions_url}{self._record_id}/actions/newversion",
            params=params,
        )
        response.raise_for_status()
        print(response.json()["links"]["latest_draft_html"])  # TODO remove
        draft_deposition_url = response.json()["links"]["latest_draft"]
        draft_reposition_id = None
        try:
            # Get the draft deposition id and the bucket link for the draft deposition
            response = requests.get(draft_deposition_url, params=params)
            response.raise_for_status()
            draft_deposition = response.json()
            draft_reposition_id = draft_deposition["id"]
            bucket_url = draft_deposition["links"]["bucket"]

            def send_data(data, upload_as):
                response = requests.put(
                    f"{bucket_url}/{upload_as}", data=data, params=params
                )
                response.raise_for_status()
                return response

            for file in files:
                # Upload file to the bucket url
                if isinstance(file.data, str):
                    with open(file.data, "rb") as f:
                        response = send_data(f, file.upload_as)
                else:
                    response = send_data(file.data, file.upload_as)
            # If all went well, publish the new version
            response = requests.post(
                f"{self._zenodo_api_depositions_url}{draft_reposition_id}/actions/publish",
                params=params,
            )
            response.raise_for_status()
            self._record_id = str(response.json()["id"])
            print(f"Published new version. New doi: {self._record_id}")
        except Exception as e:
            print(f"Failed to upload. Error: {e}")
            if draft_reposition_id is not None:
                print("Discarding draft.")
                response = requests.post(
                    f"{self._zenodo_api_depositions_url}{draft_reposition_id}/actions/discard",
                    params=params,
                )
                response.raise_for_status()
            raise
