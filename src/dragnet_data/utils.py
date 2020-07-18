import datetime
import importlib
import json
import logging
import pathlib
import random
import shutil
import uuid
from typing import Any, Dict, List, Optional, Union

import toml

LOGGER = logging.getLogger(__name__)


def get_random_sample(items: List[Any], n: int) -> List[Any]:
    """
    Thin wrapper around ``random.sample`` that takes the min of ``n`` and ``len(items)``
    when sampling, so as to avoid a ``ValueError``.
    """
    return random.sample(items, min(n, len(items)))


def get_pkg_root() -> Optional[pathlib.Path]:
    pkg = importlib.util.find_spec("dragnet_data")
    if pkg:
        return pathlib.Path(pkg.origin).parent
    else:
        return None


def generate_page_uuid(url: str) -> str:
    return str(uuid.uuid3(uuid.NAMESPACE_URL, url))


def load_json_data(fpath: Union[str, pathlib.Path]) -> Dict[str, str]:
    fpath = to_path(fpath).resolve()
    with fpath.open(mode="rt") as f:
        data = json.load(f)
    LOGGER.info("loaded json data from %s", fpath)
    return data


def save_json_data(data: List[Dict], fpath: Union[str, pathlib.Path]):
    fpath = to_path(fpath).resolve()
    with fpath.open(mode="wt") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, cls=ExtendedJSONEncoder)
    LOGGER.info("saved json data to %s", fpath)


def load_text_data(fpath: Union[str, pathlib.Path]) -> str:
    fpath = to_path(fpath).resolve()
    with fpath.open(mode="rt") as f:
        data = f.read()
    LOGGER.info("loaded text data from %s", fpath)
    return data


def save_text_data(data: str, fpath: Union[str, pathlib.Path]):
    fpath = to_path(fpath).resolve()
    with fpath.open(mode="wt") as f:
        f.write(data)
    LOGGER.info("saved text data to %s", fpath)


def load_toml_data(fpath: Union[str, pathlib.Path]) -> Dict[str, Any]:
    fpath = to_path(fpath).resolve()
    with fpath.open(mode="rt") as f:
        data = toml.load(f)
    LOGGER.info("loaded toml data from %s", fpath)
    return data


def save_toml_data(data: Dict[str, Any], fpath: Union[str, pathlib.Path]):
    fpath = to_path(fpath).resolve()
    with fpath.open(mode="wt") as f:
        toml.dump(data, f)
    LOGGER.info("saved toml data to %s", fpath)


def to_path(path: Union[str, pathlib.Path]) -> pathlib.Path:
    """Coerce ``path`` to a ``pathlib.Path``."""
    if isinstance(path, str):
        return pathlib.Path(path)
    elif isinstance(path, pathlib.Path):
        return path
    else:
        raise TypeError(
            "`path` type invalid; must be {}, not {}".format({str, pathlib.Path}, type(path))
        )


def make_gztar_archive_from_dir(dirpath: pathlib.Path) -> pathlib.Path:
    """
    Make a gzipped tar archive from all contents of the directory at ``dirpath``,
    and save to a file of the same base name with the parent directory.
    """
    fpath = pathlib.Path(shutil.make_archive(dirpath, root_dir=dirpath, format="gztar"))
    LOGGER.info("made gztar archive at %s", fpath)
    return fpath


def unpack_gztar_archive_to_dir(fpath: pathlib.Path):
    """
    Unpack contents of gzipped tar archive file at ``fpath`` into a subdirectory of the
    same base name within the same directory.
    """
    extract_dir = fpath.parent.joinpath(fpath.name[:-len("".join(fpath.suffixes))])
    shutil.unpack_archive(fpath, extract_dir, format="gztar")
    LOGGER.info("unpacked gztar archive into %s", extract_dir)


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
