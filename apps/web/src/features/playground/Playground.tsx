import { useMemo, useState } from "react";
import type { Locale } from "@tesis/content";
import { MODEL_VERSION, SUSTAINED_BAND_TICKS, runFixedSale, runTracking } from "./model";

type Copy = {
  kicker: string;
  title: string;
  intro: string;
  scope: string;
  trackingTab: string;
  depthTab: string;
  trackingTitle: string;
  trackingIntro: string;
  depthTitle: string;
  depthIntro: string;
  shock: string;
  arbitrage: string;
  band: string;
  delay: string;
  horizon: string;
  sale: string;
  remaining: string;
  noArbitrage: string;
  cex: string;
  dex: string;
  maxError: string;
  excessError: string;
  returnTick: string;
  noReturn: string;
  tick: string;
  fullDepth: string;
  reducedDepth: string;
  impact: string;
  priceMove: string;
  assumptions: string;
  model: string;
  config: string;
  assumptionsText: string;
  copyScenario: string;
  copied: string;
  copyFailed: string;
  disabled: string;
  low: string;
  high: string;
  shockRange: string;
  capacityHelp: string;
  bandHelp: string;
  ticks: string;
  saleHelp: string;
  remainingHelp: string;
  withdrawalText: string;
};

type Props = { locale: Locale; copy: Copy };

function numberLabel(value: number, digits = 3, locale: Locale = "en") {
  return new Intl.NumberFormat(locale === "es" ? "es-ES" : "en-US", { maximumFractionDigits: digits }).format(value);
}

function LineChart({
  points,
  band,
  locale,
  labels
}: {
  points: ReturnType<typeof runTracking>["points"];
  band: number;
  locale: Locale;
  labels: { cex: string; dex: string; band: string; tick: string };
}) {
  const width = 760;
  const height = 300;
  const padding = { top: 18, right: 18, bottom: 34, left: 54 };
  const values = points.flatMap((point) => [point.cexPrice, point.dexPrice, point.cexPrice * Math.exp(band), point.cexPrice * Math.exp(-band)]);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const spread = Math.max(max - min, 0.001);
  const domainMin = min - spread * 0.12;
  const domainMax = max + spread * 0.12;
  const x = (index: number) => padding.left + (index / Math.max(points.length - 1, 1)) * (width - padding.left - padding.right);
  const y = (value: number) => padding.top + ((domainMax - value) / (domainMax - domainMin)) * (height - padding.top - padding.bottom);
  const line = (selector: (point: (typeof points)[number]) => number) => points.map((point, index) => `${index === 0 ? "M" : "L"}${x(index).toFixed(2)},${y(selector(point)).toFixed(2)}`).join(" ");
  const bandPoints = [
    ...points.map((point, index) => `${x(index).toFixed(2)},${y(point.cexPrice * Math.exp(band)).toFixed(2)}`),
    ...points.map((point, index) => `${x(points.length - 1 - index).toFixed(2)},${y(points[points.length - 1 - index].cexPrice * Math.exp(-band)).toFixed(2)}`)
  ].join(" ");

  return <div className="playground-chart-wrap">
    <div className="playground-chart-legend" aria-hidden="true">
      <span><i className="chart-key chart-key-cex" />{labels.cex}</span>
      <span><i className="chart-key chart-key-dex" />{labels.dex}</span>
      <span><i className="chart-key chart-key-band" />{labels.band}</span>
    </div>
    <svg className="playground-chart" viewBox={`0 0 ${width} ${height}`} role="img" aria-label={`${labels.cex}, ${labels.dex}, ${labels.band}`}>
      {[0, 0.5, 1].map((fraction) => {
        const value = domainMax - (domainMax - domainMin) * fraction;
        const yy = y(value);
        return <g key={fraction}>
          <line x1={padding.left} x2={width - padding.right} y1={yy} y2={yy} className="chart-gridline" />
          <text x={padding.left - 8} y={yy + 4} className="chart-axis-label" textAnchor="end">{numberLabel(value, 3, locale)}</text>
        </g>;
      })}
      <polygon points={bandPoints} className="chart-band" />
      <path d={line((point) => point.cexPrice)} className="chart-cex-line" />
      <path d={line((point) => point.dexPrice)} className="chart-dex-line" />
      <text x={padding.left} y={height - 8} className="chart-axis-label">{labels.tick} 0</text>
      <text x={width - padding.right} y={height - 8} className="chart-axis-label" textAnchor="end">{labels.tick} {points.length - 1}</text>
    </svg>
  </div>;
}

