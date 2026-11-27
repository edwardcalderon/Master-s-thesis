import { useEffect, useMemo, useState } from "react";
import type { Locale } from "@tesis/content";
import type { TrackingPoint } from "./model";

type SharedSnapshot = { tick: number; updated_at?: string; model_version?: string; synthetic?: boolean };

const SNAPSHOT_URL = "https://raw.githubusercontent.com/edwardcalderon/Master-s-thesis/microworld-data/snapshot.json";

const copy = {
  en: {
    caption: "System map · schematic", cex: "CEX reference", arb: "Arbitrage rule", dex: "DEX · constant product",
    marketInput: "External price signal", decision: "Band + capacity check", trade: "Reserve swap", feedback: "Price error feedback",
    active: "Individual agents", aggregate: "Aggregate rule", ticks: "Local ticks computed", swaps: "Ticks with a swap", world: "Shared world tick",
    noAgents: "0 · aggregate model", ruleCount: "1 rule", feedUnavailable: "not connected", note: "The local experiment is recomputed in your browser. The shared feed advances periodically; it does not run individual agents. Diagram is a schematic of the implemented equations.",
    sell: "SELL X", buy: "BUY X", idle: "WITHIN BAND", current: "CURRENT STATE", persistent: "PERSISTENT FEED"
  },
  es: {
    caption: "Mapa del sistema · esquema", cex: "Referencia CEX", arb: "Regla de arbitraje", dex: "DEX · producto constante",
    marketInput: "Señal exógena de precio", decision: "Verificación de banda y capacidad", trade: "Intercambio de reservas", feedback: "Retroalimentación del error",
    active: "Agentes individuales", aggregate: "Regla agregada", ticks: "Ticks locales calculados", swaps: "Ticks con intercambio", world: "Tick del mundo compartido",
    noAgents: "0 · modelo agregado", ruleCount: "1 regla", feedUnavailable: "sin conexión", note: "El experimento local se recalcula en el navegador. La fuente compartida avanza periódicamente; no ejecuta agentes individuales. El diagrama esquematiza las ecuaciones implementadas.",
    sell: "VENDER X", buy: "COMPRAR X", idle: "DENTRO DE BANDA", current: "ESTADO ACTUAL", persistent: "FUENTE PERSISTENTE"
  }
} as const;

function readSnapshot(value: unknown): SharedSnapshot | null {
  if (!value || typeof value !== "object") return null;
  const snapshot = value as Partial<SharedSnapshot>;
  return Number.isFinite(snapshot.tick) ? snapshot as SharedSnapshot : null;
}

