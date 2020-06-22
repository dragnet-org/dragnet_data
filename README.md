# dragnet data

Repository of code and data used to build a training dataset for [`dragnet`](https://github.com/dragnet-org/dragnet) models. Specifically:

- code to fetch a random sample of the latest articles published to a manually-specified collection of RSS feeds
- code to fetch articles' HTML data via HTTP GET requests, along with any relevant metadata embedded therein
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

## methodology and data

Web pages are assigned universally unique ids based on the canonical URLs used to fetch their HTML. Each page is represented by two files:

- `data/html/[UUID].html`: Raw page HTML downloaded via HTTP GET request using the `httpx` package. No JavaScript is run on the page; character encodings are inferred.
- `data/meta/[UUID].toml`: Structured metadata extracted from page HTML in JSON-LD or microdata formats. Results vary by page, but may include canonical url, title, date published, and a decent first pass on main text content.

### gold-standard text extractions

For each page, the main text content is manually extracted from the raw HTML by following these steps:

1. Open the page's HTML file (`data/html[UUID].html`) in a web browser for which JavaScript has been disabled. There's no need to disconnect from the internet.
2. Open the corresponding metadata file (`data/meta/[UUID].toml`) in a text editor.
3. In the web browser, manually highlight the page's title, copy the text, then assign it to the `title` field and the first line of the `text` field in the text editor. If the page's metadata already has an extracted `title` field, make sure that the content is the same.
4. In the web browser, manually highlight the page's main text content, either all at once or in convenient chunks. Take care to select only included components (details below). Copy the text over to the text editor as before.

Web page components included in text extractions:

- title
- subtitles, ledes, and summaries
- main body text
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

From `data/html/0a9bec8e-7d7b-3711-81d1-9c11afa7e945.html`:

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
                    ...
                </article>
            </div>
        </div>
        ...
    </body>
</html>
```

From `data/meta/0a9bec8e-7d7b-3711-81d1-9c11afa7e945.toml`:

```toml
id = "0a9bec8e-7d7b-3711-81d1-9c11afa7e945"
url = "https://seekingalpha.com/article/4349447-1-sale-and-10-buys-i-just-made-in-retirement-portfolio"
title = "1 Sale And 10 Buys I Just Made In My Retirement Portfolio"
dt_published = 2020-05-21T22:03:34Z
text = '''
1 Sale And 10 Buys I Just Made In My Retirement Portfolio

Summary

Corporate fundamentals have been collapsing ...
```
