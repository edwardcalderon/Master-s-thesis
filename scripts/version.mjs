import { readFile, writeFile } from "node:fs/promises";
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

function assertVersion(version, source) {
  if (!/^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$/.test(version)) {
    throw new Error(`${source} must contain a semantic version, received: ${version}`);
  }
}

function releaseBlock(version) {
  const tag = `v${version}`;
  return `<!-- versioning:release:start -->\n**Current release:** [\`${tag}\`](https://github.com/edwardcalderon/Master-s-thesis/releases/tag/${tag})\n**Tracker:** [GitHub releases](https://github.com/edwardcalderon/Master-s-thesis/releases) · synchronized with \`@edcalderon/versioning\`\n<!-- versioning:release:end -->`;
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
  const readme = await read("README.md");
  if (!releaseMarker.test(readme)) {
    throw new Error("README.md is missing the versioning release marker; refusing to update an ambiguous file.");
  }
  const nextReadme = readme.replace(releaseMarker, releaseBlock(version));
  if (nextReadme !== readme) await write("README.md", nextReadme);

  if (readmeOnly) {
    console.log(`✓ README release tracker synchronized to v${version}`);
    return;
  }

  const versionFile = `${version}\n`;
  if (await read("VERSION") !== versionFile) await write("VERSION", versionFile);
  await Promise.all(workspacePackageFiles.map((relativePath) => updateJsonVersion(relativePath, version)));

  const contentPath = "packages/content/src/index.ts";
  const content = await read(contentPath);
  if (!/version:\s*"[^"]+"/.test(content)) {
    throw new Error(`Could not locate the public version in ${contentPath}.`);
  }
  const nextContent = content.replace(/version:\s*"[^"]+"/, `version: "${version}"`);
  if (nextContent !== content) await write(contentPath, nextContent);

  const thesisPath = "thesis/main.tex";
  const thesis = await read(thesisPath);
  if (!/\\newcommand\{\\versionTesis\}\{v[^}]+\}/.test(thesis)) {
    throw new Error(`Could not locate \\versionTesis in ${thesisPath}.`);
  }
  const nextThesis = thesis.replace(/\\newcommand\{\\versionTesis\}\{v[^}]+\}/, `\\newcommand{\\versionTesis}{v${version}}`);
  if (nextThesis !== thesis) await write(thesisPath, nextThesis);

  const history = await readJson("VERSION_HISTORY.json");
  if (!Array.isArray(history)) throw new Error("VERSION_HISTORY.json must contain an array.");
  if (!history.some((entry) => entry.version === version)) {
    history.push({
      version,
      date: new Date().toISOString().slice(0, 10),
      status: "release",
      summary: `Synchronized release v${version} with @edcalderon/versioning.`
    });
    await write("VERSION_HISTORY.json", `${JSON.stringify(history, null, 2)}\n`);
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

  const content = await read("packages/content/src/index.ts");
  if (!content.includes(`version: "${version}"`)) {
    errors.push(`packages/content/src/index.ts does not expose ${version}.`);
  }

  const thesis = await read("thesis/main.tex");
  if (!thesis.includes(`\\newcommand{\\versionTesis}{v${version}}`)) {
    errors.push(`thesis/main.tex does not expose v${version}.`);
  }

  const history = await readJson("VERSION_HISTORY.json");
  if (history.at(-1)?.version !== version) {
    errors.push(`VERSION_HISTORY.json ends at ${history.at(-1)?.version ?? "nothing"}; expected ${version}.`);
  }

  const readme = await read("README.md");
  if (!readme.includes(releaseBlock(version))) {
    errors.push(`README.md tracker does not match v${version}. Run pnpm version:sync.`);
  }

  if (errors.length) throw new Error(`Version integrity check failed:\n- ${errors.join("\n- ")}`);
  console.log(`✓ thesis workspace version ${version} is synchronized`);
}

const version = await repositoryVersion();

if (command === "sync") {
  await sync(version);
} else if (command === "check") {
  await check(version);
} else {
  throw new Error(`Unknown version command: ${command}. Use check or sync.`);
}
