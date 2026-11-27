import { useMemo, useState } from "react";
import type { Locale } from "@tesis/content";
import findings from "../../data/hybrid-findings.json";

type Metric = "rollout_e" | "one_e" | "one_z" | "rollout_z";

const messages = {
  en: {
    kicker: "New held-out analysis · synthetic",
    title: "Does the band-aware map travel to unseen conditions?",
    intro: "An affine map is compared with a hybrid map that changes its correction outside the no-arbitrage band. Both are fitted on one shock/depth grid, then evaluated on new seeds and held-out shock/depth cells.",
    rolloutE: "Rollout · price error",
    oneE: "One-step · price error",
    oneZ: "One-step · flow pressure",
    rolloutZ: "Rollout · flow pressure",
    favorable: "above zero: hybrid lower error",
    unfavorable: "below zero: affine lower error",
    depth: "Pool depth",
    condition: "Operating condition",
    conditionNames: {
      "E0-arb-off-static": "Arbitrage off",
      "E1-arb-low-static": "Low capacity",
      "E1-arb-high-static": "High capacity",
      "E3-adaptive-lp-high-arb": "Threshold-withdrawal LP + high capacity"
    },
    primary: "Primary held-out result",
    improvement: "mean rollout MAE improvement",
    interval: "95% paired seed-bootstrap interval",
    baseline: "L0 mean MAE",
    hybrid: "Hyb mean MAE",
    seeds: "of seeds improved",
    details: "Inspect all 32 held-out cells",
    shock: "Shock",
    cells: "Cells",
    gain: "L0 − Hyb error",
    procedure: "Procedure and scope",
    procedureText: "Selection: seeds 3000–3299, depth 1, shocks ±0.10. Confirmation: seeds 4000–4299, depths 0.5 and 2, shocks ±0.05 and ±0.20. Rollouts receive the realized future synthetic CEX shock path (an oracle input), so this is not a real-time forecast. It tests prediction inside this simulator; it does not validate markets or prove stability of the full hybrid/stochastic system.",
    model: "Hyb adds signed error beyond the configured band and an outside-band flow interaction. Capacity and LP policy are held fixed within each fitted condition.",
    flowLimit: "The z forecast receives no future noise/trend draw; its target includes unobserved stochastic flow.",
    run: "Analysis run",
    positive: "positive values favor Hyb",
    negative: "negative values favor L0"
  },
  es: {
    kicker: "Nuevo análisis reservado · sintético",
    title: "¿El mapa con banda funciona en condiciones no vistas?",
    intro: "Se compara un mapa afín con uno híbrido cuya corrección cambia fuera de la banda sin arbitraje. Ambos se ajustan en una cuadrícula de choques y profundidad; después se evalúan con semillas y celdas reservadas.",
    rolloutE: "Recursivo · error de precio",
    oneE: "Un paso · error de precio",
    oneZ: "Un paso · presión de flujo",
    rolloutZ: "Recursivo · presión de flujo",
    favorable: "sobre cero: menor error híbrido",
    unfavorable: "bajo cero: menor error afín",
    depth: "Profundidad del pool",
    condition: "Condición operativa",
    conditionNames: {
      "E0-arb-off-static": "Arbitraje desactivado",
      "E1-arb-low-static": "Capacidad baja",
      "E1-arb-high-static": "Capacidad alta",
      "E3-adaptive-lp-high-arb": "LP con retiro por umbral + capacidad alta"
    },
    primary: "Resultado principal reservado",
    improvement: "mejora media en MAE recursivo",
    interval: "intervalo bootstrap pareado por semilla del 95 %",
    baseline: "MAE medio L0",
    hybrid: "MAE medio Hyb",
    seeds: "de semillas mejoraron",
    details: "Ver las 32 celdas reservadas",
    shock: "Choque",
    cells: "Celdas",
    gain: "Error L0 − Hyb",
    procedure: "Procedimiento y alcance",
    procedureText: "Selección: semillas 3000–3299, profundidad 1 y choques ±0,10. Confirmación: semillas 4000–4299, profundidades 0,5 y 2, y choques ±0,05 y ±0,20. Los rollouts reciben la trayectoria futura realizada de choques CEX sintéticos (una entrada oráculo), así que no son pronósticos en tiempo real. Esto evalúa predicción dentro del simulador; no valida mercados ni demuestra estabilidad del sistema híbrido/estocástico completo.",
    model: "Hyb añade el error firmado que excede la banda configurada y una interacción de flujo fuera de banda. La capacidad y la política LP se mantienen fijas dentro de cada condición ajustada.",
    flowLimit: "La predicción de z no recibe el sorteo futuro de ruido o tendencia; su objetivo incluye un flujo estocástico no observado.",
    run: "Corrida de análisis",
    positive: "los valores positivos favorecen Hyb",
    negative: "los valores negativos favorecen L0"
  }
} as const;

const metricLabels: Record<Locale, Record<Metric, string>> = {
  en: { rollout_e: "rollout · price error", one_e: "one-step · price error", one_z: "one-step · flow pressure", rollout_z: "rollout · flow pressure" },
  es: { rollout_e: "recursivo · error de precio", one_e: "un paso · error de precio", one_z: "un paso · presión de flujo", rollout_z: "recursivo · presión de flujo" }
};

function format(value: number, locale: Locale, digits = 5) {
  return new Intl.NumberFormat(locale === "es" ? "es-ES" : "en-US", { maximumFractionDigits: digits, minimumFractionDigits: digits }).format(value);
}

