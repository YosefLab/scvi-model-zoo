from scvimadz.reference import GenericReference
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
    assert datasets_df.columns.to_list() == ["cell_count", "cite"]
    assert datasets_df["cell_count"].iloc[0] == 20000


def test_reference_load_model(save_path):
    model_store = MockStorage("models", save_path)
    dataset_store = MockStorage("datasets", save_path)
    generic_ref = GenericReference(
        "hca", model_store=model_store, data_store=dataset_store
    )

    model = generic_ref.load_model("hca_model_80262d08-4a30-4071-a3c6-96274182646d.zip")
    assert str(type(model)) == "<class 'scvi.model._scvi.SCVI'>"
    assert model.is_trained
    assert model.adata.n_obs == 18641
    assert model.adata.n_vars == 1200
