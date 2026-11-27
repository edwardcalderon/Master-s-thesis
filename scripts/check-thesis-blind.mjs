import { readFile } from "node:fs/promises";

const [textPath, metadataPath] = process.argv.slice(2);

if (!textPath || !metadataPath) {
  throw new Error("Usage: node check-thesis-blind.mjs <extracted-text> <pdfinfo-output>");
}

const [extractedText, metadata] = await Promise.all([
  readFile(textPath, "utf8"),
  readFile(metadataPath, "utf8"),
]);

const identityMarkers = [
  "Edward Calderón",
  "Edward Calderon",
  "Calderón Aristizábal, E.",
  "Calderon Aristizabal, E.",
  "Edward Calderón Aristizábal",
  "Edward Calderon Aristizabal",
  "John R. Ballesteros Parra",
  "Universidad Nacional de Colombia",
  "Facultad de Minas",
  "Sede Medellín",
  "Sede Medellin",
  "Medellín, Colombia",
  "Medellin, Colombia",
  "github.com/edwardcalderon",
  "Master-s-thesis",
  "cex-dex-",
  "experiment:mvp",
  "experiments/cex_dex_mvp",
  "f183520b90aa",
  "5e33d51c51a3",
  "a99f9be866b2",
  "h1c-43e446f04adf",
  "5b06486d695e",
  "9438e194aa7e",
  "1d1d9d2f8c5b",
  "dcf2ef01fdc7504834362f7cb38b93801b2effa861f6d0e3be8ed74796cef16f",
  "9c221ada2b8a2150d238c11d320e34fd3697a6a67d193ab4951b48547b09623f",
  "06778ccfb4db032d8ae143dcd4396d8786ee7814",
  "thesis/literature-audit",
];

function normalize(value) {
  return value
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .replace(/\s+/g, " ")
    .toLocaleLowerCase("en");
}

const normalizedText = normalize(extractedText);
const visibleMatches = identityMarkers.filter((marker) =>
  normalizedText.includes(normalize(marker)),
);

if (visibleMatches.length > 0) {
  throw new Error(`Identifying text remains in the blind PDF: ${visibleMatches.join(", ")}`);
}

const author = metadata.match(/^Author:[ \t]*([^\r\n]*)/m)?.[1]?.trim();

if (author) {
  throw new Error(`PDF author metadata is not blank: ${author}`);
}

console.log("Blind-review checks passed: identifying text and PDF author metadata are absent.");
