#!/usr/bin/env python3
"""Check research-question placement and keep each abstract on a single PDF page.

Requires Poppler's pdftotext. Expected wording is read from the active TeX sources;
this checks rendered pagination and reports abstract height without duplicating text.
"""

import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
import unicodedata


THESIS = Path(__file__).resolve().parent.parent / "thesis"
CHAPTER = Path("chapters/02-problem-and-state-of-the-art.tex")
ABSTRACT = Path("chapters/00-abstract.tex")


def normalize(text: str) -> str:
    # PDF ligatures, line wrapping, and discretionary hyphens are presentation only.
    return re.sub(r"[\s\-\u00ad]+", "", unicodedata.normalize("NFKC", text)).casefold()


def check(source: Path, pdf: Path, heading: str) -> int:
    section = source.read_text(encoding="utf-8").split(r"\section{" + heading + "}", 1)[1]
    # Approval markers are TeX comments inside the quote. Ignore comments when
    # extracting the text so source-control metadata does not break layout QA.
    section = re.sub(r"(?m)(?<!\\)%.*$", "", section)
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


class PdfWordParser(HTMLParser):
    """Read word coordinates from pdftotext's XHTML bbox output."""

    def __init__(self) -> None:
        super().__init__()
        self.pages: list[dict] = []
        self.current_page: dict | None = None
        self.current_word: dict | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "page":
            self.current_page = {
                "height": float(attributes["height"]),
                "words": [],
            }
            self.pages.append(self.current_page)
        elif tag == "word" and self.current_page is not None:
            self.current_word = {
                "top": float(attributes["ymin"]),
                "bottom": float(attributes["ymax"]),
                "text": "",
            }

    def handle_data(self, data: str) -> None:
        if self.current_word is not None:
            self.current_word["text"] += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "word" and self.current_word is not None:
            if self.current_page is not None:
                self.current_page["words"].append(self.current_word)
            self.current_word = None


def check_abstract(source: Path, pdf: Path, heading: str, locale: str) -> float:
    source_text = source.read_text(encoding="utf-8")
    keyword_label = r"\textbf{Keywords:}" if locale == "en" else r"\textbf{Palabras clave:}"
    abstract = source_text.split(r"\section{" + heading + "}", 1)[1]
    keyword_text = abstract.split(keyword_label, 1)[1].strip().rstrip(".")
    last_keyword_word = keyword_text.split(";")[-1].split()[-1]
    result = subprocess.run(
        ["pdftotext", "-bbox-layout", str(pdf), "-"],
        check=True, capture_output=True, text=True, encoding="utf-8",
    )
    parser = PdfWordParser()
    parser.feed(result.stdout)
    heading_text = heading.casefold()
    keyword_label_text = "Keywords:" if locale == "en" else "Palabras clave:"
    for page in parser.pages:
        words = page["words"]
        page_text = " ".join(word["text"] for word in words)
        heading_index = page_text.casefold().find(heading_text)
        keyword_index = page_text.casefold().find(keyword_label_text.casefold(), heading_index)
        if heading_index < 0 or keyword_index < 0:
            continue
        heading_word = next(
            word for word in words
            if heading_text in word["text"].casefold()
        )
        keyword_word_index = next(
            index for index, word in enumerate(words)
            if word["text"].casefold() == keyword_label_text.split()[0].casefold()
            and sum(len(item["text"]) + 1 for item in words[:index]) >= keyword_index
        )
        last_keyword = next(
            (
                word for word in words[keyword_word_index:]
                if word["text"].strip(".,;:").casefold() == last_keyword_word.casefold()
            ),
            None,
        )
        if last_keyword is None:
            raise ValueError(f"{pdf}: cannot locate the final abstract keyword.")
        used = (last_keyword["bottom"] - heading_word["top"]) / page["height"]
        return used
    raise ValueError(f"{pdf}: abstract heading and keywords were not found on one page.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf-root", type=Path, default=THESIS,
                        help="Directory containing main.pdf and es/main.pdf")
    parser.add_argument("--en-pdf", type=Path,
                        help="Optional English PDF path (overrides --pdf-root)")
    parser.add_argument("--es-pdf", type=Path,
                        help="Optional Spanish PDF path (overrides --pdf-root)")
    args = parser.parse_args()
    pdfs = {
        "en": args.en_pdf or args.pdf_root / "main.pdf",
        "es": args.es_pdf or args.pdf_root / "es" / "main.pdf",
    }
    failed = False
    for locale, folder, heading in [
        ("en", Path("."), "Research question"),
        ("es", Path("es"), "Pregunta de investigación"),
    ]:
        try:
            page = check(THESIS / folder / CHAPTER, pdfs[locale], heading)
            print(f"{locale}: complete research question and heading on PDF page {page}")
        except (OSError, ValueError, IndexError, subprocess.CalledProcessError) as error:
            print(f"Layout check failed ({locale}): {error}")
            failed = True
    for locale, folder, heading in [
        ("en", Path("."), "Abstract"),
        ("es", Path("es"), "Resumen"),
    ]:
        try:
            share = check_abstract(THESIS / folder / ABSTRACT, pdfs[locale], heading, locale)
            print(f"{locale}: abstract and keywords occupy {share:.1%} of one page")
        except (OSError, ValueError, IndexError, subprocess.CalledProcessError) as error:
            print(f"Abstract layout check failed ({locale}): {error}")
            failed = True
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
