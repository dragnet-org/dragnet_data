import argparse
import logging
import pathlib
import sys
from typing import Dict, Set

import dragnet_data as dd

logging.basicConfig(level=logging.INFO)

PKG_ROOT = dd.utils.get_pkg_root()
DIRNAMES = ("html", "meta")
_DIRNAME_GLOBPATS = {"html": "*.html", "meta": "*.toml"}


def main():
    args = add_and_parse_args()
    get_check_and_save_page_uuids(args.data_dirpath)
    for dirname in DIRNAMES:
        dirpath = args.data_dirpath.joinpath(dirname)
        dd.utils.make_gztar_archive_from_dir(dirpath)


def add_and_parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Make gztar archives of existing HTML and metadata files.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--data_dirpath",
        type=pathlib.Path,
        default=PKG_ROOT.parents[1].joinpath("data"),
        help="path to directory on disk under which HTML and meta data are stored "
        "at `data_dirpath/html` and `data_dirpath/meta`, respectively, and to which "
        "corresponding gztar archives are to be stored",
    )
    args = parser.parse_args()
    args.data_dirpath = args.data_dirpath.resolve()
    return args


def get_check_and_save_page_uuids(data_dirpath: pathlib.Path):
    page_uuids: Dict[str, Set[str]] = {}
    for dirname in DIRNAMES:
        dirpath = data_dirpath.joinpath(dirname)
        page_uuids[dirname] = {
            path.stem for path in dirpath.glob(_DIRNAME_GLOBPATS[dirname])
        }
    # check #1: make sure all pages are in both /html and /meta
    unpaired_uuids = sorted(page_uuids["html"].symmetric_difference(page_uuids["meta"]))
    if unpaired_uuids:
        raise UserWarning(
            "every page in '/html' must have a corresponding page in '/meta', "
            f"but these pages do not: {unpaired_uuids}"
        )

    all_page_uuids = page_uuids["html"]
    page_uuids_fpath = data_dirpath.joinpath("page_uuids.txt")
    # check #2: make sure all existing pages are also in the local set of pages
    if page_uuids_fpath.exists():
        existing_page_uuids = set(dd.utils.load_text_data(page_uuids_fpath, lines=True))
        missing_uuids = sorted(existing_page_uuids.difference(all_page_uuids))
        if missing_uuids:
            raise UserWarning(
                f"every page in existing {page_uuids_fpath.name} should also be present "
                f"in {data_dirpath.joinpath('html')}, but these pages are not: "
                f"{missing_uuids}"
            )

    dd.utils.save_text_data("\n".join(sorted(all_page_uuids)), page_uuids_fpath)


if __name__ == "__main__":
    sys.exit(main())
