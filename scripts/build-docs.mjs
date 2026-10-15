import { readdir, readFile, mkdir, writeFile } from "node:fs/promises";
import { join, relative } from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("..", import.meta.url));
const docsDir = join(root, "docs");
const outDir = join(root, "dist-docs");
await mkdir(outDir, { recursive: true });

const files = (await readdir(docsDir)).filter((file) => file.endsWith(".md")).sort();
const manifest = [];

for (const file of files) {
  const source = await readFile(join(docsDir, file), "utf8");
  const title = source.match(/^#\s+(.+)$/m)?.[1] ?? file.replace(/\.md$/, "");
  const output = file.replace(/\.md$/, ".txt");
  await writeFile(join(outDir, output), source);
  manifest.push({ title, source: relative(root, join(docsDir, file)), artifact: relative(root, join(outDir, output)) });
}

await writeFile(join(outDir, "manifest.json"), `${JSON.stringify(manifest, null, 2)}\n`);
console.log(`✓ prepared ${manifest.length} public thesis documents in dist-docs/`);
