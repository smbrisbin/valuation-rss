#!/usr/bin/env python3
"""Regenerates public/feed.xml and public/index.html from data/events.json."""
import json
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).parent
EVENTS_PATH = ROOT / "data" / "events.json"
FEED_PATH = ROOT / "docs" / "feed.xml"
INDEX_PATH = ROOT / "docs" / "index.html"

FEED_TITLE = "Company Valuation Announcements"
FEED_DESC = "Funding round and valuation announcements for Anthropic, Databricks, OpenAI, Anduril, and Ramp."
FEED_LINK = "https://smbrisbin.github.io/valuation-rss/"
SELF_LINK = "https://smbrisbin.github.io/valuation-rss/feed.xml"


def load_events():
    events = json.loads(EVENTS_PATH.read_text())
    events.sort(key=lambda e: e["date"], reverse=True)
    return events


def rfc822(date_str):
    dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    return format_datetime(dt)


def build_rss(events):
    items = []
    for e in events:
        items.append(f"""    <item>
      <title>{escape(e['title'])}</title>
      <link>{escape(e['link'])}</link>
      <guid isPermaLink="false">{escape(e['guid'])}</guid>
      <pubDate>{rfc822(e['date'])}</pubDate>
      <category>{escape(e['company'])}</category>
      <description>{escape(e['summary'])}</description>
    </item>""")

    now = format_datetime(datetime.now(timezone.utc))
    items_xml = "\n".join(items)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>{escape(FEED_TITLE)}</title>
    <link>{escape(FEED_LINK)}</link>
    <description>{escape(FEED_DESC)}</description>
    <language>en-us</language>
    <lastBuildDate>{now}</lastBuildDate>
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="{escape(SELF_LINK)}" rel="self" type="application/rss+xml"/>
{items_xml}
  </channel>
</rss>
"""


def build_index(events):
    rows = "\n".join(
        f"<tr><td>{escape(e['date'][:10])}</td><td>{escape(e['company'])}</td>"
        f"<td><a href=\"{escape(e['link'])}\">{escape(e['title'])}</a></td></tr>"
        for e in events
    )
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{escape(FEED_TITLE)}</title>
<style>
body {{ font-family: system-ui, sans-serif; max-width: 800px; margin: 2rem auto; padding: 0 1rem; }}
table {{ border-collapse: collapse; width: 100%; }}
td {{ padding: 0.5rem; border-bottom: 1px solid #ddd; vertical-align: top; }}
a.feed {{ display: inline-block; margin-bottom: 1rem; }}
</style></head>
<body>
<h1>{escape(FEED_TITLE)}</h1>
<p>{escape(FEED_DESC)}</p>
<p class="feed"><a href="/feed.xml">Subscribe: /feed.xml</a></p>
<table>
<tr><th>Date</th><th>Company</th><th>Announcement</th></tr>
{rows}
</table>
</body></html>
"""


def main():
    events = load_events()
    FEED_PATH.write_text(build_rss(events))
    INDEX_PATH.write_text(build_index(events))
    print(f"Wrote {len(events)} events to {FEED_PATH} and {INDEX_PATH}")


if __name__ == "__main__":
    main()
