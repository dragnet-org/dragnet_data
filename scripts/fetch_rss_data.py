import argparse
import logging
import pathlib
import random
import shutil
import sys
from typing import Any, Dict, Optional, Tuple

import dragnet_data

logging.basicConfig(level=logging.INFO)

PKG_ROOT = dragnet_data.utils.get_pkg_root()


def main():
    parser = argparse.ArgumentParser(
        description="Fetch a set of recent pages with basic metadata from a collection "
        "of RSS feeds, then save results to disk for web scraping and text extraction.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    add_arguments(parser)
    args = parser.parse_args()
    args.feeds_fpath = args.feeds_fpath.resolve()
    args.pages_fpath = args.pages_fpath.resolve()
    rss_pages = []
    feeds = dragnet_data.utils.load_toml_data(args.feeds_fpath)["feeds"]
    for feed in feeds:
        entries = dragnet_data.rss.get_entries_from_feed(feed, maxn=args.maxn_entries_per_feed)
        rss_pages.extend(
            dragnet_data.rss.get_data_from_entry(entry) for entry in entries
        )
    # just in case: remove any rss pages without urls, since we need them for scraping
    rss_pages = [rss_page for rss_page in rss_pages if rss_page.get("url")]
    logging.info("got data for %s pages from RSS feeds", len(rss_pages))
    if args.pages_fpath.exists() and args.force is False:
        logging.warning(
            "%s already exists and `force` is False; pages will not be saved:\n%s\n...",
            args.pages_fpath, rss_pages[:3],
        )
    else:
        dragnet_data.utils.save_toml_data({"pages": rss_pages}, args.pages_fpath)


def add_arguments(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--feeds_fpath",
        type=pathlib.Path,
        default=PKG_ROOT.parents[1].joinpath("data", "rss_feeds.toml"),
        help="path to file on disk where curated collection of RSS feeds is stored",
    )
    parser.add_argument(
        "--pages_fpath",
        type=pathlib.Path,
        default=PKG_ROOT.parents[1].joinpath("data", "rss_pages.toml"),
        help="path to file on disk where pages fetched from RSS feeds are to be stored",
    )
    parser.add_argument(
        "--maxn_entries_per_feed", type=int, default=25,
        help="maximum number of entries (pages) to include per feed",
    )
    parser.add_argument(
        "--force", action="store_true", default=False,
        help="if specified, save data to `pages_fpath` even if a file already exists "
        "in that location; otherwise, just log a preview to the console"
    )


if __name__ == "__main__":
    sys.exit(main())
