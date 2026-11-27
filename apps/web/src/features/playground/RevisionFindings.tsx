import { useMemo, useState } from "react";
import type { Locale } from "@tesis/content";
import findings from "../../data/h2-review-findings.json";

type Shock = -0.05 | -0.1 | -0.2;
type Panel = "recovery" | "panic" | "capacity";

const shocks: Shock[] = [-0.05, -0.1, -0.2];
const depths = [0.5, 1, 2];

const copy = {
  en: {
    kicker: "Mechanism replay · exploratory",
    title: "What drives departures after recovery?",
    intro: "A replay of the existing seed streams separates one-off panic events from repeated exits, then checks how much the reserve-linked arbitrage cap contributes at shallow depth.",
    recovery: "Post-recovery contrast",
    panic: "Panic ablation",
    capacity: "Capacity control",
    area: "E3 − E1-high post-recovery excess area",
    depth: "Depth factor",
    shock: "Shock",
    noPanic: "Panic disabled",
    withPanic: "Panic enabled",
    departures: "Recovered paths with later departure",
    episodes: "Mean episodes per recovered path",
    oneOff: "single episodes",
    recurring: "multi-episode paths",
    linked: "Reserve-linked cap",
    fixed: "Initial-reserve cap",
    recoveryRate: "E3 recovery rate",
    allRunsDepart: "E3 later departures / all runs",
    pairedDelta: "Paired E3 − E1-high area",
    interval: "95% paired seed-bootstrap interval",
    provenance: `${findings.replayed_paths.toLocaleString("en-US")} replayed paths · ${findings.exact_archived_metric_matches.toLocaleString("en-US")} archived metric matches · seeds ${findings.seed_range[0]}–${findings.seed_range[1]}`,
    limitation: "Exploratory replay of existing seeds, not an independent confirmation. The simulator is synthetic and zero-fee; departures are counted from end-of-tick states and do not establish within-tick causality.",
    noData: "No result for this selection.",
    chartLabel: "Paired post-recovery excess-area contrast by depth and shock",
    zero: "No detectable paired contrast",
    tracks: "E3 minus E1-high",
    paths: "paths",
  },
  es: {
    kicker: "Repetición de mecanismos · exploratoria",
    title: "¿Qué impulsa las salidas después de recuperarse?",
    intro: "La repetición de las semillas existentes separa los eventos únicos de pánico de las salidas recurrentes y examina cuánto aporta el límite de arbitraje ligado a reservas en profundidad baja.",
    recovery: "Contraste posrecuperación",
    panic: "Ablación del pánico",
    capacity: "Control de capacidad",
    area: "Área de exceso posrecuperación E3 − E1-alta",
    depth: "Factor de profundidad",
    shock: "Choque",
    noPanic: "Pánico desactivado",
    withPanic: "Pánico activo",
    departures: "Trayectorias recuperadas con salida posterior",
    episodes: "Episodios medios por trayectoria recuperada",
    oneOff: "episodios únicos",
    recurring: "trayectorias con episodios múltiples",
    linked: "Límite ligado a reservas",
    fixed: "Límite según reserva inicial",
    recoveryRate: "Tasa de recuperación E3",
    allRunsDepart: "Salidas posteriores E3 / todas las corridas",
    pairedDelta: "Área pareada E3 − E1-alta",
    interval: "Intervalo bootstrap pareado del 95% por semilla",
    provenance: `${findings.replayed_paths.toLocaleString("es-CO")} trayectorias repetidas · ${findings.exact_archived_metric_matches.toLocaleString("es-CO")} métricas archivadas cotejadas · semillas ${findings.seed_range[0]}–${findings.seed_range[1]}`,
    limitation: "Repetición exploratoria de semillas existentes, no una confirmación independiente. El simulador es sintético y sin comisiones; las salidas se cuentan al final de cada tick y no establecen causalidad intratick.",
    noData: "No hay resultados para esta selección.",
    chartLabel: "Contraste pareado del área de exceso posrecuperación por profundidad y choque",
    zero: "Sin contraste pareado detectable",
    tracks: "E3 menos E1-alta",
    paths: "trayectorias",
  },
} satisfies Record<Locale, Record<string, string>>;

