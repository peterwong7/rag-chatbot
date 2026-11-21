"""Fetch CS50P and CS50AI lecture notes.

Downloads the public notes pages, keeps only
the <main> text, and saves one plain-text file
per week or lecture under docs/.

Run: python fetch_notes.py
"""

import os
import re
import urllib.request
from html.parser import HTMLParser

BASE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(BASE, "docs")

PAGES = []
for week in range(10):
    PAGES.append((
        "cs50p-week%d" % week,
        "CS50P Week %d" % week,
        "https://cs50.harvard.edu/python/2022/notes/%d/"
        % week,
    ))
for lec in range(7):
    PAGES.append((
        "cs50ai-lecture%d" % lec,
        "CS50AI Lecture %d" % lec,
        "https://cs50.harvard.edu/ai/2024/notes/%d/"
        % lec,
    ))

BLOCK_TAGS = {"h1", "h2", "h3", "h4", "p", "li",
              "tr", "pre", "blockquote", "div"}


class MainText(HTMLParser):
    """Collect visible text inside <main> only."""

    def __init__(self):
        super().__init__()
        self.in_main = False
        self.skip = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == "main":
            self.in_main = True
            return
        if not self.in_main:
            return
        if tag in ("script", "style", "nav"):
            self.skip = True
        if tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag == "main":
            self.in_main = False
        if tag in ("script", "style", "nav"):
            self.skip = False
        if self.in_main and tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data):
        if self.in_main and not self.skip:
            self.parts.append(data)


def clean(text):
    """Tidy whitespace, keep blank-line breaks."""
    text = text.replace("\r", "")
    lines = []
    for line in text.split("\n"):
        line = re.sub(r"[ \t]+", " ", line).strip()
        lines.append(line)
    out = []
    blank = False
    for line in lines:
        if line == "":
            if not blank:
                out.append("")
            blank = True
        else:
            out.append(line)
            blank = False
    return "\n".join(out).strip() + "\n"


def fetch(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "rag-chatbot/1.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def main():
    os.makedirs(DOCS, exist_ok=True)
    failed = []
    for slug, title, url in PAGES:
        path = os.path.join(DOCS, slug + ".txt")
        try:
            html = fetch(url)
        except Exception as e:
            print("FAIL", slug, e)
            failed.append(slug)
            continue
        parser = MainText()
        parser.feed(html)
        text = clean("".join(parser.parts))
        head = title + "\n" + "=" * len(title) + "\n\n"
        with open(path, "w") as f:
            f.write(head + text)
        print("OK  ", slug, len(text), "chars")
    if failed:
        print("Could not fetch:", ", ".join(failed))


if __name__ == "__main__":
    main()
