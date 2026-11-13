import { readdir, readFile, mkdir, writeFile } from "node:fs/promises";
import { join, relative } from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("..", import.meta.url));
const docsDir = join(root, "docs");
const outDir = join(root, "dist-docs");

async function markdownFiles(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const nested = await Promise.all(entries.map(async (entry) => {
    const entryPath = join(directory, entry.name);
    if (entry.isDirectory()) return markdownFiles(entryPath);
    return entry.isFile() && entry.name.endsWith(".md") ? [entryPath] : [];
  }));
  return nested.flat().sort();
}

await mkdir(outDir, { recursive: true });
const files = await markdownFiles(docsDir);
const manifest = [];

for (const sourcePath of files) {
  const source = await readFile(sourcePath, "utf8");
  const relativeSource = relative(docsDir, sourcePath);
  const title = source.match(/^#\s+(.+)$/m)?.[1] ?? relativeSource.replace(/\.md$/, "");
  const artifactPath = relativeSource.replace(/\.md$/, ".txt");
  const targetPath = join(outDir, artifactPath);
  await mkdir(join(targetPath, ".."), { recursive: true });
  await writeFile(targetPath, source);
  manifest.push({
    locale: relativeSource.startsWith("es/") ? "es" : "en",
    title,
    source: relative(root, sourcePath),
    artifact: relative(root, targetPath)
  });
}

await writeFile(join(outDir, "manifest.json"), `${JSON.stringify(manifest, null, 2)}\n`);
console.log(`✓ prepared ${manifest.length} public documents in English and Spanish in dist-docs/`);
