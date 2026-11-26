import { useCallback, useEffect, useMemo, useState } from "react";
import type { Locale } from "@tesis/content";

type Snapshot = {
  model_version: string;
  synthetic: boolean;
  updated_at?: string;
  tick: number;
  cex_price: number;
  dex_price: number;
  log_error: number;
  no_arbitrage_band_log: number;
  capacity_fraction: number;
  last_event?: string;
};

type Point = Pick<Snapshot, "tick" | "cex_price" | "dex_price">;
type ExperimentResult = {
  run_id: string;
  model_version: string;
  seed_count: number;
  horizon_ticks: number;
  scenarios: Record<string, {
    maximum_absolute_log_error: { mean: number; p05: number; p95: number };
    cumulative_excess_error: { mean: number; p05: number; p95: number };
    return_to_band_rate: number;
  }>;
  trajectory: Array<Record<string, number> & { tick: number }>;
  limitations: string;
};

const SNAPSHOT_URL = "https://raw.githubusercontent.com/edwardcalderon/Master-s-thesis/microworld-data/snapshot.json";
const HISTORY_URL = "https://raw.githubusercontent.com/edwardcalderon/Master-s-thesis/microworld-data/history.json";
const API_URL = (import.meta.env.VITE_MICROWORLD_API_URL as string | undefined)?.trim().replace(/\/$/, "");

const words = {
  en: {
    kicker: "Shared world · synthetic", title: "Microworld telemetry", intro: "A periodically advanced model state, refreshed from the public snapshot when available.",
    live: "Fresh snapshot", stale: "Snapshot is stale", offline: "Feed unavailable", loading: "Connecting to shared state…", local: "Browser model stays available below.",
    tick: "World tick", cex: "CEX reference", dex: "DEX pool", error: "Log-price error", updated: "Last update", event: "Latest event", noEvent: "No trade", history: "Recent shared trajectory", noHistory: "No shared history yet. The local simulator below is ready.", model: "Model", synthetic: "Synthetic · not a thesis finding",
    enhanced: "Explore with paired seeds", enhancedIntro: "Bounded exploratory run on the reference ABM. Uses matched random schedules for static and adaptive liquidity-provider conditions.",
    seedCount: "Paired seeds", horizon: "Ticks per seed", shock: "CEX log shock", capacity: "Arbitrage capacity", run: "Start exploratory run", unavailable: "Enhanced runner unavailable", unavailableHelp: "This optional endpoint is not configured. Core scenarios and the live snapshot remain usable.",
    queued: "Run queued", running: "Waiting for isolated result…", result: "Exploratory result", failed: "Run unavailable", static: "Static LP", adaptive: "Adaptive LP", peak: "Mean peak absolute error", excess: "Mean cumulative excess error", returnRate: "Return-to-band rate", seeds: "seeds", ticks: "ticks", scope: "Exploratory only · not frozen evidence"
  },
  es: {
    kicker: "Micromundo compartido · sintético", title: "Telemetría del micromundo", intro: "Estado del modelo actualizado periódicamente; se lee la instantánea pública cuando está disponible.",
    live: "Instantánea reciente", stale: "Instantánea desactualizada", offline: "Fuente no disponible", loading: "Conectando con el estado compartido…", local: "El modelo del navegador sigue disponible abajo.",
    tick: "Tick del mundo", cex: "Referencia CEX", dex: "Pool DEX", error: "Error logarítmico", updated: "Última actualización", event: "Evento reciente", noEvent: "Sin operación", history: "Trayectoria compartida reciente", noHistory: "Aún no hay historial compartido. El simulador local está disponible abajo.", model: "Modelo", synthetic: "Sintético · no es un hallazgo de tesis",
    enhanced: "Explorar con semillas pareadas", enhancedIntro: "Ejecución exploratoria acotada del ABM de referencia. Empareja los calendarios aleatorios entre condiciones de LP estático y adaptativo.",
    seedCount: "Semillas pareadas", horizon: "Ticks por semilla", shock: "Choque logarítmico CEX", capacity: "Capacidad de arbitraje", run: "Iniciar ejecución exploratoria", unavailable: "Ejecución avanzada no disponible", unavailableHelp: "El endpoint opcional no está configurado. Los escenarios locales y la instantánea siguen disponibles.",
    queued: "Ejecución en cola", running: "Esperando el resultado aislado…", result: "Resultado exploratorio", failed: "Ejecución no disponible", static: "LP estático", adaptive: "LP adaptativo", peak: "Error absoluto máximo medio", excess: "Exceso acumulado medio", returnRate: "Tasa de retorno a banda", seeds: "semillas", ticks: "ticks", scope: "Solo exploratorio · no es evidencia confirmatoria"
  }
} as const;

