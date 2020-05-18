import datetime
import logging
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, Union

import arrow
import extruct
import ftfy
import httpx

LOGGER = logging.getLogger(__name__)

CONTEXTS = {"http://schema.org", "https://schema.org",}
ARTICLE_TYPES = {
    "Article",
    "TechArticle",
    "NewsArticle", "AnalysisNewsArticle", "AskPublicNewsArticle", "BackgroundNewsArticle", "OpinionNewsArticle", "ReportageNewsArticle", "ReviewNewsArticle",
    "BlogPosting", "LiveBlogPosting",
}
PAGE_TYPES = {"WebPage",}
METADATA_SYNTAXES = {"microdata", "json-ld"}


def get_html(
    url: str,
    client: Optional[httpx.Client] = None,
    **kwargs,
) -> Tuple[str, httpx.Response]:
    if client is None:
        response = httpx.get(url, **kwargs)
    else:
        response = client.get(url, **kwargs)
    response.raise_for_status()
    html = response.text
    return html, response


def get_data_from_html(html: str) -> Dict[str, Any]:
    data = {}
    metadata = extruct.extract(html, syntaxes=list(METADATA_SYNTAXES), uniform=True)
    for syntax in METADATA_SYNTAXES:
        for jsonld in metadata[syntax]:
            _check_context(jsonld)
            type_ = jsonld.get("@type")
            if type_ in ARTICLE_TYPES:
                syntax_data = {
                    "text": get_article_body(jsonld),
                    "url": get_canonical_url(jsonld),
                    "title": get_title(jsonld),
                    "dt_published": get_dt_published(jsonld),
                }
                data.update({key: val for key, val in syntax_data.items() if val})
    return data


def _check_context(jsonld: dict):
    context = jsonld.get("@context")
    if context not in CONTEXTS:
        LOGGER.warning(
            "context=%s is invalid; should be one of %s", context, CONTEXTS,
        )


def get_article_body(jsonld: dict) -> Optional[str]:
    """Extract and clean data from the 'articleBody' or 'text' property, in that order."""
    article_body = (
        jsonld.get("articleBody") if "articleBody" in jsonld else jsonld.get("text")
    )
    if article_body is None:
        return None
    elif isinstance(article_body, str):
        return _parse_text_dtype(article_body, split=False)
    elif isinstance(article_body, list) and all(isinstance(para, str) for para in article_body):
        return "\n\n".join(_parse_text_dtype(para, split=False) for para in article_body)
    else:
        LOGGER.warning(
            "article_body=%s must be of type Optional[Union[str, List[str]]], not %s",
            article_body, type(article_body),
        )
        return None


def get_canonical_url(jsonld: dict) -> Optional[str]:
    """
    Extract and clean data from the 'url' or 'mainEntityOfPage.@id' property,
    in that order.
    """
    url = jsonld.get("url") if "url" in jsonld else jsonld.get("mainEntityOfPage")
    if url is None:
        return None
    elif isinstance(url, str):
        return url.strip()
    elif isinstance(url, dict) and _item_is_valid_type(url, ARTICLE_TYPES | PAGE_TYPES):
        url = url.get("@id")
        if url is None:
            return None
        elif isinstance(url, str):
            return url.strip()
        else:
            LOGGER.warning(
                "mainEntityOfPage.id=%s must be of type Optional[str], not %s",
                url, type(url),
            )
            return None
    else:
        LOGGER.warning(
            "url=%s must be of type Optional[Union[str, dict]], not %s",
            url, type(url),
        )
        return None


def get_dt_published(jsonld: dict) -> Optional[datetime.datetime]:
    """Extract and clean data from the 'datePublished' property."""
    dt = (
        jsonld.get("datePublished") if "datePublished" in jsonld else
        jsonld.get("dateCreated")
    )
    return _parse_dt_dtype(dt)


def get_title(jsonld: dict) -> Optional[str]:
    """
    Extract and clean data from the 'headline', 'alternativeHeadline', or 'name'
    property, in that order.
    """
    title = (
        jsonld.get("headline") if "headline" in jsonld else
        jsonld.get("alternativeHeadline") if "alternativeHeadline" in jsonld else
        jsonld.get("name")
    )
    return _parse_text_dtype(title, split=False)


def _parse_dt_dtype(dt: Optional[str]) -> datetime.datetime:
    """
    Parse a https://schema.org/Date or https://schema.org/DateTime data type value,
    and return it as a Python-native datetime object with timezone.
    """
    if dt is None:
        return None
    if isinstance(dt, str):
        try:
            return arrow.get(dt).datetime
        except arrow.parser.ParserError:
            LOGGER.warning("`arrow` unable to parse dt=%s", dt)
            return None
    else:
        LOGGER.warning("dt=%s must be of type Optional[str], not %s", dt, type(dt))
        return None


def _parse_text_dtype(
    value: Optional[str],
    split: bool = False,
) -> Optional[Union[str, List[str]]]:
    """Parse a https://schema.org/Text data type value, optionally splitting on commas."""
    if value is None:
        return None
    elif isinstance(value, str):
        value = ftfy.fix_text(value)
        if split is False:
            return value.strip()
        else:
            return _tidy_text_values(value.split(","))
    else:
        LOGGER.warning(
            "value=%s must be of type Optional[str], not %s",
            value, type(value),
        )
        return None


def _item_is_valid_type(item: Dict, valid_types: Set[str]) -> bool:
    if isinstance(item, dict):
        type_ = item.get("@type")
        if (
            (isinstance(type_, str) and type_ in valid_types) or
            (isinstance(type_, list) and any(item in valid_types for item in type_))
        ):
            return True
    return False


def _tidy_text_values(values: Iterable[str]) -> List[str]:
    values = {value.strip() for value in values}
    return sorted(value for value in values if value)