export default function SystemOverview({ locale, points, horizon, band, capacity }: {
  locale: Locale;
  points: TrackingPoint[];
  horizon: number;
  band: number;
  capacity: number;
}) {
  const [shared, setShared] = useState<SharedSnapshot | null>(null);
  const [feedOnline, setFeedOnline] = useState(false);
  const words = copy[locale];
  const current = points.at(-1);
  const error = current?.logError ?? 0;
  const active = capacity > 0 && Math.abs(error) > band + 1e-12;
  const swaps = useMemo(() => points.slice(1).reduce((count, point, index) =>
    count + (Math.abs(point.dexPrice - points[index].dexPrice) > 1e-12 ? 1 : 0), 0), [points]);
  const direction = error > band ? words.sell : error < -band ? words.buy : words.idle;

  useEffect(() => {
    let cancelled = false;
    const refresh = async () => {
      try {
        const response = await fetch(`${SNAPSHOT_URL}?t=${Date.now()}`, { cache: "no-store" });
        if (!response.ok) throw new Error("snapshot unavailable");
        const snapshot = readSnapshot(await response.json());
        if (!snapshot) throw new Error("snapshot invalid");
        if (!cancelled) { setShared(snapshot); setFeedOnline(true); }
      } catch {
        if (!cancelled) setFeedOnline(false);
      }
    };
    void refresh();
    const timer = window.setInterval(() => void refresh(), 30_000);
    return () => { cancelled = true; window.clearInterval(timer); };
  }, []);

  return <section className="system-overview" aria-label={words.caption}>
    <div className="system-overview-top">
      <span className="mono">{words.caption}</span>
      <span className="system-feed-state"><i className={feedOnline ? "status-dot is-connected" : "status-dot"} />{words.persistent} · {feedOnline ? `${words.world} ${shared?.tick}` : words.feedUnavailable}</span>
    </div>
    <div className="system-scene" data-active={active}>
      <svg viewBox="0 0 1120 390" role="img" aria-label={`${words.cex} → ${words.arb} → ${words.dex}; ${words.feedback}`}>
        <defs>
          <linearGradient id="pool-top" x1="0" x2="1" y1="0" y2="1"><stop offset="0" stopColor="var(--accent-soft)"/><stop offset="1" stopColor="var(--panel)"/></linearGradient>
          <linearGradient id="cube-side" x1="0" x2="1"><stop offset="0" stopColor="var(--line)"/><stop offset="1" stopColor="var(--panel)"/></linearGradient>
          <filter id="node-shadow" x="-30%" y="-30%" width="160%" height="180%"><feDropShadow dx="0" dy="12" stdDeviation="8" floodColor="var(--ink)" floodOpacity=".09"/></filter>
          <marker id="arrow-tip" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 10 5 0 10z" fill="var(--accent)"/></marker>
        </defs>
        <path className="system-flow system-flow-market" d="M253 155 C330 155 343 155 416 155" markerEnd="url(#arrow-tip)" />
        <path className={`system-flow system-flow-trade${active ? " is-active" : ""}`} d="M642 165 C714 165 729 165 801 165" markerEnd="url(#arrow-tip)" />
        <path className="system-flow system-flow-feedback" d="M864 260 C790 341 487 346 430 259" markerEnd="url(#arrow-tip)" />
        <text x="330" y="135" className="system-flow-label">{words.marketInput}</text>
        <text x="710" y="143" className="system-flow-label">{words.trade}</text>
        <text x="584" y="355" className="system-flow-label">{words.feedback}</text>

        <g className="system-node system-node-cex" filter="url(#node-shadow)">
          <path className="system-cube-front" d="M75 154 163 110 252 154 164 200z"/><path className="system-cube-left" d="M75 154v87l89 49v-90z"/><path className="system-cube-right" d="M164 200v90l88-49v-87z"/>
          <path className="system-cube-highlight" d="m96 155 68-34 69 34-69 35z"/>
          <text x="164" y="222" className="system-node-label" textAnchor="middle">{words.cex}</text><text x="164" y="244" className="system-node-meta" textAnchor="middle">pᶜ = {current?.cexPrice.toFixed(4) ?? "—"}</text>
        </g>

        <g className={`system-node system-node-rule${active ? " is-active" : ""}`} filter="url(#node-shadow)">
          <path className="system-cube-front" d="M417 154 528 98 642 154 529 211z"/><path className="system-cube-left" d="M417 154v83l112 59v-85z"/><path className="system-cube-right" d="M529 211v85l113-59v-83z"/>
          <circle className="system-rule-core" cx="529" cy="188" r="29"/><path className="system-rule-mark" d="m514 188 10 10 21-23"/>
          <text x="529" y="244" className="system-node-label" textAnchor="middle">{words.arb}</text><text x="529" y="265" className="system-node-meta" textAnchor="middle">{capacity > 0 ? `${(capacity * 100).toFixed(1)}% CAPACITY` : "CAPACITY · 0%"}</text>
        </g>

        <g className="system-node system-node-pool" filter="url(#node-shadow)">
          <path className="system-cube-front" d="M802 157 891 112 980 157 891 203z"/><path className="system-cube-left" d="M802 157v84l89 49v-87z"/><path className="system-cube-right" d="M891 203v87l89-49v-84z"/>
          <path className="system-pool-surface" d="m823 159 68-34 68 34-68 35z"/><path className="system-pool-wave" d="M841 159q20-12 40 0t40 0 27 0"/>
          <text x="891" y="238" className="system-node-label" textAnchor="middle">{words.dex}</text><text x="891" y="259" className="system-node-meta" textAnchor="middle">pᴰ = {current?.dexPrice.toFixed(4) ?? "—"} · y / x</text>
        </g>
        <g className={`system-order-chip${active ? " is-active" : ""}`} transform="translate(690 198)"><rect width="94" height="24" rx="2"/><text x="47" y="16" textAnchor="middle">{direction}</text></g>
        <text x="76" y="32" className="system-scene-overline">{words.current} · {words.ticks.toUpperCase()} {Math.min(points.length - 1, horizon)} / {horizon}</text>
        <text x="1043" y="32" className="system-scene-overline" textAnchor="end">e = {error.toFixed(4)} · BAND ±{band.toFixed(3)}</text>
      </svg>
    </div>
    <div className="system-live-stats" aria-live="polite">
      <div><span>{words.active}</span><strong>{words.noAgents}</strong></div>
      <div><span>{words.aggregate}</span><strong>{words.ruleCount}</strong></div>
      <div><span>{words.ticks}</span><strong>{Math.min(points.length - 1, horizon)} / {horizon}</strong></div>
      <div><span>{words.swaps}</span><strong>{swaps}</strong></div>
      <div><span>{words.world}</span><strong>{shared?.tick ?? "—"}</strong></div>
    </div>
    <p className="system-note">{words.note}</p>
  </section>;
}