function number(value: number, locale: Locale, digits = 4) {
  return new Intl.NumberFormat(locale === "es" ? "es-ES" : "en-US", { maximumFractionDigits: digits }).format(value);
}

function validSnapshot(value: unknown): value is Snapshot {
  if (!value || typeof value !== "object") return false;
  const item = value as Partial<Snapshot>;
  return typeof item.model_version === "string" && typeof item.synthetic === "boolean"
    && Number.isFinite(item.tick) && Number.isFinite(item.cex_price) && Number.isFinite(item.dex_price)
    && Number.isFinite(item.log_error) && Number.isFinite(item.no_arbitrage_band_log)
    && Number.isFinite(item.capacity_fraction);
}

function Trajectory({ points, locale }: { points: Point[]; locale: Locale }) {
  const width = 900;
  const height = 245;
  const pad = { top: 18, right: 16, bottom: 30, left: 52 };
  const all = points.flatMap((point) => [point.cex_price, point.dex_price]);
  const lo = Math.min(...all);
  const hi = Math.max(...all);
  const spread = Math.max(hi - lo, Math.abs(hi) * 0.002, 0.0001);
  const min = lo - spread * 0.15;
  const max = hi + spread * 0.15;
  const x = (index: number) => pad.left + index / Math.max(points.length - 1, 1) * (width - pad.left - pad.right);
  const y = (value: number) => pad.top + (max - value) / (max - min) * (height - pad.top - pad.bottom);
  const path = (field: "cex_price" | "dex_price") => points.map((point, index) => `${index ? "L" : "M"}${x(index).toFixed(1)},${y(point[field]).toFixed(1)}`).join(" ");
  const formatter = new Intl.NumberFormat(locale === "es" ? "es-ES" : "en-US", { maximumFractionDigits: 3 });
  return <svg className="live-chart" viewBox={`0 0 ${width} ${height}`} role="img" aria-label={locale === "es" ? "Precios CEX y DEX a lo largo del tiempo" : "CEX and DEX prices over time"}>
    {[0, 0.5, 1].map((fraction) => {
      const yy = pad.top + fraction * (height - pad.top - pad.bottom);
      const value = max - fraction * (max - min);
      return <g key={fraction}><line x1={pad.left} x2={width - pad.right} y1={yy} y2={yy} className="live-grid" /><text x={pad.left - 8} y={yy + 4} textAnchor="end" className="live-axis">{formatter.format(value)}</text></g>;
    })}
    <path d={path("cex_price")} className="live-line live-line-cex" />
    <path d={path("dex_price")} className="live-line live-line-dex" />
    <text x={pad.left} y={height - 7} className="live-axis">{locale === "es" ? "tick" : "tick"} {points[0]?.tick ?? 0}</text>
    <text x={width - pad.right} y={height - 7} textAnchor="end" className="live-axis">{locale === "es" ? "tick" : "tick"} {points.at(-1)?.tick ?? 0}</text>
  </svg>;
}

function PairedTrajectory({ points, locale }: { points: ExperimentResult["trajectory"]; locale: Locale }) {
  const width = 760;
  const height = 170;
  const pad = { top: 12, right: 10, bottom: 25, left: 48 };
  const series = [
    { key: "static-lp_dex", className: "experiment-line-static" },
    { key: "adaptive-lp_dex", className: "experiment-line-adaptive" },
    { key: "static-lp_cex", className: "experiment-line-reference" }
  ] as const;
  const all = points.flatMap((point) => series.map(({ key }) => point[key]));
  const lo = Math.min(...all);
  const hi = Math.max(...all);
  const spread = Math.max(hi - lo, Math.abs(hi) * 0.002, 0.0001);
  const min = lo - spread * 0.12;
  const max = hi + spread * 0.12;
  const x = (index: number) => pad.left + index / Math.max(points.length - 1, 1) * (width - pad.left - pad.right);
  const y = (value: number) => pad.top + (max - value) / (max - min) * (height - pad.top - pad.bottom);
  return <svg className="experiment-chart" viewBox={`0 0 ${width} ${height}`} role="img" aria-label={locale === "es" ? "Trayectorias medias de los escenarios pareados" : "Mean trajectories for paired scenarios"}>
    {[0, 0.5, 1].map((fraction) => <line key={fraction} x1={pad.left} x2={width - pad.right} y1={pad.top + fraction * (height - pad.top - pad.bottom)} y2={pad.top + fraction * (height - pad.top - pad.bottom)} className="live-grid" />)}
    {series.map(({ key, className }) => <path key={key} className={`live-line ${className}`} d={points.map((point, index) => `${index ? "L" : "M"}${x(index).toFixed(1)},${y(point[key]).toFixed(1)}`).join(" ")} />)}
    <text x={pad.left} y={height - 5} className="live-axis">tick {points[0]?.tick ?? 0}</text>
    <text x={width - pad.right} y={height - 5} textAnchor="end" className="live-axis">tick {points.at(-1)?.tick ?? 0}</text>
  </svg>;
}

