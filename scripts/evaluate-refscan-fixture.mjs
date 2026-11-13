import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const rootDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const fixtureDir = path.join(rootDir, "experiments/refscan_evaluation");
const sourceDir = path.join(fixtureDir, "source");
const outputDir = path.join(fixtureDir, "literature");

function run(command, args, cwd = rootDir, options = {}) {
  const result = spawnSync(command, args, { cwd, stdio: "inherit", ...options });
  if (result.error) {
    console.error(`${command} could not start: ${result.error.message}`);
    process.exit(127);
  }
  if (result.status !== 0) process.exit(result.status ?? 1);
}

fs.rmSync(outputDir, { recursive: true, force: true });
const sourceBuildDir = path.join(outputDir, "source-build");
fs.mkdirSync(sourceBuildDir, { recursive: true });
run("pdflatex", [
  "-interaction=nonstopmode",
  "-halt-on-error",
  `-output-directory=${sourceBuildDir}`,
  "source.tex"
], sourceDir, {
  env: {
    ...process.env,
    TEXMFVAR: "/tmp/refscan-texmfvar",
    TEXMFCONFIG: "/tmp/refscan-texmfconfig",
    TEXMFHOME: "/tmp/refscan-texmfhome"
  }
});

const sourcePdf = path.join(sourceBuildDir, "source.pdf");
for (const edition of ["en", "es"]) {
  const refsDir = path.join(outputDir, edition, "refs");
  fs.mkdirSync(refsDir, { recursive: true });
  fs.copyFileSync(sourcePdf, path.join(refsDir, "fixture2026.pdf"));
}

for (const edition of ["en", "es"]) {
  const paperDir = path.join(fixtureDir, edition);
  console.log(`\nChecking ${edition === "en" ? "English" : "Spanish"} labeled fixture`);
  run("refscan", ["check", paperDir, "--html", "--json"]);
}

console.log(`\nFixture reports and generated PDFs are in ${outputDir} (ignored by Git).`);
