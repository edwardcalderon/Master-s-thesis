# Refscan labeled evaluation fixture

This synthetic fixture checks the limits of exact shingle matching before routine use.
It contains no copied third-party or thesis text. Generate its source PDF and run both
language editions with:

```bash
pnpm thesis:similarity:eval
```

The script requires the pinned `refscan` CLI, `pdflatex`, and Poppler's `pdftotext`.
PDFs, extracted text, and reports are written to the ignored `literature/` directory.

## Labeled cases

| Case | English edition | Spanish edition | Expected behavior |
| --- | --- | --- | --- |
| Verbatim copied prose | Exact source sentence appears unquoted in `sections/cases.tex`. | A Spanish translation of the English source passage is used. | English should match; Spanish should not match the English PDF. |
| Clean prose | Deterministic event-loop description absent from the source. | Independent Spanish description absent from the source. | No match. |
| Correctly quoted and cited text | The source sentence appears in a quote environment with `\cite{fixture2026}`. | Not applicable. | It may still match: refscan reports text overlap and does not determine whether attribution is adequate. |
| Common technical phrase | A generic sentence about constant-product market makers shares a short technical phrase with the source. | Not applicable. | A short phrase may be filtered or appear as a low-context overlap; inspect the passage and confidence. |
| Cross-language translated pair | English source PDF. | Spanish translation of the English source passage. | The exact scanner is not expected to detect translated wording across languages. |

This is a behavior demonstration, not a statistical benchmark. One synthetic source is
not enough to estimate precision, recall, or performance on real academic writing.
Review the HTML/JSON reports manually; never treat matches or missing matches as a
plagiarism decision.

## Observed result on refscan v0.25.0

- English: 4 findings. They include the unquoted copied passage, the properly quoted
  and cited passage, a 7-word common technical statement, and an overlapping run caused
  by repeated fixture text. The quote and technical phrase are known review leads, not
  misconduct findings.
- Spanish: 0 findings against the English source PDF. The translated pair is not
  detected by exact shingle matching; this is a coverage limit, not evidence that the
  Spanish text is original.
- Both runs indexed 1 of 1 fixture source PDFs. The fixture verifies that the report
  contains passage-level overlaps, but it does not validate real-world precision or
  recall.
