import { useEffect, useState, type ReactNode } from "react";
import { contentByLocale, release, type Locale } from "@tesis/content";
import englishMessages from "./locales/en.json";
import spanishMessages from "./locales/es.json";
import Playground from "./features/playground/Playground";

type IconName = "arrow" | "book" | "check" | "code" | "download" | "external" | "file" | "github" | "moon" | "play" | "sun";
type Theme = "light" | "dark";

const messages = { en: englishMessages, es: spanishMessages } satisfies Record<Locale, typeof englishMessages>;

function Icon({ name, size = 18 }: { name: IconName; size?: number }) {
  const common = { width: size, height: size, viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: 1.7, strokeLinecap: "round" as const, strokeLinejoin: "round" as const, "aria-hidden": true };
  const paths: Record<IconName, ReactNode> = {
    arrow: <><path d="M5 12h13" /><path d="m13 6 6 6-6 6" /></>,
    book: <><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v16H6.5A2.5 2.5 0 0 0 4 21.5z" /><path d="M4 5.5v16" /><path d="M8 7h8" /><path d="M8 11h6" /></>,
    check: <path d="m5 12 4 4L19 6" />,
    code: <><path d="m8 9-4 3 4 3" /><path d="m16 9 4 3-4 3" /><path d="m14 5-4 14" /></>,
    download: <><path d="M12 3v12" /><path d="m7 10 5 5 5-5" /><path d="M4 20h16" /></>,
    external: <><path d="M14 4h6v6" /><path d="M20 4 11 13" /><path d="M18 13v6H5V6h6" /></>,
    file: <><path d="M6 3h8l4 4v14H6z" /><path d="M14 3v5h5" /><path d="M9 13h6" /><path d="M9 17h6" /></>,
    github: <><path d="M15 22v-3.5c.05-1.3-.45-2.1-1-2.5 3.3-.35 6.75-1.6 6.75-7.15a5.6 5.6 0 0 0-1.5-3.9A5.2 5.2 0 0 0 19.1 2S17.85 1.6 15 3.55a13.2 13.2 0 0 0-6 0C6.15 1.6 4.9 2 4.9 2a5.2 5.2 0 0 0-1.15 4.95 5.6 5.6 0 0 0-1.5 3.9c0 5.55 3.45 6.8 6.75 7.15-.55.4-1.05 1.2-1.05 2.5V22" /><path d="M7 18c-3 .9-3-1.5-4.5-1.8" /></>,
    moon: <path d="M20.5 14.2A8.5 8.5 0 0 1 9.8 3.5 8.5 8.5 0 1 0 20.5 14.2Z" />,
    play: <path d="m8 5 11 7-11 7z" />,
    sun: <><circle cx="12" cy="12" r="3.5" /><path d="M12 2v2.2M12 19.8V22M4.93 4.93l1.56 1.56M17.5 17.5l1.57 1.57M2 12h2.2M19.8 12H22M4.93 19.07l1.56-1.56M17.5 6.5l1.57-1.57" /></>
  };
  return <svg {...common}>{paths[name]}</svg>;
}

function Label({ children }: { children: ReactNode }) {
  return <span className="label">{children}</span>;
}

function ArrowLink({ children, href }: { children: ReactNode; href: string }) {
  return <a className="arrow-link" href={href}>{children}<Icon name="arrow" size={15} /></a>;
}

function SectionHeading({ index, kicker, title, children }: { index: string; kicker: string; title: string; children?: ReactNode }) {
  return <div className="section-heading">
    <span className="section-index">{index}</span>
    <div>
      <p className="eyebrow">{kicker}</p>
      <h2>{title}</h2>
      {children && <p className="section-intro">{children}</p>}
    </div>
  </div>;
}

function initialLocale(): Locale {
  if (typeof window === "undefined") return "en";
  return window.localStorage.getItem("thesis-language") === "es" ? "es" : "en";
}

