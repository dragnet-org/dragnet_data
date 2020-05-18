import io
import json
import logging
import pathlib
import uuid
from typing import Dict, List, Union

LOGGER = logging.getLogger(__name__)


def generate_page_uuid(url: str) -> str:
    return str(uuid.uuid3(uuid.NAMESPACE_URL, url))


def load_json_data(fpath: Union[str, pathlib.Path]) -> Dict[str, str]:
    fpath = _to_path(fpath).resolve()
    with fpath.open(mode="rt") as f:
        data = json.load(f)
    LOGGER.info("loaded json data from %s", fpath)
    return data


def save_json_data(data: List[Dict], fpath: Union[str, pathlib.Path]):
    fpath = _to_path(fpath).resolve()
    with fpath.open(mode="wt") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    LOGGER.info("saved json data to %s", fpath)


def _to_path(path: Union[str, pathlib.Path]) -> pathlib.Path:
    """Coerce ``path`` to a ``pathlib.Path``."""
    if isinstance(path, str):
        return pathlib.Path(path)
    elif isinstance(path, pathlib.Path):
        return path
    else:
        raise TypeError(
            "`path` type invalid; must be {}, not {}".format({str, pathlib.Path}, type(path))
        )
