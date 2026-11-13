# LANG-001 — Bilingual web UI and final thesis

- **Owner:** `edcalderon`
- **Status:** DONE
- **Goal:** Keep the application UI in English and Spanish and publish final thesis PDFs
  in both languages. Internal documentation and working assets may remain English-only.

## Acceptance criteria

- App defaults to English and allows switching to Spanish.
- English and Spanish app locale data have matching structure.
- English and Spanish thesis sources share the same manuscript revision and workspace
  version, and both PDFs compile.
- Language policy and checks enforce only these bilingual surfaces.

## Progress

- `pnpm language:check` passed.
- `pnpm build` passed.
- `make -C thesis pdf` compiled both editions (8 pages each); LaTeX emitted one
  underfull-box warning.
- `pnpm docs:build` passed; optional Spanish docs remain available.
- Interactive PinchTab QA confirmed English is the initial UI language, Spanish switches
  all visible app copy, and switching back restores English.
- The document `lang` attribute followed the selected locale (`en`/`es`). The English
  and Spanish PDF links resolve to `./thesis/master-thesis.pdf` and
  `./thesis/master-thesis.es.pdf`; source links resolve to the matching LaTeX trees.

## Next action

No further LANG-001 implementation remains. Repeat the language build and browser QA
after future changes to locale data or the manuscript publication UI.