function initialTheme(): Theme {
  if (typeof window === "undefined") return "light";
  const savedTheme = window.localStorage.getItem("thesis-theme");
  if (savedTheme === "light" || savedTheme === "dark") return savedTheme;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function App() {
  const [locale, setLocale] = useState<Locale>(initialLocale);
  const copy = messages[locale];
  const content = contentByLocale[locale];
  const [pdfOpen, setPdfOpen] = useState(false);
  const [pdfAvailable, setPdfAvailable] = useState(false);
  const [pdfSpanishAvailable, setPdfSpanishAvailable] = useState(false);
  const [pdfLanguage, setPdfLanguage] = useState<Locale>("en");
  const [copied, setCopied] = useState(false);
  const [theme, setTheme] = useState<Theme>(initialTheme);
  const [readingMode, setReadingMode] = useState(() => typeof window !== "undefined" && window.localStorage.getItem("thesis-reading-mode") === "on");

  useEffect(() => {
    fetch("./thesis/master-thesis.pdf", { method: "HEAD" })
      .then((response) => setPdfAvailable(response.ok))
      .catch(() => setPdfAvailable(false));
    fetch("./thesis/master-thesis.es.pdf", { method: "HEAD" })
      .then((response) => setPdfSpanishAvailable(response.ok))
      .catch(() => setPdfSpanishAvailable(false));
  }, []);

  useEffect(() => {
    window.localStorage.setItem("thesis-language", locale);
    document.documentElement.lang = locale;
    document.title = copy.seo.title;
    document.querySelector('meta[name="description"]')?.setAttribute("content", copy.seo.description);
  }, [copy.seo.description, copy.seo.title, locale]);

  useEffect(() => {
    window.localStorage.setItem("thesis-theme", theme);
    document.documentElement.style.colorScheme = theme;
    document.querySelector('meta[name="theme-color"]')?.setAttribute("content", theme === "dark" ? "#191b1a" : "#f7f5ef");
  }, [theme]);

  useEffect(() => {
    window.localStorage.setItem("thesis-reading-mode", readingMode ? "on" : "off");
  }, [readingMode]);

  const copyCloneCommand = async () => {
    await navigator.clipboard?.writeText("git clone https://github.com/edwardcalderon/Master-s-thesis.git");
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1800);
  };

  const nextTheme = theme === "light" ? "dark" : "light";
  const readingLabel = readingMode ? copy.header.exitReading : copy.header.enterReading;
  const selectedPdfAvailable = pdfLanguage === "en" ? pdfAvailable : pdfSpanishAvailable;
  const selectedPdfUrl = pdfLanguage === "en" ? "./thesis/master-thesis.pdf" : "./thesis/master-thesis.es.pdf";
  const pdfStatus = pdfAvailable && pdfSpanishAvailable
    ? copy.pdf.available
    : pdfAvailable
      ? copy.pdf.missing
      : copy.pdf.pending;
  const openNotebookLabel = (title: string) => `${copy.notebook.open}: ${title}`;

  return <div className="site-shell" data-theme={theme} data-reading={readingMode ? "on" : "off"}>
    <header className="topbar page-pad">
      <a className="brand" href="#top" aria-label={copy.header.home}>
        <span className="brand-mark">MT</span>
        <span className="brand-copy"><strong>{content.thesis.shortTitle}</strong><small>{copy.header.subtitle} · {release.tag}</small></span>
      </a>
      <nav className="topnav" aria-label={copy.header.navigation}>
        <a href="#research">{copy.header.overview}</a>
        <a href="#lab">{copy.header.lab}</a>
        <a href="#abstract">{copy.header.abstract}</a>
        <a href="#notebooks">{copy.header.notebooks}</a>
        <a href="#docs">{copy.header.notes}</a>
        <a href="#pdf">{copy.header.manuscript}</a>
      </nav>
      <div className="header-actions">
        <div className="locale-switch" role="group" aria-label={copy.language.label}>
          <button className={locale === "en" ? "locale-option is-selected" : "locale-option"} type="button" onClick={() => setLocale("en")} aria-pressed={locale === "en"} lang="en">{copy.language.english}</button>
          <button className={locale === "es" ? "locale-option is-selected" : "locale-option"} type="button" onClick={() => setLocale("es")} aria-pressed={locale === "es"} lang="es">{copy.language.spanish}</button>
        </div>
        <button className="utility-button" type="button" onClick={() => setReadingMode((value) => !value)} aria-pressed={readingMode} title={readingLabel}>
          <Icon name="book" size={16} /><span>{readingMode ? copy.header.readingOn : copy.header.reading}</span>
        </button>
        <button className="theme-button" type="button" onClick={() => setTheme(nextTheme)} aria-label={theme === "light" ? copy.header.useDark : copy.header.useLight} title={theme === "light" ? copy.header.useDark : copy.header.useLight}>
          <Icon name={theme === "light" ? "moon" : "sun"} size={17} />
        </button>
        <a className="repository-link" href="https://github.com/edwardcalderon/Master-s-thesis" target="_blank" rel="noreferrer" aria-label={copy.header.openRepository}><Icon name="github" size={17} /></a>
      </div>
    </header>

    <main id="top">
      <section className="hero hero-compact page-pad">
        <div className="hero-copy">
          <p className="hero-kicker"><span className="status-dot" />{content.thesis.eyebrow}</p>
          <h1>{content.thesis.title}</h1>
          <div className="hero-actions">
            <a className="button button-primary" href="#lab">{copy.hero.begin} <Icon name="play" size={15} /></a>
            <a className="button button-quiet" href="#pdf">{copy.hero.read} <Icon name="book" size={16} /></a>
          </div>
        </div>
      </section>

      <Playground locale={locale} copy={copy.playground} />

      <section id="abstract" className="abstract-section page-pad">
        <SectionHeading index="02" kicker={copy.abstract.kicker} title={content.thesis.abstract.heading} />
        <div className="abstract-copy">
          {content.thesis.abstract.paragraphs.map((paragraph, index) => <p key={index}>{paragraph}</p>)}
          <p className="abstract-keywords"><span className="mono">{copy.abstract.keywords}:</span> {content.thesis.abstract.keywords.join("; ")}</p>
        </div>
      </section>

      <section id="research" className="research-section page-pad">
        <SectionHeading index="03" kicker={copy.research.kicker} title={copy.research.title}>{copy.research.intro}</SectionHeading>
        <div className="research-grid">
          <article className="research-card">
            <Label>{copy.research.narrative}</Label>
            <h3>{copy.research.brief}</h3>
            <p>{copy.research.briefText}</p>
            <ArrowLink href="#docs">{copy.research.readBrief}</ArrowLink>
          </article>
          <article className="research-card">
            <Label>{copy.research.evidence}</Label>
            <h3>{copy.research.executable}</h3>
            <p>{copy.research.evidenceText}</p>
            <ArrowLink href="#notebooks">{copy.research.openNotebooks}</ArrowLink>
          </article>
          <article className="research-card">
            <Label>{copy.research.artifact}</Label>
            <h3>{copy.research.thesisArtifact}</h3>
            <p>{copy.research.artifactText}</p>
            <ArrowLink href="#pdf">{copy.research.openManuscript}</ArrowLink>
          </article>
        </div>
      </section>

      <section id="notebooks" className="notebooks-section page-pad">
        <SectionHeading index="04" kicker={copy.notebook.kicker} title={copy.notebook.title}>{copy.notebook.intro}</SectionHeading>
        <div className="notebook-toolbar"><span className="mono">{copy.notebook.count} {String(content.notebooks.length).padStart(2, "0")}</span><a className="quiet-link" href="https://github.com/edwardcalderon/Master-s-thesis/tree/main/notebooks" target="_blank" rel="noreferrer">{copy.notebook.browse} <Icon name="external" size={14} /></a></div>
        <div className="notebook-list">
          {content.notebooks.map((notebook) => <article className="notebook-row" key={notebook.id}>
            <span className="notebook-index">{notebook.id}</span>
            <div className="notebook-main"><div className="notebook-title-line"><h3>{notebook.title}</h3><Label>{notebook.status}</Label></div><p>{notebook.description}</p><div className="notebook-meta"><span>{notebook.kind}</span><span>{notebook.runtime}</span></div></div>
            <a className="notebook-open" href={notebook.href} aria-label={openNotebookLabel(notebook.title)}><Icon name="arrow" size={16} /></a>
          </article>)}
        </div>
      </section>

      <section id="docs" className="docs-section page-pad">
        <SectionHeading index="05" kicker={copy.docs.kicker} title={copy.docs.title}>{copy.docs.intro}</SectionHeading>
        <div className="docs-layout">
          <div className="docs-list">
            {content.docs.map((doc, index) => <a className="doc-row" href={doc.href} key={doc.label}><span className="doc-index">{String(index + 1).padStart(2, "0")}</span><span className="doc-label"><strong>{doc.label}</strong><small>{doc.meta}</small></span><Icon name="arrow" size={16} /></a>)}
          </div>
          <aside className="architecture-card">
            <p className="note-heading">{copy.docs.map}</p>
            <div className="tree-line tree-root"><span>master-thesis</span><small>{copy.docs.workspace}</small></div>
            <div className="tree-line"><strong>apps/web</strong><small>{copy.docs.web}</small></div>
            <div className="tree-line"><strong>packages/content</strong><small>{copy.docs.content}</small></div>
            <div className="tree-line"><strong>notebooks</strong><small>{copy.docs.notebooks}</small></div>
            <div className="tree-line"><strong>thesis</strong><small>{copy.docs.thesis}</small></div>
            <div className="tree-line"><strong>docs</strong><small>{copy.docs.docs}</small></div>
          </aside>
        </div>
        <div className="layer-ribbon">{content.layers.map((layer) => <div className="layer" key={layer.index}><span className="mono">{layer.index}</span><strong>{layer.label}</strong><small>{layer.detail}</small></div>)}</div>
      </section>

      <section id="pdf" className="pdf-section page-pad">
        <div className="pdf-copy">
          <p className="eyebrow">{copy.pdf.kicker}</p>
          <h2>{copy.pdf.title}</h2>
          <p>{copy.pdf.intro}</p>
          <div className="pdf-language-switch" role="group" aria-label={copy.pdf.languageGroup}>
            <button className={pdfLanguage === "en" ? "language-option is-selected" : "language-option"} type="button" onClick={() => setPdfLanguage("en")} aria-pressed={pdfLanguage === "en"} disabled={!pdfAvailable} title={pdfAvailable ? copy.pdf.primary : copy.pdf.downloadUnavailable}>{copy.pdf.primary}</button>
            <button className={pdfLanguage === "es" ? "language-option is-selected" : "language-option"} type="button" onClick={() => setPdfLanguage("es")} aria-pressed={pdfLanguage === "es"} disabled={!pdfSpanishAvailable} title={pdfSpanishAvailable ? copy.pdf.openSpanish : copy.pdf.missingSpanish}>{copy.pdf.translation}</button>
          </div>
          <div className="pdf-actions">
            <button className="button button-primary" type="button" onClick={() => setPdfOpen((value) => !value)}><Icon name="book" size={16} />{pdfOpen ? copy.pdf.closeViewer : copy.pdf.openViewer}</button>
            <a className="button button-quiet" href={pdfAvailable ? "./thesis/master-thesis.pdf" : undefined} aria-disabled={!pdfAvailable} title={pdfAvailable ? copy.pdf.englishPdf : copy.pdf.downloadUnavailable} onClick={(event) => { if (!pdfAvailable) event.preventDefault(); }} download><Icon name="download" size={16} /> {copy.pdf.englishPdf}</a>
            <a className="button button-quiet" href={pdfSpanishAvailable ? "./thesis/master-thesis.es.pdf" : undefined} aria-disabled={!pdfSpanishAvailable} title={pdfSpanishAvailable ? copy.pdf.translation : copy.pdf.missingSpanish} onClick={(event) => { if (!pdfSpanishAvailable) event.preventDefault(); }} download><Icon name="download" size={16} /> {copy.pdf.spanishPdf}</a>
          </div>
          <p className="pdf-meta"><span className="mono">{copy.pdf.artifactLabel} / {release.tag}</span><span>{pdfStatus}</span></p>
        </div>
        <div className={"pdf-frame" + (pdfOpen ? " pdf-frame-open" : "")}>
          <div className="pdf-window-bar"><span className="mono">{pdfLanguage === "en" ? "master-thesis.pdf · EN" : "master-thesis.es.pdf · ES"}</span><span>{pdfOpen ? copy.pdf.reader : copy.pdf.pdfReady}</span></div>
          <div className={"pdf-page" + (selectedPdfAvailable && pdfOpen ? " pdf-page-live" : "")}>
            {selectedPdfAvailable && pdfOpen ? <iframe className="pdf-embed" src={selectedPdfUrl + "#view=FitH"} title={pdfLanguage === "en" ? copy.pdf.englishPdfTitle : copy.pdf.spanishPdfTitle} /> : <><p className="pdf-page-label">{copy.pdf.pageLabel} · {release.tag}</p><h3>{content.thesis.title}</h3><p>{pdfOpen ? (pdfLanguage === "es" ? copy.pdf.spanishPending : copy.pdf.englishPending) : copy.pdf.closedHint}</p><span className="pdf-page-number">01</span></>}
          </div>
        </div>
      </section>

      <section className="closing-section page-pad">
        <div><p className="eyebrow">{copy.closing.eyebrow}</p><h2>{copy.closing.title}</h2><p>{copy.closing.text}</p></div>
        <div className="clone-card"><span className="mono">{copy.closing.repository}</span><code>git clone .../Master-s-thesis.git</code><button type="button" onClick={copyCloneCommand}>{copied ? <><Icon name="check" size={15} />{copy.closing.copied}</> : <><Icon name="code" size={15} />{copy.closing.copyCommand}</>}</button></div>
      </section>
    </main>

    <footer className="footer page-pad"><span>© {new Date().getFullYear()} {copy.footer.copyright}</span><span>{copy.footer.tagline}</span><div className="footer-links"><a href={release.trackerUrl} target="_blank" rel="noreferrer"><span className="mono">{release.tag}</span> {copy.footer.release} <Icon name="external" size={14} /></a><a href="https://github.com/edwardcalderon/Master-s-thesis" target="_blank" rel="noreferrer">{copy.footer.repository} <Icon name="external" size={14} /></a></div></footer>
  </div>;
}

export default App;
