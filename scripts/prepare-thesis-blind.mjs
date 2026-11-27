import { cp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const language = process.argv[2];

if (!["en", "es"].includes(language)) {
  throw new Error("Usage: node prepare-thesis-blind.mjs <en|es>");
}

const repositoryRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const thesisRoot = path.join(repositoryRoot, "thesis");
const buildRoot = path.join(thesisRoot, "build");
const stageRoot = path.join(buildRoot, language + "-blind");
const sourceDir = language === "en" ? thesisRoot : path.join(thesisRoot, "es");
const stageDir = path.join(stageRoot, language);
const sourceMain = path.join(sourceDir, "main.tex");
const mainTex = await readFile(sourceMain, "utf8");
const revision = mainTex.match(/\\newcommand\{\\revisionManuscrito\}\{([^}]+)\}/)?.[1];

if (!revision) {
  throw new Error("Could not determine the manuscript revision from " + path.relative(repositoryRoot, sourceMain));
}

await rm(stageRoot, { recursive: true, force: true });
await mkdir(stageDir, { recursive: true });
await cp(sourceMain, path.join(stageDir, "main.tex"));
await cp(path.join(sourceDir, "chapters"), path.join(stageDir, "chapters"), {
  recursive: true,
});

const stagedFigures = language === "en" ? path.join(stageDir, "figures") : path.join(stageRoot, "figures");
await cp(path.join(thesisRoot, "figures"), stagedFigures, {
  recursive: true,
  filter: (source) => !source.endsWith("empirical_dex_pilot_summary.csv"),
});

const bibliography = await readFile(path.join(thesisRoot, "references.bib"), "utf8");
const maskedRepositoryReference = `@misc{calderon2026repository,
  author = {{Anonymous}},
  title = {CEX/DEX research repository (anonymized for peer review)},
  year = {2026},
  note = {Author details and URL withheld}
}`;
const anonymousBibliography = bibliography.replace(
  /@misc\{calderon2026repository,[\s\S]*?\n\}/,
  maskedRepositoryReference,
);

if (anonymousBibliography === bibliography) {
  throw new Error("Could not find the self-identifying repository reference to anonymize");
}

const bibliographyPath = language === "en"
  ? path.join(stageDir, "references.bib")
  : path.join(stageRoot, "references.bib");
await writeFile(bibliographyPath, anonymousBibliography);

console.log("Prepared current " + language + " source for blind rendering (manuscript " + revision + ").");
console.log("Staged LaTeX source: " + path.relative(repositoryRoot, stageDir));
