#!/usr/bin/env python3
"""Reject PDFs that split the research question from its heading or across pages.

Requires Poppler's pdftotext. The expected wording comes from the active TeX source;
this checks rendered pagination without duplicating the bilingual research questions.
"""

import argparse
from pathlib import Path
import re
import subprocess
import unicodedata


THESIS = Path(__file__).resolve().parent.parent / "thesis"
CHAPTER = Path("chapters/02-problem-and-state-of-the-art.tex")


def normalize(text: str) -> str:
    # PDF ligatures, line wrapping, and discretionary hyphens are presentation only.
    return re.sub(r"[\s\-\u00ad]+", "", unicodedata.normalize("NFKC", text)).casefold()


def check(source: Path, pdf: Path, heading: str) -> int:
    section = source.read_text(encoding="utf-8").split(r"\section{" + heading + "}", 1)[1]
    question = re.search(
        r"\\begin\{quote\}\s*\\emph\{(.*?)\}\s*\\end\{quote\}", section, re.DOTALL
    )
    if question is None:
        raise ValueError(f"Cannot locate the research question in {source}")
    result = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"],
        check=True, capture_output=True, text=True, encoding="utf-8",
    )
    expected = normalize(heading + question.group(1))
    pages = [
        index for index, page in enumerate(result.stdout.split("\f"), start=1)
        if expected in normalize(page)
    ]
    if len(pages) != 1:
        raise ValueError(
            f"{pdf}: research-question heading and full quotation must appear together "
            "on exactly one page, without an intervening table or other text."
        )
    return pages[0]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf-root", type=Path, default=THESIS,
                        help="Directory containing main.pdf and es/main.pdf")
    args = parser.parse_args()
    failed = False
    for locale, folder, heading in [
        ("en", Path("."), "Research question"),
        ("es", Path("es"), "Pregunta de investigación"),
    ]:
        try:
            page = check(THESIS / folder / CHAPTER, args.pdf_root / folder / "main.pdf", heading)
            print(f"{locale}: complete research question and heading on PDF page {page}")
        except (OSError, ValueError, IndexError, subprocess.CalledProcessError) as error:
            print(f"Layout check failed ({locale}): {error}")
            failed = True
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
