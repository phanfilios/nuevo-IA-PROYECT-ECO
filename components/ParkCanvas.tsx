"use client";

import { useEffect, useState } from "react";
import type { Design, Zone, ZoneType } from "../lib/types";

const colors: Partial<Record<ZoneType, string>> = {
  CONSERVATION: "#29774d", FOREST: "#215b3d", MEADOW: "#a9d267", WETLAND: "#5ca99c", WATER: "#3c94c9",
  RECREATION: "#f1b956", EDUCATION: "#a98be8", REST_AREA: "#e9d7b4", ENTRANCE: "#34495e",
};
const points = (coords: [number, number][]) => coords.map(([x, y]) => `${x},${y}`).join(" ");

export function ParkCanvas({ design }: { design?: Design }) {
  const [selected, setSelected] = useState<Zone | undefined>();
  useEffect(() => setSelected(undefined), [design?.id]);
  if (!design) return <div className="empty-canvas"><span>PARQUE</span><p>Configura el terreno y genera alternativas.</p></div>;
  const width = Math.max(...design.boundary.map(([x]) => x));
  const height = Math.max(...design.boundary.map(([, y]) => y));
  return (
    <section className="canvas-panel">
      <svg className="park-canvas" viewBox={`-4 -4 ${width + 8} ${height + 8}`} role="img" aria-label="Plano preliminar del parque">
        <rect x="0" y="0" width={width} height={height} className="terrain-boundary" />
        {design.zones.map((zone) => <polygon key={zone.id} points={points(zone.polygon)} fill={colors[zone.type] ?? "#b9c6b5"} className={selected?.id === zone.id ? "zone selected" : "zone"} onClick={() => setSelected(zone)}><title>{zone.type} — {zone.area_m2.toFixed(0)} m²</title></polygon>)}
        {design.paths.map((path) => <polyline key={path.id} points={points(path.coordinates)} className={path.type === "BIKE_PATH" ? "bike-path" : "park-path"} style={{ strokeWidth: path.width_m }}><title>{path.type} — {path.length_m.toFixed(0)} m</title></polyline>)}
      </svg>
      <div className="canvas-info"><span>{width.toFixed(0)} m × {height.toFixed(0)} m</span>{selected ? <span><b>{selected.type}</b> · {selected.area_m2.toFixed(0)} m²</span> : <span>Selecciona una zona</span>}</div>
      <div className="legend">{["CONSERVATION", "MEADOW", "WATER", "RECREATION", "EDUCATION", "ENTRANCE"].map((type) => <span key={type}><i style={{ background: colors[type as ZoneType] }} />{type.replace("_", " ")}</span>)}</div>
    </section>
  );
}
