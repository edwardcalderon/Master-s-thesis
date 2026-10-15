# Architecture note

This is a deliberately small monorepo. The public web app is the presentation layer, while research assets remain portable and useful without JavaScript.

```text
apps/web          → public landing page, notebook explorer, PDF viewer shell
packages/content  → typed metadata consumed by web and future clients
packages/ui       → shared visual tokens
docs              → Markdown research context
notebooks         → executable evidence
thesis            → LaTeX source and PDF build
data              → explicit raw/processed boundaries
```

The repository uses pnpm workspaces and Turborepo so a future API, analysis package, or second presentation surface can be added without moving the current public contract.
