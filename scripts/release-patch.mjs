import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";

const rootDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const pnpm = process.platform === "win32" ? "pnpm.cmd" : "pnpm";
const extraArgs = process.argv.slice(2).filter((argument, index) => !(index === 0 && argument === "--"));

function run(args) {
  execFileSync(pnpm, args, { cwd: rootDir, stdio: "inherit" });
}

// The package owns package/version/changelog updates. The local synchronizer
// projects that version onto the thesis-specific artifacts it cannot discover.
run(["exec", "versioning", "patch", "--config", "versioning.config.json", "--no-commit", "--no-tag", ...extraArgs]);
run(["exec", "versioning", "sync", "--config", "versioning.config.json"]);
run(["readme:update"]);
run(["version:sync"]);
run(["release:verify"]);

console.log("\nPatch release prepared. Review the diff, then commit and tag v<version> deliberately.");
