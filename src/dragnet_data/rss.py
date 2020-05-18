import datetime
import logging
import random
import urllib.parse
from typing import Any, Dict, List, Optional

import feedparser
import ftfy

LOGGER = logging.getLogger(__name__)


def get_entries_from_feed(
    feed: Dict[str, str], *, maxn: Optional[int] = None,
) -> List[Dict]:
    feed_parsed = feedparser.parse(feed["url"])
    entries = feed_parsed.get("entries", [])
    if maxn:
        entries = random.sample(entries, min(maxn, len(entries)))
    LOGGER.info("got %s entries from %s feed", len(entries), feed["name"])
    return entries


def get_data_from_entry(entry: Dict[str, Any]) -> Dict[str, str]:
    data = {
        "url": get_url(entry),
        "title": get_title(entry),
        "dt_published": get_dt_published(entry),
    }
    return {key: val for key, val in data.items() if val}


def get_dt_published(entry: Dict[str, Any]) -> str:
    dt_published_struct = entry.get("published_parsed")
    if dt_published_struct:
        return datetime.datetime(*dt_published_struct[:6]).isoformat()
    else:
        return None


def get_title(entry: Dict[str, Any]) -> str:
    title = entry.get("title")
    if title:
        return ftfy.fix_text(title)
    else:
        return None


def get_url(entry: Dict[str, Any]) -> str:
    link = entry.get("link")
    if link:
        return urllib.parse.urljoin(link, urllib.parse.urlparse(link).path).rstrip("/")
    else:
        return None