export default function Playground({ locale, copy }: Props) {
  const [mode, setMode] = useState<"tracking" | "depth">("tracking");
  const [shock, setShock] = useState(0.1);
  const [capacity, setCapacity] = useState<number>(0.03);
  const [band, setBand] = useState(0.003);
  const [delay, setDelay] = useState(0);
  const [horizon, setHorizon] = useState(20);
  const [sale, setSale] = useState(500);
  const [remaining, setRemaining] = useState(0.45);
  const [copyState, setCopyState] = useState<"idle" | "copied" | "failed">("idle");

  const trackingParameters = useMemo(() => ({
    shockLogReturn: shock,
    shockTick: 1,
    horizonTicks: horizon,
    executionDelayTicks: delay,
    noArbitrageBandLog: band,
    capacityFraction: capacity
  }), [band, capacity, delay, horizon, shock]);
  const tracking = useMemo(() => runTracking(trackingParameters), [trackingParameters]);
  const fullDepth = useMemo(() => runFixedSale(sale, 1), [sale]);
  const reducedDepth = useMemo(() => runFixedSale(sale, remaining), [remaining, sale]);

  const copyScenario = async () => {
    const scenario = {
      modelVersion: MODEL_VERSION,
      config: "experiments/cex_dex_mvp/config.json",
      configVersion: MODEL_VERSION,
      initialReserves: { x: 10_000, y: 10_000 },
      initialCexPrice: 1,
      swapFee: 0,
      experiment: mode === "tracking" ? "E0/E1" : "E2",
      ...(mode === "tracking"
        ? { ...trackingParameters, sustainedBandTicks: SUSTAINED_BAND_TICKS, results: { maxAbsoluteLogError: tracking.maxAbsoluteLogError, maxExcessError: tracking.maxExcessError, sustainedReturnTick: tracking.sustainedReturnTick } }
        : { fixedSaleX: sale, remainingReserveFraction: remaining, results: { fullDepthImpact: fullDepth.absoluteLogPriceImpact, reducedDepthImpact: reducedDepth.absoluteLogPriceImpact } })
    };
    try {
      await navigator.clipboard.writeText(JSON.stringify(scenario, null, 2));
      setCopyState("copied");
    } catch {
      setCopyState("failed");
    }
    window.setTimeout(() => setCopyState("idle"), 2200);
  };

  return <section id="lab" className="playground-section page-pad">
    <div className="section-heading">
      <span className="section-index">02</span>
      <div>
        <p className="eyebrow">{copy.kicker}</p>
        <h2>{copy.title}</h2>
        <p className="section-intro">{copy.intro}</p>
      </div>
    </div>

    <div className="playground-shell">
      <div className="playground-topline">
        <div className="playground-tabs" role="group" aria-label={copy.title}>
          <button type="button" aria-pressed={mode === "tracking"} className={mode === "tracking" ? "playground-tab is-selected" : "playground-tab"} onClick={() => setMode("tracking")}>E0 / E1 · {copy.trackingTab}</button>
          <button type="button" aria-pressed={mode === "depth"} className={mode === "depth" ? "playground-tab is-selected" : "playground-tab"} onClick={() => setMode("depth")}>E2 · {copy.depthTab}</button>
        </div>
        <span className="playground-version mono">{copy.model} {MODEL_VERSION}</span>
      </div>

      <div className="playground-grid" id="playground-panel" aria-label={mode === "tracking" ? copy.trackingTitle : copy.depthTitle}>
        <aside className="playground-controls" aria-label={copy.assumptions}>
          {mode === "tracking" ? <>
            <div className="playground-control-heading"><p className="eyebrow">{copy.trackingTab}</p><h3>{copy.trackingTitle}</h3><p>{copy.trackingIntro}</p></div>
            <label className="range-control"><span>{copy.shock}<strong>{shock >= 0 ? "+" : ""}{numberLabel(shock, 2, locale)}</strong></span><input type="range" min="-0.2" max="0.2" step="0.01" value={shock} onChange={(event) => setShock(Number(event.target.value))} /><small>{copy.shockRange}</small></label>
            <label className="range-control"><span>{copy.arbitrage}<strong>{capacity === 0 ? copy.disabled : `${numberLabel(capacity * 100, 1, locale)}%`}</strong></span><select value={capacity} onChange={(event) => setCapacity(Number(event.target.value))}><option value={0}>{copy.disabled} · 0%</option><option value={0.005}>{copy.low} · {numberLabel(0.5, 1, locale)}%</option><option value={0.03}>{copy.high} · {numberLabel(3, 0, locale)}%</option></select><small>{copy.capacityHelp}</small></label>
            <label className="range-control"><span>{copy.band}<strong>{numberLabel(band, 3, locale)}</strong></span><input type="range" min="0.001" max="0.02" step="0.001" value={band} onChange={(event) => setBand(Number(event.target.value))} /><small>{copy.bandHelp}</small></label>
            <div className="playground-control-pair">
              <label className="range-control"><span>{copy.delay}<strong>{delay}</strong></span><input type="range" min="0" max="5" step="1" value={delay} onChange={(event) => setDelay(Number(event.target.value))} /><small>{copy.ticks}</small></label>
              <label className="range-control"><span>{copy.horizon}<strong>{horizon}</strong></span><input type="range" min="5" max="40" step="1" value={horizon} onChange={(event) => setHorizon(Number(event.target.value))} /><small>{copy.ticks}</small></label>
            </div>
          </> : <>
            <div className="playground-control-heading"><p className="eyebrow">{copy.depthTab}</p><h3>{copy.depthTitle}</h3><p>{copy.depthIntro}</p></div>
            <label className="range-control"><span>{copy.sale}<strong>{numberLabel(sale, 0, locale)} x</strong></span><input type="range" min="100" max="2000" step="50" value={sale} onChange={(event) => setSale(Number(event.target.value))} /><small>{copy.saleHelp}</small></label>
            <label className="range-control"><span>{copy.remaining}<strong>{Math.round(remaining * 100)}%</strong></span><input type="range" min="0.2" max="1" step="0.05" value={remaining} onChange={(event) => setRemaining(Number(event.target.value))} /><small>{copy.remainingHelp}</small></label>
            <div className="playground-invariant"><span className="mono">x · y</span><p>{copy.withdrawalText}</p></div>
          </>}
          <button className="playground-copy button button-quiet" type="button" onClick={copyScenario}>{copyState === "copied" ? copy.copied : copyState === "failed" ? copy.copyFailed : copy.copyScenario}</button>
        </aside>

        <div className="playground-results" aria-live="polite">
          {mode === "tracking" ? <>
            <div className="playground-result-heading"><div><p className="eyebrow">E0 / E1</p><h3>{copy.trackingTitle}</h3></div><span className="playground-run-mark"><i className="status-dot" />{copy.scope}</span></div>
            <LineChart points={tracking.points} band={band} locale={locale} labels={{ cex: copy.cex, dex: copy.dex, band: copy.noArbitrage, tick: copy.tick }} />
            <div className="playground-metrics">
              <div><span>{copy.maxError}</span><strong>{numberLabel(tracking.maxAbsoluteLogError, 4, locale)}</strong></div>
              <div><span>{copy.excessError}</span><strong>{numberLabel(tracking.maxExcessError, 4, locale)}</strong></div>
              <div><span>{copy.returnTick}</span><strong>{tracking.sustainedReturnTick ?? copy.noReturn}</strong></div>
            </div>
          </> : <>
            <div className="playground-result-heading"><div><p className="eyebrow">E2</p><h3>{copy.depthTitle}</h3></div><span className="playground-run-mark"><i className="status-dot" />{copy.scope}</span></div>
            <div className="depth-comparison">
              {[{ label: copy.fullDepth, result: fullDepth }, { label: copy.reducedDepth, result: reducedDepth }].map(({ label, result }) => <article className="depth-card" key={label}>
                <p>{label}</p>
                <strong>{numberLabel(result.absoluteLogPriceImpact, 4, locale)}</strong>
                <span>{copy.impact}</span>
                <div className="depth-bar-track"><i style={{ width: `${Math.min(result.absoluteLogPriceImpact / Math.max(reducedDepth.absoluteLogPriceImpact, 0.0001) * 100, 100)}%` }} /></div>
                <small>{copy.priceMove}: {numberLabel(result.percentagePriceChange * 100, 2, locale)}%</small>
              </article>)}
            </div>
            <div className="depth-note"><span className="mono">{numberLabel(sale, 0, locale)} x</span><p>{copy.assumptionsText}</p></div>
          </>}
        </div>
      </div>

      <div className="playground-footnote"><span className="mono">{copy.config} · cex-dex-mvp 0.3.0</span><p>{copy.assumptionsText}</p></div>
    </div>
  </section>;
}
