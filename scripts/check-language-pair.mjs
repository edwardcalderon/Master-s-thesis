import { access, readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const rootDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const policy = JSON.parse(await readFile(path.join(rootDir, "language-policy.json"), "utf8"));

function requireCondition(condition, message) {
  if (!condition) throw new Error(message);
}

function macroValue(source, macroName, sourcePath) {
  const pattern = new RegExp("\\\\newcommand\\{\\\\" + macroName + "\\}\\{([^}]+)\\}");
  const match = source.match(pattern);
  requireCondition(match, sourcePath + " is missing \\" + macroName + ".");
  return match[1];
}

function compareShape(primary, translation, sourceLabel, currentPath = "$") {
  const primaryType = Array.isArray(primary) ? "array" : typeof primary;
  const translationType = Array.isArray(translation) ? "array" : typeof translation;
  requireCondition(primaryType === translationType, sourceLabel + " has a mismatched value at " + currentPath + ".");

  if (Array.isArray(primary)) {
    requireCondition(primary.length === translation.length, sourceLabel + " has a different array length at " + currentPath + ".");
    primary.forEach((value, index) => compareShape(value, translation[index], sourceLabel, currentPath + "[" + index + "]"));
    return;
  }

  if (primaryType === "object" && primary !== null && translation !== null) {
    const primaryKeys = Object.keys(primary).sort();
    const translationKeys = Object.keys(translation).sort();
    requireCondition(
      JSON.stringify(primaryKeys) === JSON.stringify(translationKeys),
      sourceLabel + " is missing keys at " + currentPath + "."
    );
    for (const key of primaryKeys) compareShape(primary[key], translation[key], sourceLabel, currentPath + "." + key);
  }
}

async function readJson(relativePath) {
  return JSON.parse(await readFile(path.join(rootDir, relativePath), "utf8"));
}

async function requirePairExists(pair, kind) {
  requireCondition(pair?.en && pair?.es, "Every " + kind + " pair must declare en and es paths.");
  await access(path.join(rootDir, pair.en));
  await access(path.join(rootDir, pair.es));
}

async function checkRelativeMarkdownLinks(sourcePath, markdown) {
  const markdownLink = /\[[^\]]+\]\(([^)]+)\)/g;
  for (const match of markdown.matchAll(markdownLink)) {
    const target = match[1].split(/[?#]/)[0];
    if (!target || /^(?:https?:|mailto:|#)/.test(target)) continue;
    let decodedTarget = target;
    try {
      decodedTarget = decodeURIComponent(target);
    } catch {
      // Keep a literal path when the URL is not percent-encoded correctly.
    }
    try {
      await access(path.resolve(path.dirname(path.join(rootDir, sourcePath)), decodedTarget));
    } catch {
      throw new Error(sourcePath + " contains a broken relative link: " + target + ".");
    }
  }
}

requireCondition(policy.projectPrimary === "en", "The project primary language must be en.");
requireCondition(policy.internalWorkingLanguage === "en", "Internal working files must default to English.");
requireCondition(
  Array.isArray(policy.requiredSecondary) && policy.requiredSecondary.includes("es"),
  "Spanish (es) must be a required secondary language."
);
requireCondition(
  JSON.stringify(policy.requiredBilingualSurfaces) === JSON.stringify(["application", "finalManuscript"]),
  "Only the application UI and final manuscript are required bilingual surfaces."
);

const locales = [policy.projectPrimary, ...policy.requiredSecondary];
requireCondition(policy.application?.defaultLanguage === policy.projectPrimary, "The application must default to the primary language.");
requireCondition(
  JSON.stringify(policy.application?.supportedLanguages) === JSON.stringify(locales),
  "Application languages must match the primary and required secondary languages in policy order."
);
const htmlEntry = await readFile(path.join(rootDir, "apps/web/index.html"), "utf8");
const webAppSource = await readFile(path.join(rootDir, "apps/web/src/App.tsx"), "utf8");
requireCondition(
  htmlEntry.includes(`<html lang="${policy.application.defaultLanguage}">`),
  "The app HTML entry must declare the default application language."
);
requireCondition(
  htmlEntry.includes(
    `<title>${(await readJson(policy.application.translations[policy.projectPrimary].content)).thesis.title}</title>`
  ),
  "The app HTML entry must declare the primary manuscript title before the app loads."
);
requireCondition(
  !/href\s*=\s*"[^"]+\.tex(?:[?#][^"]*)?"/.test(webAppSource),
  "The public web app must not expose direct TeX download links."
);

let primaryContent;
const applicationContentByLocale = Object.create(null);
for (const locale of locales) {
  const translationFiles = policy.application?.translations?.[locale];
  requireCondition(translationFiles, "Application translations are not configured for " + locale + ".");
  const messageData = await readJson(translationFiles.messages);
  const contentData = await readJson(translationFiles.content);
  applicationContentByLocale[locale] = contentData;
  requireCondition(
    messageData.seo.title === contentData.thesis.title,
    locale + " web document title must match its manuscript title."
  );
  if (locale === policy.projectPrimary) {
    primaryContent = contentData;
    continue;
  }

  const primaryFiles = policy.application.translations[policy.projectPrimary];
  compareShape(await readJson(primaryFiles.messages), messageData, "Application messages for " + locale);
  compareShape(await readJson(primaryFiles.content), contentData, "Application content for " + locale);
  requireCondition(
    contentData.thesis.version === primaryContent.thesis.version,
    "English and Spanish app content must declare the same workspace version."
  );

  for (const href of contentData.docs.map((item) => item.href)) {
    await access(path.join(rootDir, href.replace(/^\.\//, "")));
  }
  for (const href of contentData.notebooks.map((item) => item.href)) {
    await access(path.join(rootDir, href.replace(/^\.\//, "")));
  }
}

for (const pair of policy.documentPairs ?? []) {
  await requirePairExists(pair, "document");
  await checkRelativeMarkdownLinks(pair.en, await readFile(path.join(rootDir, pair.en), "utf8"));
  await checkRelativeMarkdownLinks(pair.es, await readFile(path.join(rootDir, pair.es), "utf8"));
  const englishText = await readFile(path.join(rootDir, pair.en), "utf8");
  const spanishText = await readFile(path.join(rootDir, pair.es), "utf8");
  const englishLink = path.relative(path.dirname(pair.en), pair.es).split(path.sep).join("/");
  const spanishLink = path.relative(path.dirname(pair.es), pair.en).split(path.sep).join("/");
  requireCondition(englishText.includes(`](${englishLink})`), pair.en + " must link to its Spanish edition.");
  requireCondition(spanishText.includes(`](${spanishLink})`), pair.es + " must link to its English edition.");
}

for (const pair of policy.jsonPairs ?? []) {
  await requirePairExists(pair, "JSON document");
  const primary = await readJson(pair.en);
  const translation = await readJson(pair.es);
  requireCondition(
    JSON.stringify(primary.map((entry) => [entry.version, entry.date, entry.status])) ===
      JSON.stringify(translation.map((entry) => [entry.version, entry.date, entry.status])),
    pair.es + " must preserve the release versions, dates, statuses, and order from " + pair.en + "."
  );
}

for (const pair of policy.notebookPairs ?? []) {
  await requirePairExists(pair, "notebook");
  const primaryNotebook = await readJson(pair.en);
  const translatedNotebook = await readJson(pair.es);
  requireCondition(
    primaryNotebook.cells.length === translatedNotebook.cells.length,
    pair.es + " must retain the same cell sequence as " + pair.en + "."
  );

  for (const [index, cell] of primaryNotebook.cells.entries()) {
    const translatedCell = translatedNotebook.cells[index];
    requireCondition(cell.cell_type === translatedCell.cell_type, pair.es + " changes cell type at index " + index + ".");
    if (cell.cell_type === "code") {
      requireCondition(
        JSON.stringify(cell.source) === JSON.stringify(translatedCell.source) &&
          JSON.stringify(cell.outputs) === JSON.stringify(translatedCell.outputs),
        pair.es + " must preserve code and outputs from " + pair.en + "."
      );
    } else if (cell.cell_type === "markdown") {
      const primaryText = Array.isArray(cell.source) ? cell.source.join("") : cell.source;
      const translatedText = Array.isArray(translatedCell.source) ? translatedCell.source.join("") : translatedCell.source;
      await checkRelativeMarkdownLinks(pair.en, primaryText);
      await checkRelativeMarkdownLinks(pair.es, translatedText);
    }
  }
}

const editions = new Set();
const versions = new Set();
let expectedInputs;

for (const locale of locales) {
  const manuscript = policy.manuscriptSources?.[locale];
  requireCondition(manuscript, "No manuscript source is configured for " + locale + ".");
  requireCondition(
    manuscript.role === (locale === policy.projectPrimary ? "primary" : "required-translation"),
    "The role for " + locale + " must match its language policy."
  );
  requireCondition(manuscript.pdf.endsWith(".pdf"), "The " + locale + " manuscript output must be a PDF.");

  const sourcePath = path.join(rootDir, manuscript.source);
  const source = await readFile(sourcePath, "utf8");
  const siteThesis = applicationContentByLocale[locale]?.thesis;
  const documentTitle = source.match(/pdftitle=\{([^}]+)\}/)?.[1];
  requireCondition(siteThesis, "No web thesis content is configured for " + locale + ".");
  requireCondition(
    siteThesis.title === documentTitle,
    locale + " web heading must match the title embedded in " + manuscript.source + "."
  );
  const languageCode = macroValue(source, "languageCode", manuscript.source);
  const edition = macroValue(source, "revisionManuscrito", manuscript.source);
  const version = macroValue(source, "versionTesis", manuscript.source);

  requireCondition(
    languageCode === locale,
    manuscript.source + " declares " + languageCode + "; expected " + locale + "."
  );
  editions.add(edition);
  versions.add(version);

  const inputs = [...source.matchAll(/\\input\{([^}]+)\}/g)]
    .map((match) => match[1])
    .filter((inputPath) => inputPath.startsWith("chapters/"));
  requireCondition(inputs.length > 0, manuscript.source + " must input chapter sources.");

  const abstractInput = inputs.find((inputPath) => /(?:^|\/)00-abstract$/.test(inputPath));
  requireCondition(abstractInput, manuscript.source + " must include its abstract chapter.");
  const abstractPath = path.resolve(path.dirname(sourcePath), abstractInput + ".tex");
  const abstractSource = await readFile(abstractPath, "utf8");
  const abstractHeading = locale === "en" ? "Abstract" : "Resumen";
  const headingMarker = `\\section{${abstractHeading}}`;
  const keywordMarker = locale === "en" ? "\\textbf{Keywords:}" : "\\textbf{Palabras clave:}";
  const abstractStart = abstractSource.indexOf(headingMarker);
  const paragraphStart = abstractStart + headingMarker.length;
  const keywordStart = abstractSource.indexOf(keywordMarker, paragraphStart);
  const webAbstract = siteThesis.abstract;
  requireCondition(abstractStart >= 0, abstractPath + " is missing its " + abstractHeading + " section.");
  requireCondition(keywordStart > paragraphStart, abstractPath + " is missing its keyword section.");
  const sourceParagraphs = abstractSource.slice(paragraphStart, keywordStart)
    .trim()
    .split(/\n\s*\n/)
    .map((paragraph) => paragraph.replace(/\s+/g, " ").trim())
    .filter(Boolean);
  const sourceKeywords = abstractSource.slice(keywordStart + keywordMarker.length)
    .trim()
    .replace(/\.$/, "")
    .split(";")
    .map((keyword) => keyword.trim());
  requireCondition(
    webAbstract?.heading === abstractHeading && JSON.stringify(webAbstract.paragraphs) === JSON.stringify(sourceParagraphs),
    locale + " web abstract must match the text in " + abstractPath + "."
  );
  requireCondition(
    JSON.stringify(webAbstract.keywords) === JSON.stringify(sourceKeywords),
    locale + " web abstract keywords must match the text in " + abstractPath + "."
  );

  for (const inputPath of inputs) {
    await access(path.resolve(path.dirname(sourcePath), inputPath + ".tex"));
  }

  if (expectedInputs === undefined) expectedInputs = inputs;
  else {
    requireCondition(
      JSON.stringify(inputs) === JSON.stringify(expectedInputs),
      manuscript.source + " must include the same chapter sequence as the primary manuscript."
    );
  }

  await access(path.join(rootDir, path.dirname(manuscript.pdf)));
}

requireCondition(editions.size === 1, "English and Spanish sources must share one manuscript revision.");
requireCondition(versions.size === 1, "English and Spanish sources must share one workspace release version.");

console.log(
  "Language policy verified: bilingual application UI and final thesis; " +
    policy.projectPrimary +
    " primary; " +
    policy.requiredSecondary.join(", ") +
    " required; manuscript " +
    [...editions][0] +
    "."
);
