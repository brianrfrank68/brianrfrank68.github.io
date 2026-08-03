#!/usr/bin/env python3
"""Apply the Gilman FLB theme to a Diamond Mind Baseball HTML export.

Diamond Mind re-exports each league directory (FLB_2026, FLB_2026_pre_1, ...)
wholesale every week: it overwrites dmrpt.css with its plain default and adds
new box-score files that have no stylesheet link at all. This script repairs
both, and is safe to run repeatedly:

  1. Copies the maintained dmrpt_template.css over each directory's dmrpt.css.
  2. For every game box score (bare-digit filename, e.g. 2026032601020.htm):
     - skips it if already processed (has a <link rel="stylesheet"> tag)
     - injects the dmrpt.css link
     - wraps the <pre> block in <div class="boxscore"> so it picks up the
       card styling from the stylesheet
     - fills in the empty <title> from the first line of the box score

Usage:
    python league/style_flb_reports.py
    python league/style_flb_reports.py FLB_2026 FLB_2026_pre_1
    python league/style_flb_reports.py --dry-run
"""

import argparse
import re
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_CSS = Path(__file__).resolve().parent / "dmrpt_template.css"
DEFAULT_DIRS = ["FLB_2026", "FLB_2026_pre_1", "FLB_2026_pre_2", "FLB_2026_pre_3"]

BOX_SCORE_RE = re.compile(r"^\d+\.htm$")
CSS_LINK = '<link rel="stylesheet" type="text/css" href="dmrpt.css">'


def style_box_score(html: str) -> str | None:
    """Return the updated HTML, or None if no change was made."""
    if "dmrpt.css" in html:
        return None  # already processed

    updated = html.replace("</head>", f"</head>\n{CSS_LINK}", 1)

    updated = re.sub(
        r'(<body[^>]*>)\s*<pre>',
        r'\1\n<div class="boxscore">\n<pre>',
        updated,
        count=1,
    )
    updated = updated.replace("</pre>\n\n</body>", "</pre>\n</div>\n\n</body>", 1)

    match = re.search(r"<pre>\s*\n(.+)", updated)
    if match:
        first_line = match.group(1).strip()
        updated = updated.replace("<title></title>", f"<title>{first_line}</title>", 1)

    return updated


def process_directory(directory: Path, dry_run: bool) -> None:
    if not directory.is_dir():
        print(f"skip {directory.name}: not a directory")
        return

    css_path = directory / "dmrpt.css"
    if dry_run:
        print(f"[dry-run] would copy {TEMPLATE_CSS.name} -> {css_path}")
    else:
        shutil.copyfile(TEMPLATE_CSS, css_path)

    updated_count = 0
    skipped_count = 0
    for htm_file in sorted(directory.glob("*.htm")):
        if not BOX_SCORE_RE.match(htm_file.name):
            continue
        original = htm_file.read_text(encoding="utf-8", errors="replace")
        updated = style_box_score(original)
        if updated is None:
            skipped_count += 1
            continue
        updated_count += 1
        if not dry_run:
            htm_file.write_text(updated, encoding="utf-8")

    verb = "would update" if dry_run else "updated"
    print(f"{directory.name}: css refreshed, {verb} {updated_count} box score(s), "
          f"{skipped_count} already styled")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "directories", nargs="*", default=DEFAULT_DIRS,
        help="league directories to process (default: all FLB_2026* dirs)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="report what would change without writing anything",
    )
    args = parser.parse_args()

    if not TEMPLATE_CSS.exists():
        print(f"error: template stylesheet not found at {TEMPLATE_CSS}", file=sys.stderr)
        return 1

    for name in args.directories:
        process_directory(REPO_ROOT / name, args.dry_run)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