function fmt(value: number, locale: Locale, digits = 3) {
  return new Intl.NumberFormat(locale === "es" ? "es-CO" : "en-US", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(value);
}

function Percent({ value, locale }: { value: number; locale: Locale }) {
  return <>{fmt(value * 100, locale, 1)}%</>;
}

function PostRecoveryChart({ locale }: { locale: Locale }) {
  const t = copy[locale];
  const rows = findings.post_recovery.filter((row) => row.scope === "cell");
  const width = 760;
  const height = 236;
  const left = 64;
  const right = 28;
  const top = 18;
  const bottom = 46;
  const maxValue = 0.15;
  const x = (depth: number) => left + ((depth - 0.5) / 1.5) * (width - left - right);
  const y = (value: number) => top + ((maxValue - value) / maxValue) * (height - top - bottom);
  const colors = ["#455f4c", "#b77b4e", "#7685a1"];

  return <div className="revision-chart-wrap">
    <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={t.chartLabel}>
      {[0, 0.05, 0.1, 0.15].map((tick) => <g key={tick}>
        <line x1={left} x2={width - right} y1={y(tick)} y2={y(tick)} className="revision-gridline" />
        <text x={left - 9} y={y(tick) + 4} textAnchor="end" className="revision-axis-label">{fmt(tick, locale, 2)}</text>
      </g>)}
      {depths.map((depth) => <g key={depth}>
        <line x1={x(depth)} x2={x(depth)} y1={top} y2={height - bottom} className="revision-depth-line" />
        <text x={x(depth)} y={height - 18} textAnchor="middle" className="revision-axis-label">{depth}</text>
      </g>)}
      {shocks.map((shock, seriesIndex) => {
        const points = depths.map((depth) => {
          const row = rows.find((item) => item.depth_scale === depth && item.shock_log_return === shock);
          if (!row) return undefined;
          const mean = row.post_recovery_excess_area_e3_minus_e1_mean;
          const low = row.post_recovery_excess_area_ci95_low;
          const high = row.post_recovery_excess_area_ci95_high;
          return { depth, mean, low, high };
        }).filter((point): point is NonNullable<typeof point> => Boolean(point));
        return <g key={shock} className="revision-series" style={{ color: colors[seriesIndex] }}>
          {points.length > 1 && <polyline points={points.map((point) => `${x(point.depth)},${y(point.mean)}`).join(" ")} className="revision-series-line" />}
          {points.map((point) => <g key={point.depth}>
            <line x1={x(point.depth)} x2={x(point.depth)} y1={y(point.high)} y2={y(point.low)} className="revision-ci" />
            <line x1={x(point.depth) - 5} x2={x(point.depth) + 5} y1={y(point.high)} y2={y(point.high)} className="revision-ci" />
            <line x1={x(point.depth) - 5} x2={x(point.depth) + 5} y1={y(point.low)} y2={y(point.low)} className="revision-ci" />
            <circle cx={x(point.depth)} cy={y(point.mean)} r="4.5" className="revision-point" />
          </g>)}
        </g>;
      })}
    </svg>
    <div className="revision-legend">{shocks.map((shock, index) => <span key={shock}><i style={{ backgroundColor: colors[index] }} />{t.shock} {fmt(shock, locale, 2)}</span>)}</div>
  </div>;
}

export default function RevisionFindings({ locale }: { locale: Locale }) {
  const t = copy[locale];
  const [panel, setPanel] = useState<Panel>("recovery");
  const [shock, setShock] = useState<Shock>(-0.05);
  const departure = useMemo(() => {
    const get = (variant: string, condition: string) => findings.departure_episodes.find((row) => row.variant === variant && row.condition === condition && row.shock_log_return === shock);
    return {
      e1Panic: get("fixed_orders", "E1-arb-high-static"),
      e1NoPanic: get("no_panic", "E1-arb-high-static"),
      e3Panic: get("fixed_orders", "E3-adaptive-lp-high-arb"),
      e3NoPanic: get("no_panic", "E3-adaptive-lp-high-arb"),
    };
  }, [shock]);
  const capacityRows = findings.capacity_counterfactual.filter((row) => row.shock_log_return === shock);
  const current = capacityRows.find((row) => row.capacity_reference === "current_reserves");
  const fixed = capacityRows.find((row) => row.capacity_reference === "initial_reserves");
  const panelNames: Record<Panel, string> = { recovery: t.recovery, panic: t.panic, capacity: t.capacity };

  return <section className="revision-findings" aria-labelledby="revision-findings-title">
    <div className="revision-findings-heading">
      <div><p className="eyebrow">{t.kicker}</p><h3 id="revision-findings-title">{t.title}</h3><p>{t.intro}</p></div>
      <span className="revision-run-tag">H2 · 0.7.0</span>
    </div>
    <div className="revision-tabs" role="tablist" aria-label={t.title}>
      {(Object.keys(panelNames) as Panel[]).map((key) => <button key={key} type="button" role="tab" aria-selected={panel === key} className={panel === key ? "is-selected" : ""} onClick={() => setPanel(key)}>{panelNames[key]}</button>)}
    </div>
    {panel === "recovery" && <div className="revision-panel" role="tabpanel">
      <div className="revision-panel-heading"><div><h4>{t.area}</h4><p>{t.interval}</p></div><span>{t.tracks}</span></div>
      <PostRecoveryChart locale={locale} />
      <div className="revision-depth-labels">{depths.map((depth) => <span key={depth}>{t.depth} {depth}</span>)}</div>
    </div>}
    {panel === "panic" && <div className="revision-panel" role="tabpanel">
      <div className="revision-panel-heading"><div><h4>{t.panic}</h4><p>{t.departures} · {t.episodes}</p></div>
        <label className="revision-shock"><span>{t.shock}</span><select value={shock} onChange={(event) => setShock(Number(event.target.value) as Shock)}>{shocks.map((value) => <option key={value} value={value}>{fmt(value, locale, 2)}</option>)}</select></label>
      </div>
      <div className="revision-ablation-grid">
        {[{ name: "E1-high · static", on: departure.e1Panic, off: departure.e1NoPanic }, { name: "E3 · threshold withdrawal", on: departure.e3Panic, off: departure.e3NoPanic }].map((item) => <article key={item.name} className="revision-ablation-card">
          <h5>{item.name}</h5>
          {[{ label: t.withPanic, row: item.on }, { label: t.noPanic, row: item.off }].map(({ label, row }) => row ? <div key={label} className="revision-ablation-row"><span>{label}</span><strong><Percent value={row.departure_rate_given_recovery} locale={locale} /></strong><small>{row.departure_paths}/{row.recovered_with_followup} {t.paths} · {fmt(row.mean_departure_episodes_per_recovered_path, locale, 2)} {locale === "es" ? "episodios/trayectoria" : "episodes/path"}</small></div> : <p key={label}>{t.noData}</p>)}
        </article>)}
      </div>
      <p className="revision-takeaway"><strong>{locale === "es" ? "Lectura del mecanismo" : "Mechanism read"}:</strong> {locale === "es" ? "las salidas E1 poco profundas desaparecen sin pánico; las salidas E3 recurrentes permanecen." : "shallow E1 departures disappear without panic; recurrent E3 departures remain."}</p>
    </div>}
    {panel === "capacity" && <div className="revision-panel" role="tabpanel">
      <div className="revision-panel-heading"><div><h4>{t.capacity}</h4><p>{t.shock} {fmt(shock, locale, 2)} · {t.depth} 0.5</p></div>
        <label className="revision-shock"><span>{t.shock}</span><select value={shock} onChange={(event) => setShock(Number(event.target.value) as Shock)}>{shocks.map((value) => <option key={value} value={value}>{fmt(value, locale, 2)}</option>)}</select></label>
      </div>
      {current && fixed ? <div className="revision-capacity-grid">
        {[{ label: t.linked, row: current }, { label: t.fixed, row: fixed }].map(({ label, row }) => <article key={label}><h5>{label}</h5><div><span>{t.recoveryRate}</span><strong><Percent value={Number(row.e3_recovery_rate)} locale={locale} /></strong></div><div><span>{t.allRunsDepart}</span><strong><Percent value={Number(row.e3_departure_rate_per_all_runs)} locale={locale} /></strong></div><div><span>{t.pairedDelta}</span><strong>{fmt(row.post_recovery_area_delta_e3_minus_e1, locale, 4)}</strong><small>[{fmt(row.post_recovery_area_ci95_low, locale, 4)}, {fmt(row.post_recovery_area_ci95_high, locale, 4)}]</small></div></article>)}
      </div> : <p>{t.noData}</p>}
      <p className="revision-takeaway">{locale === "es" ? "El límite fijo sigue acotado por las reservas activas. Este control modifica la regla de capacidad en una sola profundidad; no identifica una descomposición causal general." : "The fixed cap remains bounded by active reserves. This control changes the capacity rule at one depth; it does not identify a general causal decomposition."}</p>
    </div>}
    <footer className="revision-provenance"><span>{t.provenance}</span><p>{t.limitation}</p></footer>
  </section>;
}
