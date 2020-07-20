import argparse
import logging
import pathlib
import random
import sys
from typing import Any, Dict, Optional, Tuple, Union

import httpx

import dragnet_data as dd

logging.basicConfig(level=logging.INFO)

PKG_ROOT = dd.utils.get_pkg_root()
USER_AGENTS = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:75.0) Gecko/20100101 Firefox/75.0",
)
_META_FIELDS = ("id", "url", "dt_published", "title", "text")


def main():
    args = add_and_parse_args()
    # make html and meta directories if they don't already exist
    for dirname in dd.utils.DATA_DIRNAMES:
        args.data_dirpath.joinpath(dirname).mkdir(parents=True, exist_ok=True)
    # load and shuffle rss pages (to avoid slamming sites' servers)
    rss_pages = dd.utils.load_rss_pages(args.pages_fpath)
    rss_pages = random.sample(rss_pages, k=len(rss_pages))
    # fetch html and re-extract base metadata, plus text if available
    n_pages = len(rss_pages)
    with httpx.Client(timeout=args.http_timeout) as client:
        for idx, rss_page in enumerate(rss_pages):
            logging.info("getting data for page %s / %s", idx, n_pages)
            headers = {"user-agent": random.choice(USER_AGENTS)}
            data = get_page_html_and_meta_data(
                rss_page["url"], client=client, headers=headers,
            )
            if data is None:
                continue
            else:
                html, meta = data
                html_fpath = args.data_dirpath.joinpath("html", f"{meta['id']}.html")
                meta_fpath = args.data_dirpath.joinpath("meta", f"{meta['id']}.toml")
                save_page_data_or_log(html, html_fpath, args.force)
                save_page_data_or_log(meta, meta_fpath, args.force)


def add_and_parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch HTML documents and some metadata for a set of pages "
        "published to a curated collection of RSS feeds -- and, when possible, "
        "extract a first pass on the page's main body text.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--pages_fpath",
        type=pathlib.Path,
        default=PKG_ROOT.parents[1].joinpath("data", "rss_pages.toml"),
        help="path to file on disk where pages fetched from RSS feeds are stored",
    )
    parser.add_argument(
        "--data_dirpath",
        type=pathlib.Path,
        default=PKG_ROOT.parents[1].joinpath("data", "TODO"),
        help="path to directory on disk under which HTML and meta data are to be stored "
        "at `data_dirpath/html` and `data_dirpath/meta`, respectively",
    )
    parser.add_argument(
        "--http_timeout", type=float, default=5.0,
        help="number of seconds to wait on all network operations before raising a timeout error",
    )
    parser.add_argument(
        "--force", action="store_true", default=False,
        help="if specified, save HTML and meta data under `data_dirpath` even if files "
        "already exist in those locations; otherwise, just log a preview to the console. "
    )
    args = parser.parse_args()
    args.pages_fpath = args.pages_fpath.resolve()
    args.data_dirpath = args.data_dirpath.resolve()
    return args


def get_page_html_and_meta_data(
    url: str,
    client: Optional[httpx.Client] = None,
    **kwargs,
) -> Optional[Tuple[str, Dict[str, Any]]]:
    try:
        html, response = dd.html.get_html(url, client=client, **kwargs)
    except httpx.HTTPError:
        logging.exception("unable to get HTML for %s", url)
        return
    try:
        meta = dd.html.get_data_from_html(html)
    except Exception:
        logging.error("unable to extract data from HTML for %s", url)
        return
    if "url" not in meta:
        meta["url"] = str(response.url)
    meta["id"] = dd.utils.generate_page_uuid(meta["url"])
    # HACK: let's add empty placeholders for text and title, if not already present
    for field in ("text", "title"):
        _ = meta.setdefault(field, "")
    # for convenience, let's standardize the order of fields in output data
    meta = {field: meta.get(field) for field in _META_FIELDS}
    return (html, meta)


def save_page_data_or_log(
    data: Union[str, Dict[str, Any]], fpath: pathlib.Path, force: bool,
):
    if fpath.exists() and force is False:
        logging.warning(
            "%s already exists and `force` is False; data will not be saved", fpath,
        )
    else:
        if isinstance(data, str):
            dd.utils.save_text_data(data, fpath)
        elif isinstance(data, dict):
            dd.utils.save_toml_data(data, fpath)
        else:
            raise TypeError(f"data type {type(data)} is invalid")


if __name__ == "__main__":
    sys.exit(main())