export default function HybridEvidence({ locale }: { locale: Locale }) {
  const copy = messages[locale];
  const [metric, setMetric] = useState<Metric>("rollout_e");
  const [expanded, setExpanded] = useState(false);
  const cells = findings.shock_depth_condition_cells;
  const displayRows = useMemo(() => {
    const groups = new Map<string, { depth: number; condition: string; values: number[] }>();
    cells.forEach((cell) => {
      const key = `${cell.depth_scale}|${cell.condition}`;
      const group = groups.get(key) ?? { depth: cell.depth_scale, condition: cell.condition, values: [] };
      group.values.push(cell[`mean_improvement_${metric}`]);
      groups.set(key, group);
    });
    return [...groups.values()].map((group) => ({ ...group, value: group.values.reduce((sum, value) => sum + value, 0) / group.values.length }))
      .sort((a, b) => a.depth - b.depth || a.condition.localeCompare(b.condition));
  }, [cells, metric]);
  const max = Math.max(...displayRows.map((row) => Math.abs(row.value)), 1e-9);
  const chart = { width: 780, rowHeight: 34, left: 250, center: 510, range: 220 };
  const primary = findings.summary;
  const primaryMetrics = primary.metric_summary.rollout_e;
  const shownCells = [...cells].sort((a, b) => a.depth_scale - b.depth_scale || a.shock_log_return - b.shock_log_return || a.condition.localeCompare(b.condition));

  return <section className="hybrid-evidence" aria-labelledby="hybrid-evidence-title">
    <div className="hybrid-evidence-heading">
      <div><p className="eyebrow">{copy.kicker}</p><h3 id="hybrid-evidence-title">{copy.title}</h3><p>{copy.intro}</p></div>
      <span className="hybrid-analysis-tag">L0 ↔ Hyb</span>
    </div>
    <div className="hybrid-primary">
      <div className="hybrid-primary-number"><span>{copy.primary}</span><strong>{format(primary.mean_improvement_rollout_mae_e, locale, 6)}</strong><small>{copy.improvement}</small></div>
      <div className="hybrid-primary-stats">
        <div><span>{copy.interval}</span><strong>[{format(primary.bootstrap_95pct_ci_low, locale, 6)}, {format(primary.bootstrap_95pct_ci_high, locale, 6)}]</strong></div>
        <div><span>{copy.baseline}</span><strong>{format(primaryMetrics.L0_mean_mae, locale)}</strong></div>
        <div><span>{copy.hybrid}</span><strong>{format(primaryMetrics.Hyb_mean_mae, locale)}</strong></div>
        <div><span>{copy.seeds}</span><strong>{format(primary.share_seeds_hyb_lower_rollout_mae_e * 100, locale, 1)}%</strong></div>
      </div>
    </div>
    <div className="hybrid-chart-heading">
      <div><span>{copy.gain}</span><small>{copy.positive} · {copy.negative}</small></div>
      <label className="hybrid-metric-select"><span className="sr-only">{locale === "es" ? "Métrica del gráfico" : "Chart metric"}</span>
        <select value={metric} onChange={(event) => setMetric(event.target.value as Metric)}>
          {(Object.keys(metricLabels[locale]) as Metric[]).map((key) => <option key={key} value={key}>{metricLabels[locale][key]}</option>)}
        </select>
      </label>
    </div>
    <div className="hybrid-chart-wrap">
      <svg viewBox={`0 0 ${chart.width} ${displayRows.length * chart.rowHeight + 18}`} role="img" aria-label={`${copy.gain}: ${metricLabels[locale][metric]}`}>
        <line x1={chart.center} x2={chart.center} y1="0" y2={displayRows.length * chart.rowHeight} className="hybrid-zero" />
        {displayRows.map((row, index) => {
          const y = index * chart.rowHeight + 8;
          const barWidth = Math.abs(row.value / max) * chart.range;
          const x = row.value >= 0 ? chart.center : chart.center - barWidth;
          const name = copy.conditionNames[row.condition as keyof typeof copy.conditionNames];
          return <g key={`${row.depth}-${row.condition}`}>
            <text x="0" y={y + 14} className="hybrid-row-label">{name}</text>
            <text x={chart.left} y={y + 14} className="hybrid-row-depth">{copy.depth} {row.depth}</text>
            <rect x={x} y={y} width={Math.max(barWidth, 1)} height="17" rx="2" className={row.value >= 0 ? "hybrid-bar positive" : "hybrid-bar negative"} />
            <text x={row.value >= 0 ? x + barWidth + 6 : x - 6} y={y + 13} textAnchor={row.value >= 0 ? "start" : "end"} className="hybrid-value-label">{format(row.value, locale, 5)}</text>
          </g>;
        })}
      </svg>
    </div>
    <p className="hybrid-model-note">{copy.model} {copy.flowLimit}</p>
    <details className="hybrid-cell-details" open={expanded} onToggle={(event) => setExpanded(event.currentTarget.open)}>
      <summary>{copy.details}</summary>
      <div className="hybrid-table-scroll"><table>
        <thead><tr><th>{copy.depth}</th><th>{copy.shock}</th><th>{copy.condition}</th><th>{metricLabels[locale][metric]}</th></tr></thead>
        <tbody>{shownCells.map((cell, index) => <tr key={index}><td>{cell.depth_scale}</td><td>{cell.shock_log_return > 0 ? "+" : ""}{format(cell.shock_log_return, locale, 2)}</td><td>{copy.conditionNames[cell.condition as keyof typeof copy.conditionNames]}</td><td>{format(cell[`mean_improvement_${metric}`], locale, 6)}</td></tr>)}</tbody>
      </table></div>
    </details>
    <div className="hybrid-procedure"><span>{copy.procedure}</span><p>{copy.procedureText}</p><small>{copy.run}: {findings.run_id} · {findings.analysis_version} · {primary.confirmation_trajectory_count} trajectories · {primary.seed_count} seeds</small></div>
  </section>;
}
