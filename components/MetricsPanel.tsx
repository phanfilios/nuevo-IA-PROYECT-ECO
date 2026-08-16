"use client";

import type { Design } from "../lib/types";

const metric = (label: string, value: string) => <div className="metric" key={label}><span>{label}</span><b>{value}</b></div>;

export function MetricsPanel({ design }: { design?: Design }) {
  if (!design) return <section className="metrics"><h2>Métricas</h2><p className="muted">Las métricas se calculan en el backend tras generar un diseño.</p></section>;
  const m = design.metrics;
  return <section className="metrics"><h2>Métricas calculadas</h2><div className="metric-grid">
    {metric("Área total", `${m.total_area_m2.toLocaleString()} m²`)}
    {metric("Conservación", `${m.conservation_area_m2.toLocaleString()} m² · ${m.conservation_percentage}%`)}
    {metric("Recreación", `${m.recreation_area_m2.toLocaleString()} m² · ${m.recreation_percentage}%`)}
    {metric("Agua", `${m.water_area_m2.toLocaleString()} m²`)}
    {metric("Senderos", `${(m.path_length_m / 1000).toFixed(2)} km`)}
    {metric("Zonas", String(m.zone_count))}
    {metric("Conectividad", `${m.connectivity_index.toFixed(0)}%`)}
    {metric("Índice ecológico", `${m.ecological_index.toFixed(0)}/100`)}
    {metric("Puntuación", `${m.overall_score.toFixed(0)}/100`)}
  </div></section>;
}
