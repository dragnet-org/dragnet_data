# dragnet data

Repository of code and data used to build a training dataset for [`dragnet`](https://github.com/dragnet-org/dragnet) models. Specifically:

- code to fetch a random sample of the latest articles published to a manually-specified collection of RSS feeds
- code to fetch articles' HTML data via HTTP GET requests, along with a draft extraction of relevant metadata embedded therein
- code to save all (HTML, metadata) documents in gztar archives
- data produced by the above code, in conjunction with a manual text extraction process

## setup

To make the training dataset accessible for `dragnet`, do the following:

```bash
$ git clone https://github.com/bdewilde/dragnet_data.git
$ cd dragnet_data
$ tar xvf data/html.tar.gz
$ tar xvf data/meta.tar.gz
```

If you'll be developing with the code, you'll also need to install it as a package:

```bash
$ pip install -e .
$ pip install -e .[dev]
```

## process

1. Make sure you've extracted the archive files containing gold-standard HTML (`/data/html.tar.gz`) and extracted metadata (`/data/meta.tar.gz`), as described in the preceding section. _This is important!_
2. Fetch a batch of RSS pages from the RSS feeds specified in `/data/rss_feeds.toml`, optionally filtering to a subset of feeds, with additional control over the total and per-feed number of pages to fetch. Examples:

    ```bash
    $ python scripts/fetch_rss_data.py
    $ python scripts/fetch_rss_data.py --only_feeds "BBC News" "CNN" "WebMD Health"
    $ python scripts/fetch_rss_data.py --maxn_pages 100 --maxn_pages_per_feed 10
    ```

3. Scrape HTML and automatically extract draft metadata for the pages just fetched. If specifying a custom RSS pages file, be sure to use the same value as in the previous step! Examples:

    ```bash
    $ python scripts/fetch_html_data.py
    $ python scripts/fetch_html_data.py --pages_fpath "/path/to/my_rss_pages.toml"
    ```

4. Extract gold-standard text, title, and date published for each page in the batch, as described in detail below.
5. Move all completed (html, meta) files into the "official" gold-standard data directories: `/data/html` and `/data/meta`, respectively.
6. Package the new data up into archive files and add their UUIDs to the tally. Any inconsistencies arising from file-handling _should_ be caught automatically:

    ```bash
    $ python scripts/archive_data.py
    ```

7. Commit the changes and push them to the repo!

## data and methodology

Web pages are assigned universally unique ids (UUIDs) based on the canonical URLs used to fetch their HTML. Each page is represented by two files:

- `/data/html/[UUID].html`: Raw page HTML downloaded via HTTP GET request using the `httpx` package. No JavaScript is run on the page; character encodings are inferred.
- `/data/meta/[UUID].toml`: Structured metadata extracted from page HTML — first via automatic extraction from JSON-LD or microdata formats, followed by a manual pass described below. Results vary by page, but typically include canonical url, title, date published, and main text content.

All pages included in the gold-standard archive data are listed in `/data/page_uuids.txt`.

### gold-standard metadata extractions

For each page, gold-standard metadata is manually extracted from the raw HTML by following these steps:

1. Open the page's HTML file (`/data/html[UUID].html`) in a web browser for which JavaScript has been disabled. There's no need to disconnect from the internet.
2. Open the corresponding metadata file (`/data/meta/[UUID].toml`) in a text editor.

#### `title`

3. In the web browser, manually highlight the visible text content of the page's title, copy the text, then assign it to the `title` field in the text editor. If the page's metadata already has an extracted `title` field (it was automatically extracted), use it as a sanity-check only before overwriting its contents.

Included web page components:

- main page title

Excluded web page components:

- subtitles, ledes, and summaries

#### `dt_published`

4. In the web browser, manually highlight the visible text content containing the page's date published data, if present; copy the text, then assign it to the `dt_published` field in the text editor. If the page's metadata already has an extracted `dt_published` field (it was automatically extracted), use it as a sanity-check only before overwriting its contents; if there's an automatically extracted value but no visible text content for you to copy, remove the field and its value from the metadata file.

Note that automatic extractions are saved in toml-native datetime format, but you'll be pasting in a human-friendly text string. All gold-standard extractions must be visible web page content, not structured metadata embedded within HTML documents.

Included web page components:

- days, dates, times, and timezones in any recognizable format
- humanized date/time representations, such as "Today" or "13 hours ago"

Excluded web page components:

- labeling or connective prefix, such as "Published: ..." or "on ..."
- symbols adjacent to but _external_ to date/time text separating it from other components
- similar date/time text for "date updated", when presented alongside "date published"
- recognizable date/time published if it's used as the start of main article text

#### `text`

5. In the web browser, manually highlight the page's main visible text content, either all at once or in convenient chunks. Take care to select only included components (details below). Copy the text over to the text editor as before, and be sure to spread it out across multiple lines using toml's multi-line literal string syntax (`'''`).

Web page components included in text extractions:

- main body text
- subtitles, ledes, and summaries
- pull quotes and block quotes
- visible image captions, excluding sourcing info
- visible text content of embedded social media posts

Web page components excluded from text extractions:

- advertisements
- visitor comments or callouts to them
- navigational elements, such as global nav bars, breadcrumbs, and "related content" links/previews
- page metadata, such as authorship, publication date, section/content tags, reading duration, and sourcing info (usually)
- site-specific boilerplate content that isn't actually _page_-specific
- links with calls to action, such as "share", "donate", "subscribe", "buy", "download", or "fact-check"
- embedded tables and other structured data representations (usually)
- image captions included within photo galleries
- urls of images displayed in embedded social media posts

### example page data

From `/data/html/0a9bec8e-7d7b-3711-81d1-9c11afa7e945.html`:

```html
<!DOCTYPE html>
<html itemscope="" itemtype="https://schema.org/WebPage" lang="en">
    <head>
        <meta charset="utf-8" />
        <meta content="IE=edge" http-equiv="X-UA-Compatible" />
        <meta content="width=device-width" name="viewport" />
        <title>1 Sale And 10 Buys I Just Made In My Retirement Portfolio | Seeking Alpha</title>
        ...
    </head>
    <body class="sa-a">
        ...
        <div id="main_content" class="col-xs-7">
            <div id="content-rail" role="main">
                <article>
                    ...
                    <h1>1 Sale And 10 Buys I just Made In My Retirement Portfolio</h1>
                    <div class="a-info clearfix">
                        ::before
                        <time content="2020-05-21T22:03:34Z">May 21, 2020 6:03 PM ET</time>
                        <span id="a-comments-wrapper"></span>
                        ...
                    </div>
                    ...
                </article>
            </div>
        </div>
        ...
    </body>
</html>
```

From `/data/meta/0a9bec8e-7d7b-3711-81d1-9c11afa7e945.toml`:

```toml
id = "0a9bec8e-7d7b-3711-81d1-9c11afa7e945"
url = "https://seekingalpha.com/article/4349447-1-sale-and-10-buys-i-just-made-in-retirement-portfolio"
title = "1 Sale And 10 Buys I Just Made In My Retirement Portfolio"
dt_published = "May 21, 2020 6:03 PM ET"
text = '''
Summary

Corporate fundamentals have been collapsing ...
```

### RSS feeds

The set of feeds included in `/data/rss_feeds.toml` was manually compiled through the following process:

1. Identify a candidate website through some convenient means -- web search, aggregator site, popular RSS feed listing, etc. -- taking care to prioritize variety of content and site structure relative to any sites already in the list.
2. Navigate to the candidate site in a web browser, then check its source code for any links to RSS feeds by searching for `rss` or `application/rss+xml` or `atom`.
3. Copy an appropriate link's `href` value and add it to a new entry in `rss_feeds.toml` along with the site's name (in alphabetical order, by name), structured like so:

    ```
    [[feeds]]
    name = "[SITE NAME]"
    url = "[RSS FEED URL]"
    ```

4. Before officially committing to a feed, it's best to check its contents to make sure that there are entries and that those entries have the expected structure. An easy way is to pass `{"name": "[SITE NAME]", "url": "[RSS_FEED_URL]"}` into `dragnet_data.rss.get_entries_from_feed()` and check its output.

Note that the current set of feeds is pretty good, and we should only add new ones to address specific needs.

## License

The data in this project is licensed under the [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/) license.

The source code used to produce that data is licensed under the MIT license.