export default function LiveMicroworld({ locale }: { locale: Locale }) {
  const copy = words[locale];
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [history, setHistory] = useState<Point[]>([]);
  const [feed, setFeed] = useState<"loading" | "live" | "error">("loading");
  const [now, setNow] = useState(Date.now());
  const [seedCount, setSeedCount] = useState(20);
  const [horizon, setHorizon] = useState(40);
  const [shock, setShock] = useState(0.1);
  const [capacity, setCapacity] = useState(0.03);
  const [requestState, setRequestState] = useState<"idle" | "queued" | "running" | "done" | "error">("idle");
  const [result, setResult] = useState<ExperimentResult | null>(() => {
    if (typeof window === "undefined") return null;
    try { return JSON.parse(window.localStorage.getItem("microworld-last-experiment") || "null") as ExperimentResult | null; }
    catch { return null; }
  });
  const [requestError, setRequestError] = useState("");

  const refresh = useCallback(async () => {
    try {
      const [snapshotResponse, historyResponse] = await Promise.all([
        fetch(`${SNAPSHOT_URL}?v=${Date.now()}`, { cache: "no-store" }),
        fetch(`${HISTORY_URL}?v=${Date.now()}`, { cache: "no-store" })
      ]);
      if (!snapshotResponse.ok) throw new Error("snapshot not available");
      const candidate: unknown = await snapshotResponse.json();
      if (!validSnapshot(candidate)) throw new Error("invalid snapshot schema");
      setSnapshot(candidate);
      if (historyResponse.ok) {
        const rows: unknown = await historyResponse.json();
        if (Array.isArray(rows)) setHistory(rows.filter((row): row is Point => row && Number.isFinite(row.tick) && Number.isFinite(row.cex_price) && Number.isFinite(row.dex_price)).slice(-120));
      }
      setFeed("live");
    } catch {
      setFeed("error");
    }
  }, []);

  useEffect(() => {
    void refresh();
    const poll = window.setInterval(() => { void refresh(); setNow(Date.now()); }, 30_000);
    const clock = window.setInterval(() => setNow(Date.now()), 5_000);
    return () => { window.clearInterval(poll); window.clearInterval(clock); };
  }, [refresh]);

  const stale = useMemo(() => {
    if (!snapshot?.updated_at) return true;
    const time = Date.parse(snapshot.updated_at);
    return !Number.isFinite(time) || now - time > 45 * 60 * 1000;
  }, [now, snapshot]);

  const runExperiment = async () => {
    if (!API_URL) return;
    setRequestState("queued");
    setRequestError("");
    setResult(null);
    try {
      const response = await fetch(`${API_URL}/api/experiment`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ seed_count: seedCount, horizon, shock, capacity })
      });
      setRequestState("running");
      const payload = await response.json();
      if (!response.ok || !payload.result || typeof payload.result.run_id !== "string") throw new Error(payload.error || copy.failed);
      const value = payload.result as ExperimentResult;
      setResult(value);
      window.localStorage.setItem("microworld-last-experiment", JSON.stringify(value));
      setRequestState("done");
    } catch (error) {
      setRequestError(error instanceof Error ? error.message : copy.failed);
      setRequestState("error");
    }
  };

  const points = history.length > 1 ? history : snapshot ? [{ tick: snapshot.tick, cex_price: snapshot.cex_price, dex_price: snapshot.dex_price }] : [];
  const statusText = feed === "loading" ? copy.loading : feed === "error" || !snapshot ? copy.offline : stale ? copy.stale : copy.live;
  const updated = snapshot?.updated_at ? new Intl.DateTimeFormat(locale === "es" ? "es-ES" : "en-US", { dateStyle: "medium", timeStyle: "short" }).format(new Date(snapshot.updated_at)) : "—";

  return <section className="live-microworld" aria-labelledby="live-microworld-title">
    <div className="live-heading">
      <div><p className="eyebrow">{copy.kicker}</p><h3 id="live-microworld-title">{copy.title}</h3><p>{copy.intro}</p></div>
      <div className={`live-status ${feed === "live" && !stale ? "is-live" : "is-muted"}`} aria-live="polite"><i className="status-dot" />{statusText}</div>
    </div>
    <div className="live-metrics">
      <div><span>{copy.tick}</span><strong>{snapshot?.tick ?? "—"}</strong></div>
      <div><span>{copy.cex}</span><strong>{snapshot ? number(snapshot.cex_price, locale, 5) : "—"}</strong></div>
      <div><span>{copy.dex}</span><strong>{snapshot ? number(snapshot.dex_price, locale, 5) : "—"}</strong></div>
      <div><span>{copy.error}</span><strong>{snapshot ? number(snapshot.log_error, locale, 5) : "—"}</strong></div>
    </div>
    <div className="live-chart-head"><span>{copy.history}</span><div className="live-legend"><i className="live-key live-key-cex" />CEX <i className="live-key live-key-dex" />DEX</div></div>
    {points.length > 1 ? <Trajectory points={points} locale={locale} /> : <div className="live-empty">{feed === "loading" ? copy.loading : copy.noHistory}</div>}
    <div className="live-provenance">
      <span>{copy.updated}: <strong>{updated}</strong></span>
      <span>{copy.event}: <strong>{snapshot?.last_event ?? copy.noEvent}</strong></span>
      <span>{copy.model}: <strong>{snapshot?.model_version ?? "infra-001-placeholder-0.1"}</strong></span>
    </div>
    <p className="live-caveat">{copy.synthetic}. {copy.local}</p>

    <div className="enhanced-run">
      <div className="enhanced-copy"><p className="eyebrow">Azure optional · bounded cloud run</p><h4>{copy.enhanced}</h4><p>{copy.enhancedIntro}</p></div>
      <div className="enhanced-controls">
        <label><span>{copy.seedCount}<b>{seedCount}</b></span><input type="range" min="2" max="100" step="2" value={seedCount} onChange={(event) => setSeedCount(Number(event.target.value))} /></label>
        <label><span>{copy.horizon}<b>{horizon}</b></span><input type="range" min="5" max="100" step="5" value={horizon} onChange={(event) => setHorizon(Number(event.target.value))} /></label>
        <label><span>{copy.shock}<b>{shock >= 0 ? "+" : ""}{number(shock, locale, 2)}</b></span><input type="range" min="-0.2" max="0.2" step="0.01" value={shock} onChange={(event) => setShock(Number(event.target.value))} /></label>
        <label><span>{copy.capacity}<b>{number(capacity * 100, locale, 1)}%</b></span><input type="range" min="0" max="0.1" step="0.005" value={capacity} onChange={(event) => setCapacity(Number(event.target.value))} /></label>
        <button className="button button-primary" type="button" disabled={!API_URL || requestState === "queued" || requestState === "running"} onClick={() => void runExperiment()}>{!API_URL ? copy.unavailable : requestState === "queued" || requestState === "running" ? copy.running : copy.run}</button>
      </div>
      {!API_URL && <p className="enhanced-unavailable">{copy.unavailableHelp}</p>}
      {requestError && <p className="enhanced-unavailable" role="alert">{requestError}</p>}
      {result && <div className="enhanced-result" aria-live="polite"><div className="enhanced-result-top"><strong>{copy.result}</strong><span>{result.seed_count} {copy.seeds} · {result.horizon_ticks} {copy.ticks} · ABM {result.model_version}</span></div>
        <div className="experiment-legend"><span><i className="experiment-key experiment-key-reference" />CEX</span><span><i className="experiment-key experiment-key-static" />{copy.static}</span><span><i className="experiment-key experiment-key-adaptive" />{copy.adaptive}</span></div>
        <PairedTrajectory points={result.trajectory} locale={locale} />
        {([ ["static-lp", copy.static], ["adaptive-lp", copy.adaptive] ] as const).map(([key, label]) => {
          const metrics = result.scenarios[key];
          return <div className="enhanced-result-row" key={key}><b>{label}</b><span>{copy.peak}: {number(metrics.maximum_absolute_log_error.mean, locale, 4)} [{number(metrics.maximum_absolute_log_error.p05, locale, 4)}–{number(metrics.maximum_absolute_log_error.p95, locale, 4)}]</span><span>{copy.returnRate}: {number(metrics.return_to_band_rate * 100, locale, 1)}%</span></div>;
        })}
        <small>{result.limitations}</small>
        <button type="button" className="button button-quiet enhanced-download" onClick={() => {
          const blob = new Blob([JSON.stringify(result, null, 2)], { type: "application/json" });
          const url = URL.createObjectURL(blob);
          const link = document.createElement("a");
          link.href = url; link.download = `microworld-${result.run_id}.json`; link.click(); URL.revokeObjectURL(url);
        }}>{locale === "es" ? "Descargar resultado JSON" : "Download result JSON"}</button>
      </div>}
      {requestState === "running" && <p className="enhanced-unavailable" aria-live="polite">{copy.queued} · {copy.running}</p>}
    </div>
  </section>;
}
