import { spawnSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const rootDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const action = process.argv[2] ?? "check";
const editions = [
  { label: "English", directory: "thesis" },
  { label: "Spanish", directory: "thesis/es" }
];

if (!new Set(["check", "fetch"]).has(action)) {
  console.error("Usage: node scripts/check-thesis-similarity.mjs [check|fetch]");
  process.exit(2);
}

let failed = false;
for (const edition of editions) {
  const args = action === "check"
    ? ["check", edition.directory, "--html", "--json"]
    : ["fetch", edition.directory];
  console.log(`${action === "check" ? "Scanning" : "Fetching cited sources for"} ${edition.label} thesis edition`);
  const result = spawnSync("refscan", args, { cwd: rootDir, stdio: "inherit" });

  if (result.error?.code === "ENOENT") {
    console.error(
      "refscan is not installed. Install the pinned version with:\n" +
        "uv tool install --from git+https://github.com/rktreddy/refscan.git@1b4a59e42775521d5610399b1bd093597666fdc7 refscan"
    );
    process.exit(127);
  }
  if (result.error) {
    console.error(`Could not start refscan for ${edition.label}: ${result.error.message}`);
    failed = true;
  } else if (result.status !== 0) {
    failed = true;
  }
}

if (failed) process.exit(1);
