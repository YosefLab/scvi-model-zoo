import shutil

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--network-tests",
        action="store_true",
        default=False,
        help="Run tests that involve network operations. This increases test time.",
    )


def pytest_collection_modifyitems(config, items):
    run_network = config.getoption("--network-tests")
    skip_network = pytest.mark.skip(reason="need --network-tests option to run")
    for item in items:
        # All tests marked with `pytest.mark.network` get skipped unless
        # `--network-tests` passed
        if not run_network and ("network" in item.keywords):
            item.add_marker(skip_network)


@pytest.fixture(scope="function")
def save_path(tmpdir):
    data_dir = tmpdir.mkdir("temp_data")
    yield str(data_dir) + "/"
    shutil.rmtree(str(tmpdir))
