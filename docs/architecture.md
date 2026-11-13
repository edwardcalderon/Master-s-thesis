# Architecture note

This is a deliberately small monorepo. The public web app is the presentation layer, while research assets remain portable and useful without JavaScript.

```text
apps/web          → bilingual public landing page, notebook explorer, PDF viewer shell
packages/content  → versioned English/Spanish content consumed by the web app
packages/ui       → shared visual tokens
docs              → Markdown research context
notebooks         → executable evidence
thesis            → English LaTeX source, required Spanish translation, paired PDFs
docs/es           → Spanish companions for public research documentation
notebooks/es      → Spanish notebook copies with matching code and outputs
data              → explicit raw/processed boundaries
```

The repository uses pnpm workspaces and Turborepo so a future API, analysis package, or second presentation surface can be added without moving the current public contract.

---

[Español](es/architecture.md)
