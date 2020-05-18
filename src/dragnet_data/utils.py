import datetime
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
        json.dump(data, f, indent=2, ensure_ascii=False, cls=ExtendedJSONEncoder)
    LOGGER.info("saved json data to %s", fpath)


def load_text_data(fpath: Union[str, pathlib.Path]) -> str:
    fpath = _to_path(fpath).resolve()
    with fpath.open(mode="rt") as f:
        data = f.read()
    LOGGER.info("loaded text data from %s", fpath)
    return data


def save_text_data(data: str, fpath: Union[str, pathlib.Path]):
    fpath = _to_path(fpath).resolve()
    with fpath.open(mode="wt") as f:
        f.write(data)
    LOGGER.info("saved text data to %s", fpath)


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


class ExtendedJSONEncoder(json.JSONEncoder):
    """
    Sub-class of :class:`json.JSONEncoder`, used to write JSON data to disk in
    :func:`write_json()` while handling a broader range of Python objects.
    - :class:`datetime.datetime` => ISO-formatted string
    - :class:`datetime.date` => ISO-formatted string
    """

    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        else:
            return super().default(obj)
