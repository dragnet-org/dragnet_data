import argparse
import logging
import pathlib
import sys

import dragnet_data

logging.basicConfig(level=logging.INFO)

PKG_ROOT = dragnet_data.utils.get_pkg_root()


def main():
    parser = argparse.ArgumentParser(
        description="Make gztar archives of existing HTML and metadata files.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    add_arguments(parser)
    args = parser.parse_args()
    args.data_dirpath = args.data_dirpath.resolve()
    for dirname in ("html", "meta"):
        dirpath = args.data_dirpath.joinpath(dirname)
        dragnet_data.utils.make_gztar_archive_from_dir(dirpath)


def add_arguments(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--data_dirpath", type=pathlib.Path, default=PKG_ROOT.parents[1].joinpath("data"),
        help="path to directory on disk under which HTML and meta data are stored "
        "at `data_dirpath/html` and `data_dirpath/meta`, respectively, and to which "
        "corresponding gztar archives are to be stored",
    )


if __name__ == "__main__":
    sys.exit(main())
