export const thesis = {
  shortTitle: "Master Thesis Lab",
  eyebrow: "Open research workspace · 2026",
  title: "A thesis built to be read, run, and questioned.",
  description:
    "A public-facing research workspace for a reproducible master thesis. The question, method, evidence, and final argument stay close enough to inspect.",
  version: "0.1.1",
  state: "foundation",
  location: "Colombia · distributed lab",
  license: "CC BY-NC 4.0 · source available"
} as const;

export const release = {
  version: thesis.version,
  tag: `v${thesis.version}`,
  trackerUrl: `https://github.com/edwardcalderon/Master-s-thesis/releases/tag/v${thesis.version}`
} as const;

export const notebooks = [
  {
    id: "00",
    title: "Project tour",
    kind: "Orientation",
    description: "The shortest path through the research question, repository, and public artifacts.",
    runtime: "Python 3.12",
    status: "Ready",
    href: "./notebooks/00-project-tour.ipynb",
    accent: "lime"
  },
  {
    id: "01",
    title: "Reproducibility template",
    kind: "Methods",
    description: "A clean starting point for loading data, declaring assumptions, and recording outputs.",
    runtime: "Python · pandas",
    status: "Template",
    href: "./notebooks/01-reproducibility-template.ipynb",
    accent: "orange"
  },
  {
    id: "02",
    title: "Evidence notebook",
    kind: "Analysis",
    description: "Reserved for the first thesis result: one claim, one figure, one traceable source.",
    runtime: "To be defined",
    status: "Planned",
    href: "./notebooks/02-evidence-notebook.ipynb",
    accent: "blue"
  }
] as const;

export const docs = [
  { label: "Research brief", meta: "Start here", href: "./docs/index.md" },
  { label: "Method and assumptions", meta: "How to read the work", href: "./docs/methodology.md" },
  { label: "Reproducibility protocol", meta: "Run it again", href: "./docs/reproducibility.md" },
  { label: "Architecture note", meta: "Why the repo looks like this", href: "./docs/architecture.md" }
] as const;

export const layers = [
  { index: "01", label: "Narrative", detail: "Question, context, contribution" },
  { index: "02", label: "Evidence", detail: "Data, notebooks, figures, logs" },
  { index: "03", label: "Artifact", detail: "LaTeX source, PDF, release" }
] as const;
