import os

import pytest

from scvimadz.storage import ZenodoStorage

_TEST_ZENODO_RECORD = "5805615"


def test_zenodo_storage_init(save_path):
    store = ZenodoStorage(_TEST_ZENODO_RECORD, save_path)
    assert store._record_id == _TEST_ZENODO_RECORD
    assert store._data_dir == save_path
    assert store._zenodo_record_url_template == "https://zenodo.org/record/{}/files/{}"
    assert store._zenodo_api_base_url == "https://zenodo.org/api/"
    assert store._zenodo_api_records_url == "https://zenodo.org/api/records/"

    store = ZenodoStorage(_TEST_ZENODO_RECORD, save_path)
    assert store._zenodo_api_base_url == "https://zenodo.org/api/"


@pytest.mark.network
def test_list_keys(save_path):
    store = ZenodoStorage(_TEST_ZENODO_RECORD, save_path)
    keys = store.list_keys()
    assert len(keys) == 3
    assert "datasets_metadata.csv" in keys
    assert "hca_dataset_dcfaad7a-70a4-4669-87d2-7bb241673097.h5ad" in keys
    assert "tabula_sapiens_dataset_b4c16899-e458-4cf5-947e-bed59031f156.h5ad" in keys


@pytest.mark.network
def test_download_file(save_path):
    store = ZenodoStorage(_TEST_ZENODO_RECORD, save_path)
    exception_raised = False
    try:
        store.download_file("foo")
    except ValueError:
        exception_raised = True
    assert exception_raised
    file_path = store.download_file("datasets_metadata.csv")
    assert os.path.isfile(file_path)
