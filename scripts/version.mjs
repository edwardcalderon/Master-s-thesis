import { access, readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const rootDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const command = process.argv[2] ?? "check";
const readmeOnly = process.argv.includes("--readme-only");
const workspacePackageFiles = [
  "apps/web/package.json",
  "packages/content/package.json",
  "packages/ui/package.json"
];
const releaseMarker = /<!-- versioning:release:start -->[\s\S]*?<!-- versioning:release:end -->/;

const file = (...segments) => path.join(rootDir, ...segments);
const read = (relativePath) => readFile(file(relativePath), "utf8");
const write = (relativePath, contents) => writeFile(file(relativePath), contents);
const readJson = async (relativePath) => JSON.parse(await read(relativePath));
async function fileExists(relativePath) {
  try {
    await access(file(relativePath));
    return true;
  } catch (error) {
    if (error.code === "ENOENT") return false;
    throw error;
  }
}

function assertVersion(version, source) {
  if (!/^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$/.test(version)) {
    throw new Error(`${source} must contain a semantic version, received: ${version}`);
  }
}

function releaseBlock(version, locale = "en") {
  const tag = `v${version}`;
  if (locale === "es") {
    return `<!-- versioning:release:start -->\n**Versión actual:** [\`${tag}\`](https://github.com/edwardcalderon/Master-s-thesis/releases/tag/${tag})\n**Registro:** [Versiones de GitHub](https://github.com/edwardcalderon/Master-s-thesis/releases) · sincronizado con \`@edcalderon/versioning\`\n<!-- versioning:release:end -->`;
  }
  return `<!-- versioning:release:start -->\n**Current release:** [\`${tag}\`](https://github.com/edwardcalderon/Master-s-thesis/releases/tag/${tag})\n**Tracker:** [GitHub releases](https://github.com/edwardcalderon/Master-s-thesis/releases) · synchronized with \`@edcalderon/versioning\`\n<!-- versioning:release:end -->`;
}

function changelogSummary(changelog, version, relativePath) {
  const lines = changelog.split(/\r?\n/);
  const headingPattern = /^##\s+\[?v?(\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?)\]?/;

  for (let start = 0; start < lines.length; start += 1) {
    const match = lines[start].match(headingPattern);
    if (match?.[1] !== version) continue;

    let end = start + 1;
    while (end < lines.length && !/^#{1,2}\s/.test(lines[end])) end += 1;
    const body = lines.slice(start + 1, end).join("\n").trim();
    if (/^###\s/m.test(body) && /^-\s/m.test(body)) return body;
  }

  throw new Error(`${relativePath} has no populated changelog entry for v${version}.`);
}

function replaceLatestChanges(readme, summary, version, locale) {
  const lines = readme.split(/\r?\n/);
  const titlePattern = locale === "es"
    ? /^##\s+(?:📋\s+)?Últimos cambios\b/i
    : /^##\s+(?:📋\s+)?Latest Changes\b/i;
  const start = lines.findIndex((line) => titlePattern.test(line));
  if (start === -1) throw new Error(`README${locale === "es" ? ".es" : ""}.md is missing its latest-changes section.`);

  let end = start + 1;
  while (end < lines.length && !/^#{1,2}\s/.test(lines[end])) end += 1;

  const title = locale === "es"
    ? `## 📋 Últimos cambios (v${version})`
    : `## 📋 Latest Changes (v${version})`;
  const footer = locale === "es"
    ? "Consulta el [historial completo](./CHANGELOG.es.md) y las [versiones de GitHub](https://github.com/edwardcalderon/Master-s-thesis/releases). [English version](./README.md)."
    : "For full version history, see [CHANGELOG.md](./CHANGELOG.md) and [GitHub releases](https://github.com/edwardcalderon/Master-s-thesis/releases).";
  const section = `${title}\n\n${summary}\n\n${footer}`;
  const before = lines.slice(0, start).join("\n").replace(/\n+$/, "");
  const after = lines.slice(end).join("\n").replace(/^\n+/, "");
  return `${before}\n\n${section}${after ? `\n\n${after}` : ""}`.replace(/\n+$/, "\n");
}

async function syncReadmes(version) {
  const readmes = [
    { readmePath: "README.md", changelogPath: "CHANGELOG.md", locale: "en" },
    { readmePath: "README.es.md", changelogPath: "CHANGELOG.es.md", locale: "es" }
  ];

  for (const { readmePath, changelogPath, locale } of readmes) {
    if (!(await fileExists(readmePath))) continue;

    let readme = await read(readmePath);
    if (!releaseMarker.test(readme)) {
      throw new Error(`${readmePath} is missing the versioning release marker; refusing to update an ambiguous file.`);
    }

    const summary = changelogSummary(await read(changelogPath), version, changelogPath);
    readme = readme.replace(releaseMarker, releaseBlock(version, locale));
    const nextReadme = replaceLatestChanges(readme, summary, version, locale);
    if (nextReadme !== await read(readmePath)) await write(readmePath, nextReadme);
  }
}

async function repositoryVersion() {
  const manifest = await readJson("package.json");
  assertVersion(manifest.version, "package.json version");
  return manifest.version;
}

async function updateJsonVersion(relativePath, version) {
  const manifest = await readJson(relativePath);
  if (manifest.version !== version) {
    manifest.version = version;
    await write(relativePath, `${JSON.stringify(manifest, null, 2)}\n`);
  }
}

async function sync(version) {
  await syncReadmes(version);

  if (readmeOnly) {
    console.log(`✓ English and Spanish README release summaries synchronized to v${version}`);
    return;
  }

  const versionFile = `${version}\n`;
  if (await read("VERSION") !== versionFile) await write("VERSION", versionFile);
  await Promise.all(workspacePackageFiles.map((relativePath) => updateJsonVersion(relativePath, version)));

  for (const locale of ["en", "es"]) {
    const contentPath = `packages/content/src/locales/${locale}.json`;
    const content = await readJson(contentPath);
    if (!content.thesis || typeof content.thesis.version !== "string") {
      throw new Error(`Could not locate the public version in ${contentPath}.`);
    }
    if (content.thesis.version !== version) {
      content.thesis.version = version;
      await write(contentPath, `${JSON.stringify(content, null, 2)}\n`);
    }
  }

  const thesisPath = "thesis/main.tex";
  const thesis = await read(thesisPath);
  if (!/\\newcommand\{\\versionTesis\}\{v[^}]+\}/.test(thesis)) {
    throw new Error(`Could not locate \\versionTesis in ${thesisPath}.`);
  }
  const nextThesis = thesis.replace(/\\newcommand\{\\versionTesis\}\{v[^}]+\}/, `\\newcommand{\\versionTesis}{v${version}}`);
  if (nextThesis !== thesis) await write(thesisPath, nextThesis);

  const spanishThesisPath = "thesis/es/main.tex";
  const spanishThesis = await read(spanishThesisPath);
  if (!/\\newcommand\{\\versionTesis\}\{v[^}]+\}/.test(spanishThesis)) {
    throw new Error("Could not locate \\versionTesis in " + spanishThesisPath + ".");
  }
  const nextSpanishThesis = spanishThesis.replace(
    /\\newcommand\{\\versionTesis\}\{v[^}]+\}/,
    "\\newcommand{\\versionTesis}{v" + version + "}"
  );
  if (nextSpanishThesis !== spanishThesis) await write(spanishThesisPath, nextSpanishThesis);


  const history = await readJson("VERSION_HISTORY.json");
  if (!Array.isArray(history)) throw new Error("VERSION_HISTORY.json must contain an array.");
  let releaseRecord = history.find((entry) => entry.version === version);
  if (!releaseRecord) {
    releaseRecord = {
      version,
      date: new Date().toISOString().slice(0, 10),
      status: "release",
      summary: `Synchronized release v${version} with @edcalderon/versioning.`
    };
    history.push(releaseRecord);
    await write("VERSION_HISTORY.json", `${JSON.stringify(history, null, 2)}\n`);
  }

  if (await fileExists("VERSION_HISTORY.es.json")) {
    const spanishHistory = await readJson("VERSION_HISTORY.es.json");
    if (!Array.isArray(spanishHistory)) throw new Error("VERSION_HISTORY.es.json must contain an array.");
    if (!spanishHistory.some((entry) => entry.version === version)) {
      spanishHistory.push({
        version,
        date: releaseRecord.date,
        status: releaseRecord.status,
        summary: `Versión v${version} sincronizada con @edcalderon/versioning.`
      });
      await write("VERSION_HISTORY.es.json", `${JSON.stringify(spanishHistory, null, 2)}\n`);
    }
  }

  console.log(`✓ repository artifacts synchronized to v${version}`);
}

