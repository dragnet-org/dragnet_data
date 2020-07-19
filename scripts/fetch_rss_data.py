import argparse
import logging
import pathlib
import sys
from typing import Dict, List, Optional

import dragnet_data as dd

logging.basicConfig(level=logging.INFO)

PKG_ROOT = dd.utils.get_pkg_root()


def main():
    args = add_and_parse_args()
    pages = []
    feeds = filter_feeds(dd.utils.load_rss_feeds(), args.only_feeds)
    for feed in feeds:
        entries = dd.rss.get_entries_from_feed(feed, maxn=args.maxn_pages_per_feed)
        pages.extend(dd.rss.get_data_from_entry(entry) for entry in entries)
    # just in case: remove any rss pages without urls, since we need them for scraping
    pages = [page for page in pages if page.get("url")]
    if args.maxn_pages:
        pages = dd.utils.get_random_sample(pages, args.maxn_pages)
    logging.info("got data for %s pages from RSS feeds", len(pages))
    if args.pages_fpath.exists() and args.force is False:
        logging.warning(
            "%s already exists and `force` is False; pages will not be saved:\n%s\n...",
            args.pages_fpath, pages[:3],
        )
    else:
        dd.utils.save_toml_data({"pages": pages}, args.pages_fpath)


def add_and_parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch a set of recent pages with basic metadata from a collection "
        "of RSS feeds, then save results to disk for web scraping and text extraction.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--pages_fpath",
        type=pathlib.Path,
        default=PKG_ROOT.parents[1].joinpath("data", "rss_pages.toml"),
        help="path to file on disk where pages fetched from RSS feeds are to be stored",
    )
    parser.add_argument(
        "--only_feeds",
        type=str,
        nargs="+",
        help="name(s) of feed(s) in `rss_feeds.toml` for which pages will be fetched, only",
    )
    parser.add_argument(
        "--maxn_pages", type=int,
        help="maximum number of pages to fetch from all feeds, in total; "
        "if more pages were fetched than specified here, a random sample is selected",
    )
    parser.add_argument(
        "--maxn_pages_per_feed", type=int, default=25,
        help="maximum number of pages to fetch per feed",
    )
    parser.add_argument(
        "--force", action="store_true", default=False,
        help="if specified, save data to `pages_fpath` even if a file already exists "
        "in that location; otherwise, just log a preview to the console"
    )
    args = parser.parse_args()
    args.feeds_fpath = args.feeds_fpath.resolve()
    args.pages_fpath = args.pages_fpath.resolve()
    return args


def filter_feeds(
    feeds: List[Dict[str, str]],
    only_feeds: Optional[List[str]],
) -> List[Dict[str, str]]:
    """
    Filter items in ``feeds`` to just those specified in ``only_feeds``, if any,
    taking care to ensure that all items in ``only_feeds`` are also in ``feeds``.
    """
    if not only_feeds:
        return feeds
    else:
        all_feed_names = set(feed["name"] for feed in feeds)
        only_feed_names = set(only_feeds)
        if not only_feed_names.issubset(all_feed_names):
            missing_feeds = sorted(only_feed_names.difference(all_feed_names))
            raise ValueError(
                "not all feeds specified in `only` are found in `feeds_fpath`; "
                f"specifically: {missing_feeds}"
            )
        else:
            return [feed for feed in feeds if feed["name"] in only_feed_names]


if __name__ == "__main__":
    sys.exit(main())
