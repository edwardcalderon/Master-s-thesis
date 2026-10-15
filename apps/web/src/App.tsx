import { useEffect, useState, type ReactNode } from "react";
import { docs, layers, notebooks, release, thesis } from "@tesis/content";

type IconName = "arrow" | "book" | "check" | "code" | "download" | "external" | "file" | "github" | "moon" | "play" | "sun";
type Theme = "light" | "dark";

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

function initialTheme(): Theme {
  if (typeof window === "undefined") return "light";
  const savedTheme = window.localStorage.getItem("thesis-theme");
  if (savedTheme === "light" || savedTheme === "dark") return savedTheme;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function App() {
  const [pdfOpen, setPdfOpen] = useState(false);
  const [pdfAvailable, setPdfAvailable] = useState(false);
  const [copied, setCopied] = useState(false);
  const [theme, setTheme] = useState<Theme>(initialTheme);
  const [readingMode, setReadingMode] = useState(() => typeof window !== "undefined" && window.localStorage.getItem("thesis-reading-mode") === "on");

  useEffect(() => {
    fetch("./thesis/master-thesis.pdf", { method: "HEAD" })
      .then((response) => setPdfAvailable(response.ok))
      .catch(() => setPdfAvailable(false));
  }, []);

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
  const readingLabel = readingMode ? "Exit reading mode" : "Enter reading mode";

  return <div className="site-shell" data-theme={theme} data-reading={readingMode ? "on" : "off"}>
    <header className="topbar page-pad">
      <a className="brand" href="#top" aria-label="Master Thesis Lab home">
        <span className="brand-mark">MT</span>
        <span className="brand-copy"><strong>Master Thesis</strong><small>research edition · {release.tag}</small></span>
      </a>
      <nav className="topnav" aria-label="Primary navigation">
        <a href="#research">Overview</a>
        <a href="#notebooks">Notebooks</a>
        <a href="#docs">Notes</a>
        <a href="#pdf">Manuscript</a>
      </nav>
      <div className="header-actions">
        <button className="utility-button" type="button" onClick={() => setReadingMode((value) => !value)} aria-pressed={readingMode} title={readingLabel}>
          <Icon name="book" size={16} /><span>{readingMode ? "Reading on" : "Reading"}</span>
        </button>
        <button className="theme-button" type="button" onClick={() => setTheme(nextTheme)} aria-label={`Use ${nextTheme} theme`} title={`Use ${nextTheme} theme`}>
          <Icon name={theme === "light" ? "moon" : "sun"} size={17} />
        </button>
        <a className="repository-link" href="https://github.com/edwardcalderon/Master-s-thesis" target="_blank" rel="noreferrer" aria-label="Open repository"><Icon name="github" size={17} /></a>
      </div>
    </header>

    <main id="top">
      <section className="hero page-pad">
        <div className="hero-copy">
          <p className="hero-kicker"><span className="status-dot" />{thesis.eyebrow}</p>
          <h1>{thesis.title}</h1>
          <p className="hero-lede">{thesis.description}</p>
          <div className="hero-actions">
            <a className="button button-primary" href="#research">Begin with the overview <Icon name="arrow" size={16} /></a>
            <a className="button button-quiet" href="#pdf">Read the manuscript <Icon name="book" size={16} /></a>
          </div>
        </div>
        <aside className="hero-note" aria-label="Thesis record">
          <p className="note-heading">Thesis record</p>
          <dl>
            <div><dt>Version</dt><dd className="mono">{release.tag}</dd></div>
            <div><dt>Status</dt><dd>{thesis.state}</dd></div>
            <div><dt>Method</dt><dd>Simulation &amp; reproducible evidence</dd></div>
            <div><dt>Access</dt><dd>Public research workspace</dd></div>
          </dl>
          <a className="quiet-link" href={release.trackerUrl} target="_blank" rel="noreferrer">View release record <Icon name="external" size={14} /></a>
        </aside>
      </section>

      <section className="manifest-strip page-pad" aria-label="Project manifest">
        <div className="manifest-item"><span>Research state</span><strong><i className="status-dot" />{thesis.state}</strong></div>
        <div className="manifest-item"><span>Current version</span><strong className="mono">{release.tag}</strong></div>
        <div className="manifest-item"><span>Research layers</span><strong className="mono">03 / 03</strong></div>
        <div className="manifest-item"><span>License</span><strong>{thesis.license}</strong></div>
      </section>

      <section id="research" className="research-section page-pad">
        <SectionHeading index="01" kicker="Research overview" title="Start with the question.">The repository follows the way a thesis is examined: question, method, evidence, and argument—each available as a separate, inspectable artifact.</SectionHeading>
        <div className="research-grid">
          <article className="research-card">
            <Label>01 · Narrative</Label>
            <h3>Research brief</h3>
            <p>Context, research question, contribution, and the boundaries of the present version.</p>
            <ArrowLink href="#docs">Read the brief</ArrowLink>
          </article>
          <article className="research-card">
            <Label>02 · Evidence</Label>
            <h3>Executable evidence</h3>
            <p>Notebooks turn an analytical claim into traceable inputs, assumptions, and outputs.</p>
            <ArrowLink href="#notebooks">Open notebooks</ArrowLink>
          </article>
          <article className="research-card">
            <Label>03 · Manuscript</Label>
            <h3>Thesis artifact</h3>
            <p>LaTeX source, compiled PDF, release record, and methods remain connected.</p>
            <ArrowLink href="#pdf">Open the manuscript</ArrowLink>
          </article>
        </div>
      </section>

      <section id="notebooks" className="notebooks-section page-pad">
        <SectionHeading index="02" kicker="Notebook explorer" title="Evidence that can be revisited.">Each notebook has one purpose, a readable scope, and a route back to the chapter it informs.</SectionHeading>
        <div className="notebook-toolbar"><span className="mono">NOTEBOOKS / {String(notebooks.length).padStart(2, "0")}</span><a className="quiet-link" href="https://github.com/edwardcalderon/Master-s-thesis/tree/main/notebooks" target="_blank" rel="noreferrer">Browse source <Icon name="external" size={14} /></a></div>
        <div className="notebook-list">
          {notebooks.map((notebook) => <article className="notebook-row" key={notebook.id}>
            <span className="notebook-index">{notebook.id}</span>
            <div className="notebook-main"><div className="notebook-title-line"><h3>{notebook.title}</h3><Label>{notebook.status}</Label></div><p>{notebook.description}</p><div className="notebook-meta"><span>{notebook.kind}</span><span>{notebook.runtime}</span></div></div>
            <a className="notebook-open" href={notebook.href} aria-label={`Open ${notebook.title}`}><Icon name="arrow" size={16} /></a>
          </article>)}
        </div>
      </section>

      <section id="docs" className="docs-section page-pad">
        <SectionHeading index="03" kicker="Documentation" title="Notes around the result.">The surrounding documentation names assumptions, explains the reproduction path, and records the current limits of the work.</SectionHeading>
        <div className="docs-layout">
          <div className="docs-list">
            {docs.map((doc, index) => <a className="doc-row" href={doc.href} key={doc.label}><span className="doc-index">{String(index + 1).padStart(2, "0")}</span><span className="doc-label"><strong>{doc.label}</strong><small>{doc.meta}</small></span><Icon name="arrow" size={16} /></a>)}
          </div>
          <aside className="architecture-card">
            <p className="note-heading">Repository map</p>
            <div className="tree-line tree-root"><span>master-thesis</span><small>research workspace</small></div>
            <div className="tree-line"><strong>apps/web</strong><small>public reading surface</small></div>
            <div className="tree-line"><strong>packages/content</strong><small>versioned metadata</small></div>
            <div className="tree-line"><strong>notebooks</strong><small>executable evidence</small></div>
            <div className="tree-line"><strong>thesis</strong><small>LaTeX manuscript</small></div>
            <div className="tree-line"><strong>docs</strong><small>methods and protocol</small></div>
          </aside>
        </div>
        <div className="layer-ribbon">{layers.map((layer) => <div className="layer" key={layer.index}><span className="mono">{layer.index}</span><strong>{layer.label}</strong><small>{layer.detail}</small></div>)}</div>
      </section>

      <section id="pdf" className="pdf-section page-pad">
        <div className="pdf-copy">
          <p className="eyebrow">04 · Manuscript</p>
          <h2>Read the thesis in context.</h2>
          <p>The public manuscript is published with its source and release record. The viewer appears here when the PDF artifact is available.</p>
          <div className="pdf-actions"><button className="button button-primary" type="button" onClick={() => setPdfOpen((value) => !value)}><Icon name="book" size={16} />{pdfOpen ? "Close viewer" : "Open viewer"}</button><a className="button button-quiet" href="./thesis/main.tex" download><Icon name="download" size={16} /> LaTeX source</a></div>
          <p className="pdf-meta"><span className="mono">THESIS / {release.tag}</span><span>{pdfAvailable ? "PDF artifact available" : "PDF artifact pending build"}</span></p>
        </div>
        <div className={`pdf-frame${pdfOpen ? " pdf-frame-open" : ""}`}>
          <div className="pdf-window-bar"><span className="mono">master-thesis.pdf</span><span>{pdfOpen ? "reader" : "source ready"}</span></div>
          <div className={`pdf-page${pdfAvailable && pdfOpen ? " pdf-page-live" : ""}`}>
            {pdfAvailable && pdfOpen ? <iframe className="pdf-embed" src="./thesis/master-thesis.pdf#view=FitH" title="Compiled master thesis" /> : <><p className="pdf-page-label">MASTER THESIS · {release.tag}</p><h3>A reproducible research object</h3><p>{pdfOpen ? "The compiled thesis will appear here once the approved PDF is built and published with the site." : "Open the viewer to inspect the published manuscript when it is available."}</p><span className="pdf-page-number">01</span></>}
          </div>
        </div>
      </section>

      <section className="closing-section page-pad">
        <div><p className="eyebrow">A living record</p><h2>Question first. Evidence next.</h2><p>Clone the workspace, inspect the assumptions, and follow the artifact trail.</p></div>
        <div className="clone-card"><span className="mono">Repository</span><code>git clone .../Master-s-thesis.git</code><button type="button" onClick={copyCloneCommand}>{copied ? <><Icon name="check" size={15} />Copied</> : <><Icon name="code" size={15} />Copy clone command</>}</button></div>
      </section>
    </main>

    <footer className="footer page-pad"><span>© {new Date().getFullYear()} Master Thesis Lab</span><span>Open research · reproducible by default</span><div className="footer-links"><a href={release.trackerUrl} target="_blank" rel="noreferrer"><span className="mono">{release.tag}</span> Release record <Icon name="external" size={14} /></a><a href="https://github.com/edwardcalderon/Master-s-thesis" target="_blank" rel="noreferrer">Repository <Icon name="external" size={14} /></a></div></footer>
  </div>;
}

export default App;
