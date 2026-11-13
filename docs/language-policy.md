# Language policy

## Project default

English (`en`) is the primary language for internal project work, source files,
research notes, notebooks, and documentation. Internal working assets may be English
only. Existing Spanish companion documents can remain when useful, but they are
optional and are not a release requirement.

## Required bilingual surfaces

Only two project surfaces must be available in both English and Spanish:

1. **The web application UI and its user-facing content.** English is the default;
   Spanish is selectable from the interface. Both locale files must contain the same
   keys and content structure.
2. **The final thesis PDFs.** Every final English manuscript revision has a complete
   Spanish translation. Both PDFs share a manuscript revision and are compiled and
   published together. TeX working files are build inputs and are not copied to Pages.

| Role | Public Pages artifact |
| --- | --- |
| English primary | `thesis/master-thesis.pdf` |
| Required Spanish translation | `thesis/master-thesis.es.pdf` |

The manuscript revision is distinct from the workspace release version. The language
check enforces the app locales and matching thesis language, revision, workspace
version, and chapter order. It does not require translations of internal documents,
notebooks, task records, configurations, or experiment assets.

## Updating and publishing

1. Update English UI strings and content, then update the corresponding Spanish UI
   content in the same change.
2. Edit the English manuscript and advance its manuscript revision.
3. Translate the full thesis change into Spanish, preserving equations, tables, figure
   meaning, citations, results, limitations, and section order. Translate or gloss
   English labels embedded in figures where needed.
4. Run `pnpm language:check`, then `make -C thesis pdf`.
5. Publish both thesis PDFs in the same Pages deployment. CI compiles both entry points
   and copies the artifacts as `master-thesis.pdf` and `master-thesis.es.pdf`.

`language-policy.json` identifies the required app locales and manuscript paths.
`scripts/check-language-pair.mjs` checks these mandatory surfaces; additional document
translations are optional.

---

[Español](es/language-policy.md)
