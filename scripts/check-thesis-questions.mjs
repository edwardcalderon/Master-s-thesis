import { execFileSync } from "node:child_process";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const repositoryRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const controlPath = path.join(repositoryRoot, "thesis/question-control.json");
const control = JSON.parse(await readFile(controlPath, "utf8"));

if (control.schemaVersion !== 1 || !Array.isArray(control.approvals) || control.approvals.length === 0) {
  throw new Error("Question control file must contain schema version 1 and an approval record.");
}

const approvalIds = new Set();
for (const approval of control.approvals) {
  if (!approval?.id || approvalIds.has(approval.id)) {
    throw new Error("Question approval records must have unique, non-empty IDs.");
  }
  approvalIds.add(approval.id);

  if (approval.status !== "approved") {
    throw new Error("Question record " + approval.id + " is not approved.");
  }
  if (typeof approval.approvedBy !== "string" || approval.approvedBy.trim().length < 3) {
    throw new Error("Question record " + approval.id + " is missing an approver.");
  }
  const dateParts = (approval.approvedOn ?? "").split("-");
  if (dateParts.length !== 3 || dateParts[0].length !== 4 ||
      dateParts[1].length !== 2 || dateParts[2].length !== 2 ||
      dateParts.some((part) => !/^[0-9]+$/.test(part))) {
    throw new Error("Question record " + approval.id + " needs an ISO approval date.");
  }
  if (typeof approval.rationale !== "string" || approval.rationale.trim().length < 30) {
    throw new Error("Question record " + approval.id + " needs a substantive rationale.");
  }
  if (typeof approval.provenance !== "string" || approval.provenance.trim().length < 30) {
    throw new Error("Question record " + approval.id + " needs decision provenance.");
  }
  for (const language of ["en", "es"]) {
    for (const questionId of ["main", "h2", "h3"]) {
      const text = approval.questions?.[questionId]?.[language];
      if (typeof text !== "string" || text.trim().length < 20) {
        throw new Error("Question record " + approval.id + " is missing " + language + "." + questionId + ".");
      }
    }
  }
}

const activeApproval = control.approvals.at(-1);
if (control.activeApproval !== activeApproval.id) {
  throw new Error("activeApproval must refer to the latest appended approval record.");
}

const baseRefIndex = process.argv.indexOf("--base-ref");
let baseRef = baseRefIndex >= 0 ? process.argv[baseRefIndex + 1] : null;
if (baseRefIndex >= 0 && !baseRef) throw new Error("--base-ref requires a Git ref.");
if (!baseRef) {
  try {
    execFileSync(
      "git",
      ["cat-file", "-e", "HEAD:thesis/question-control.json"],
      { cwd: repositoryRoot, stdio: "ignore" },
    );
    baseRef = "HEAD";
  } catch {
    // The first approval baseline has not yet been committed.
  }
}

if (baseRef) {
  const baseCommit = execFileSync(
    "git",
    ["rev-parse", "--verify", baseRef],
    { cwd: repositoryRoot },
  ).toString("utf8").trim();
  let baselineExists = true;
  try {
    execFileSync(
      "git",
      ["cat-file", "-e", baseCommit + ":thesis/question-control.json"],
      { cwd: repositoryRoot, stdio: "ignore" },
    );
  } catch {
    // Permit the first PR that introduces the approval ledger.
    baselineExists = false;
  }

  if (baselineExists) {
    const baselineText = execFileSync(
      "git",
      ["show", baseCommit + ":thesis/question-control.json"],
      { cwd: repositoryRoot },
    ).toString("utf8");
    const baseline = JSON.parse(baselineText);
    if (control.approvals.length < baseline.approvals.length) {
      throw new Error("Question approval history cannot be shortened.");
    }
    for (let index = 0; index < baseline.approvals.length; index += 1) {
      if (JSON.stringify(control.approvals[index]) !== JSON.stringify(baseline.approvals[index])) {
        throw new Error("Prior question approval records must be preserved; append a new record instead.");
      }
    }
  }
}

const sourceFiles = {
  en: {
    main: "thesis/chapters/02-problem-and-state-of-the-art.tex",
    h2: "thesis/chapters/04-hypotheses.tex",
    h3: "thesis/chapters/04-hypotheses.tex",
  },
  es: {
    main: "thesis/es/chapters/02-problem-and-state-of-the-art.tex",
    h2: "thesis/es/chapters/04-hypotheses.tex",
    h3: "thesis/es/chapters/04-hypotheses.tex",
  },
};

function collapseWhitespace(value) {
  return value.trim().split(/\s+/).join(" ");
}

function extractLockedQuestion(source, questionId, filePath) {
  const beginMarker = "% QUESTION_LOCK:" + questionId + ":BEGIN";
  const endMarker = "% QUESTION_LOCK:" + questionId + ":END";
  const begin = source.indexOf(beginMarker);
  const end = source.indexOf(endMarker);

  if (begin < 0 || end < 0 || end <= begin || source.indexOf(beginMarker, begin + 1) >= 0) {
    throw new Error(filePath + " must contain exactly one complete lock block for " + questionId + ".");
  }

  let question = source.slice(begin + beginMarker.length, end).trim();
  const emphasisPrefix = "\\emph{";
  if (question.startsWith(emphasisPrefix) && question.endsWith("}")) {
    question = question.slice(emphasisPrefix.length, -1).trim();
  }
  return collapseWhitespace(question);
}

for (const language of ["en", "es"]) {
  for (const questionId of ["main", "h2", "h3"]) {
    const relativePath = sourceFiles[language][questionId];
    const source = await readFile(path.join(repositoryRoot, relativePath), "utf8");
    const actual = extractLockedQuestion(source, questionId, relativePath);
    const approved = collapseWhitespace(activeApproval.questions[questionId][language]);

    if (actual !== approved) {
      throw new Error(
        language + "." + questionId + " differs from approved record " + activeApproval.id + ". " +
        "Do not edit a research question silently. Obtain explicit approval, append a dated " +
        "record with its rationale and provenance in thesis/question-control.json, then update the source.",
      );
    }
  }
}

console.log(
  "Research-question guard passed: main, H2 and H3 match " +
  activeApproval.id +
  " in English and Spanish.",
);
