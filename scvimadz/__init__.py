import logging
from rich.console import Console
from rich.logging import RichHandler

from . import reference, storage

# https://github.com/python-poetry/poetry/pull/2366#issuecomment-652418094
# https://github.com/python-poetry/poetry/issues/144#issuecomment-623927302
try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata

package_name = "scvi-model-zoo"
__version__ = importlib_metadata.version(package_name)

logger = logging.getLogger(__name__)
# set the default logging level
logger.setLevel(logging.INFO)

# nice logging outputs
console = Console(force_terminal=True)
if console.is_jupyter:
    console.is_jupyter = False
ch = RichHandler(show_path=False, console=console)
logger.addHandler(ch)

# this prevents double outputs
logger.propagate = False

__all__ = ["reference", "storage"]
