import argparse
import logging
import pathlib
import sys

import dragnet_data

logging.basicConfig(level=logging.INFO)

def main():
    parser = argparse.ArgumentParser(
        description="Script to fetch HTML documents and some metadata for a set of pages "
        "published to a curated collection of RSS feeds -- and, when possible, "
        "to extract a first pass on the page's main body text.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    add_arguments(parser)
    args = parser.parse_args()
    # fetch base data from rss feeds
    rss_pages = []
    feeds = dragnet_data.utils.load_json_data(args.feeds_fpath)
    for feed in feeds:
        entries = dragnet_data.rss.get_entries_from_feed(feed, maxn=args.maxn_entries_per_feed)
        rss_pages.extend(
            dragnet_data.rss.get_data_from_entry(entry) for entry in entries
        )
    logging.info("got data for %s pages from RSS feeds", len(rss_pages))
    dragnet_data.utils.save_json_data(rss_pages, args.pages_fpath)


def add_arguments(parser):
    parser.add_argument(
        "--feeds_fpath", type=pathlib.Path, default=pathlib.Path("./data/rss_feeds.json"),
    )
    parser.add_argument(
        "--pages_fpath", type=pathlib.Path, default=pathlib.Path("./data/rss_pages.json"),
    )
    parser.add_argument(
        "--maxn_entries_per_feed", type=int, default=25,
    )


if __name__ == "__main__":
    sys.exit(main())
