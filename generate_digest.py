#!/usr/bin/env python3
"""Regenerates docs/digest.html from data/digests.json."""
import json
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).parent
DIGESTS_PATH = ROOT / "data" / "digests.json"
DIGEST_HTML_PATH = ROOT / "docs" / "digest.html"

TITLE = "Weekly Digest — Company Valuation & IPO Announcements"
TYPE_LABELS = {"funding": "Funding", "ipo": "IPO Timeline"}


def load_digests():
    digests = json.loads(DIGESTS_PATH.read_text())
    digests.sort(key=lambda d: d["week_end"], reverse=True)
    return digests


def build_html(digests):
    if not digests:
        body = "<p>No weekly digests have been generated yet. Check back after the next scheduled run.</p>"
    else:
        sections = []
        for d in digests:
            events_html = ""
            if d.get("notable_events"):
                rows = "\n".join(
                    f"<li><strong>{escape(e['company'])}</strong> "
                    f"[{escape(TYPE_LABELS.get(e.get('type', 'funding'), 'Funding'))}]: "
                    f"<a href=\"{escape(e['link'])}\">{escape(e['title'])}</a> ({escape(e['date'][:10])})</li>"
                    for e in d["notable_events"]
                )
                events_html = f"<ul>\n{rows}\n</ul>"
            else:
                events_html = "<p><em>No notable changes this week.</em></p>"

            sections.append(f"""<section>
<h2>{escape(d['week_start'][:10])} – {escape(d['week_end'][:10])}</h2>
<p>{escape(d.get('summary', ''))}</p>
{events_html}
</section>""")
        body = "\n<hr>\n".join(sections)

    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{escape(TITLE)}</title>
<style>
body {{ font-family: system-ui, sans-serif; max-width: 800px; margin: 2rem auto; padding: 0 1rem; }}
section {{ margin-bottom: 1.5rem; }}
h2 {{ font-size: 1.1rem; }}
a.back {{ display: inline-block; margin-bottom: 1rem; }}
</style></head>
<body>
<p class="back"><a href="/valuation-rss/">&larr; Back to feed</a></p>
<h1>{escape(TITLE)}</h1>
<p>Weekly summary of notable valuation/funding changes for Anthropic, Databricks, OpenAI, Anduril, and Ramp.</p>
{body}
</body></html>
"""


def main():
    digests = load_digests()
    DIGEST_HTML_PATH.write_text(build_html(digests))
    print(f"Wrote {len(digests)} digests to {DIGEST_HTML_PATH}")


if __name__ == "__main__":
    main()
