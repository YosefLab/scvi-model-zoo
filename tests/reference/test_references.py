import json
import os

import anndata
import numpy as np

from scvimadz.reference import DatasetMetadata, GenericReference, ModelMetadata
from tests.mock import MockStorage


def test_reference(save_path):
    model_store = MockStorage("models", save_path)
    dataset_store = MockStorage("datasets", save_path)
    generic_ref = GenericReference(
        "hca", model_store=model_store, data_store=dataset_store
    )
    assert generic_ref.reference_name == "hca"
    assert generic_ref.model_store is model_store
    assert generic_ref.data_store is dataset_store
    assert generic_ref._get_reference_prefix() == "hca_"

    exception_raised = False
    try:
        generic_ref._get_object_keys("foo")
    except ValueError:
        exception_raised = True
    assert exception_raised

    models_df = generic_ref.get_models_df()
    assert len(models_df) == 1
    assert models_df.index[0] == "hca_model_80262d08-4a30-4071-a3c6-96274182646d.zip"
    assert models_df.columns.to_list() == [
        "cls_name",
        "hyperparameter_alpha",
        "hyperparameter_beta",
        "batch_corrected",
        "train_dataset",
    ]
    assert models_df["cls_name"].iloc[0] == "scvi.model.SCVI"

    datasets_df = generic_ref.get_datasets_df()
    assert len(datasets_df) == 1
    assert (
        datasets_df.index[0] == "hca_dataset_dcfaad7a-70a4-4669-87d2-7bb241673097.h5ad"
    )
    assert datasets_df.columns.to_list() == [
        "cell_count",
        "gene_count",
        "cite",
        "has_latent_embedding",
        "tissue",
        "is_annotated",
    ]
    assert datasets_df["cell_count"].iloc[0] == 100


def test_reference_load_model(save_path):
    model_store = MockStorage("models", save_path)
    dataset_store = MockStorage("datasets", save_path)
    generic_ref = GenericReference(
        "hca", model_store=model_store, data_store=dataset_store
    )

    model = generic_ref.load_model("hca_model_80262d08-4a30-4071-a3c6-96274182646d.zip")
    assert str(type(model)) == "<class 'scvi.model._scvi.SCVI'>"
    assert model.is_trained
    assert model.adata.n_obs == 100
    assert model.adata.n_vars == 35


def test_reference_save_dataset(save_path):
    model_store = MockStorage("models", save_path)
    dataset_store = MockStorage("datasets", save_path)
    generic_ref = GenericReference(
        "hca", model_store=model_store, data_store=dataset_store
    )

    # Create a dummy fille
    dummydir = os.path.join(save_path, "dummyfiles")
    os.mkdir(dummydir)
    dummyfile_path = os.path.join(dummydir, "dummy_file.h5ad")
    counts = np.random.normal(1, 5, size=(42, 42))
    adata = anndata.AnnData(counts)
    adata.write(dummyfile_path)

    dsm = DatasetMetadata(
        is_cite=True, has_latent_embedding=True, tissue="Misc", is_annotated=False
    )
    dataset_id = generic_ref.save_dataset(dummyfile_path, None, True, dsm)

    datasets_df = generic_ref.get_datasets_df()
    assert len(datasets_df) == 2
    existing_dataset_id = "hca_dataset_dcfaad7a-70a4-4669-87d2-7bb241673097.h5ad"
    assert datasets_df.columns.to_list() == [
        "cell_count",
        "gene_count",
        "cite",
        "has_latent_embedding",
        "tissue",
        "is_annotated",
    ]

    assert datasets_df["cell_count"].loc[existing_dataset_id] == 100
    assert datasets_df["cell_count"].loc[dataset_id] == 42

    assert bool(datasets_df["cite"].loc[existing_dataset_id]) is False
    assert bool(datasets_df["cite"].loc[dataset_id]) is True

    assert datasets_df["gene_count"].loc[dataset_id] == 42.0
    assert bool(datasets_df["has_latent_embedding"].loc[dataset_id]) is True
    assert datasets_df["tissue"].loc[dataset_id] == "Misc"
    assert bool(datasets_df["is_annotated"].loc[dataset_id]) is False


def test_reference_save_model(save_path):
    model_store = MockStorage("models", save_path)
    dataset_store = MockStorage("datasets", save_path)
    generic_ref = GenericReference(
        "hca", model_store=model_store, data_store=dataset_store
    )

    # Create a dummy fille
    dummydir = os.path.join(save_path, "dummyfiles")
    os.mkdir(dummydir)
    dummyfile_path = os.path.join(dummydir, "dummy_file")
    with open(dummyfile_path, "w") as f:
        f.write("hello world")

    init_params_dict = {
        "kwargs": {"model_kwargs": {}},
        "non_kwargs": {
            "n_hidden": 128,
            "n_latent": 10,
            "n_layers": 1,
            "dropout_rate": 0.1,
            "dispersion": "gene",
            "gene_likelihood": "zinb",
            "latent_distribution": "normal",
        },
    }
    mm = ModelMetadata(
        cls_name="scvi.model.SCVI",
        train_dataset="tabula_sapiens_dataset_168d13ea-308d-4069-9345-e3041d738e6c.h5ad",
        n_hidden=128,
        n_layers=1,
        n_latent=10,
        use_observed_lib_size=False,
        is_cite=True,
        init_params=json.dumps(init_params_dict),
    )
    model_id = generic_ref.save_model(dummyfile_path, None, True, mm)

    models_df = generic_ref.get_models_df()
    assert len(models_df) == 2
    existing_model_id = "hca_model_80262d08-4a30-4071-a3c6-96274182646d.zip"
    assert models_df.columns.to_list() == [
        "cls_name",
        "hyperparameter_alpha",
        "hyperparameter_beta",
        "batch_corrected",
        "train_dataset",
        "n_hidden",
        "n_layers",
        "n_latent",
        "use_observed_lib_size",
        "is_cite",
        "init_params",
    ]

    assert models_df["cls_name"].loc[existing_model_id] == "scvi.model.SCVI"
    assert models_df["cls_name"].loc[model_id] == "scvi.model.SCVI"

    assert (
        models_df["train_dataset"].loc[existing_model_id]
        == "hca_dataset_dcfaad7a-70a4-4669-87d2-7bb241673097.h5ad"
    )
    assert (
        models_df["train_dataset"].loc[model_id]
        == "tabula_sapiens_dataset_168d13ea-308d-4069-9345-e3041d738e6c.h5ad"
    )

    assert models_df["n_hidden"].loc[model_id] == 128.0
    assert models_df["n_layers"].loc[model_id] == 1.0
    assert models_df["n_latent"].loc[model_id] == 10.0
    assert bool(models_df["use_observed_lib_size"].loc[model_id]) is False
    assert bool(models_df["is_cite"].loc[model_id]) is True
    assert models_df["init_params"].loc[model_id] == json.dumps(init_params_dict)
