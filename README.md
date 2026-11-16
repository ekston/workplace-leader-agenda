# Workplace Leader Weekly Agenda

Static site for https://workplaceleaders.ch/, served by GitHub Pages from `main` (root).
Plain HTML and CSS with a little vanilla JS for the appendix filters. No framework, no build pipeline, no cookies, no tracking, no external requests (system font stack: Inter if installed, otherwise Helvetica Neue / Helvetica / Arial).

## Layout

| Path | What |
| --- | --- |
| `index.html` | Latest edition |
| `editions/YYYY-MM-DD/index.html` | Permanent copy of each edition |
| `editions/YYYY-MM-DD/edition.json` | The edition's content |
| `archive/index.html` | List of all editions |
| `feed.xml` | RSS 2.0 feed, one item per edition |
| `assets/style.css`, `assets/filters.js` | Design and filters |
| `favicon.svg` | Swiss cross on red |
| `CNAME` | `workplaceleaders.ch` |
| `tools/build.py` | Optional helper that regenerates the HTML and feed from the JSON files |

## Adding a weekly edition

1. Copy the latest folder, e.g. `cp -r editions/2026-11-16 editions/2026-11-23`, and delete the copied `index.html`.
2. Edit `editions/2026-11-23/edition.json`: `date`, `date_long`, `kw`, `pubdate_rfc822` (RFC 822, e.g. `Mon, 23 Nov 2026 07:00:00 +0100`), `tradeoff_title` (also the RSS item title), `headline_html`, `summary` (RSS description and meta description), then the trade-off, pillars, calls, anti-pattern, cliffs and items. The four pillars are standing sections defined once in `STANDING` in `tools/build.py` (tag, name, line mark, strapline, order); each edition only supplies `tag`, `subtitle`, `reality`, `action` and `sources` per pillar, and the build stops if one of the four is missing. Source keys are either a key in `urls` or `mc:MC1234567` for a Message Center post.
3. Run `python3 tools/build.py` (Python 3 standard library only). It rewrites `index.html`, every `editions/*/index.html`, `archive/index.html` and `feed.xml`.
4. Check locally with `python3 -m http.server` and open http://localhost:8000/.
5. Commit and push to `main`. GitHub Pages publishes within a minute or two.

You can also edit the HTML files by hand; the helper only saves the copying.

## DNS (Hover)

Apex `workplaceleaders.ch`: A records 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153 (optional AAAA 2606:50c0:8000::153, 2606:50c0:8001::153, 2606:50c0:8002::153, 2606:50c0:8003::153). `www`: CNAME to `ekston.github.io`. Then tick "Enforce HTTPS" in the repository's Pages settings once the certificate is issued.