async function check(version) {
  const errors = [];
  const versionFile = (await read("VERSION")).trim();
  if (versionFile !== version) errors.push(`VERSION is ${versionFile || "empty"}; expected ${version}.`);

  for (const relativePath of workspacePackageFiles) {
    const manifest = await readJson(relativePath);
    if (manifest.version !== version) errors.push(`${relativePath} is ${manifest.version}; expected ${version}.`);
  }

  for (const locale of ["en", "es"]) {
    const content = await readJson(`packages/content/src/locales/${locale}.json`);
    if (content.thesis?.version !== version) {
      errors.push(`packages/content/src/locales/${locale}.json does not expose ${version}.`);
    }
  }

  const thesis = await read("thesis/main.tex");
  const spanishThesis = await read("thesis/es/main.tex");
  const expectedSpanishThesisVersion = "\\newcommand{\\versionTesis}{v" + version + "}";
  if (!spanishThesis.includes(expectedSpanishThesisVersion)) {
    errors.push("thesis/es/main.tex does not expose v" + version + ".");
  }
  if (!thesis.includes(`\\newcommand{\\versionTesis}{v${version}}`)) {
    errors.push(`thesis/main.tex does not expose v${version}.`);
  }

  const history = await readJson("VERSION_HISTORY.json");
  if (history.at(-1)?.version !== version) {
    errors.push(`VERSION_HISTORY.json ends at ${history.at(-1)?.version ?? "nothing"}; expected ${version}.`);
  }
  if (await fileExists("VERSION_HISTORY.es.json")) {
    const spanishHistory = await readJson("VERSION_HISTORY.es.json");
    if (spanishHistory.at(-1)?.version !== version) {
      errors.push(`VERSION_HISTORY.es.json ends at ${spanishHistory.at(-1)?.version ?? "nothing"}; expected ${version}.`);
    }
    if (JSON.stringify(history.map((entry) => entry.version)) !== JSON.stringify(spanishHistory.map((entry) => entry.version))) {
      errors.push("VERSION_HISTORY.json and VERSION_HISTORY.es.json do not contain the same releases in the same order.");
    }
  }

  const readme = await read("README.md");
  if (!readme.includes(releaseBlock(version))) {
    errors.push(`README.md tracker does not match v${version}. Run pnpm version:sync.`);
  }
  const englishSummary = changelogSummary(await read("CHANGELOG.md"), version, "CHANGELOG.md");
  if (!readme.includes(`## 📋 Latest Changes (v${version})`) || !readme.includes(englishSummary)) {
    errors.push(`README.md latest changes do not match CHANGELOG.md for v${version}. Run pnpm readme:update.`);
  }
  if (await fileExists("README.es.md")) {
    const spanishReadme = await read("README.es.md");
    if (!spanishReadme.includes(releaseBlock(version, "es"))) {
      errors.push(`README.es.md tracker does not match v${version}. Run pnpm version:sync.`);
    }
    const spanishSummary = changelogSummary(await read("CHANGELOG.es.md"), version, "CHANGELOG.es.md");
    if (!spanishReadme.includes(`## 📋 Últimos cambios (v${version})`) || !spanishReadme.includes(spanishSummary)) {
      errors.push(`README.es.md latest changes do not match CHANGELOG.es.md for v${version}. Run pnpm readme:update.`);
    }
  }

  if (errors.length) throw new Error(`Version integrity check failed:\n- ${errors.join("\n- ")}`);
  console.log(`✓ thesis workspace version ${version} is synchronized`);
}

const version = await repositoryVersion();

if (command === "sync") {
  await sync(version);
} else if (command === "readme") {
  await syncReadmes(version);
  console.log(`✓ English and Spanish README summaries synchronized to v${version}`);
} else if (command === "check") {
  await check(version);
} else {
  throw new Error(`Unknown version command: ${command}. Use check or sync.`);
}
