"use client";

import type { TerrainInput } from "../lib/types";

type Props = { terrain: TerrainInput; onChange: (terrain: TerrainInput) => void };

export function TerrainForm({ terrain, onChange }: Props) {
  const update = <K extends keyof TerrainInput>(key: K, value: TerrainInput[K]) => onChange({ ...terrain, [key]: value });
  return (
    <fieldset className="form-section">
      <legend>Terreno</legend>
      <div className="two-columns">
        <label>Ancho (m)<input type="number" min="6" value={terrain.width_m} onChange={(e) => update("width_m", Number(e.target.value))} /></label>
        <label>Largo (m)<input type="number" min="6" value={terrain.length_m} onChange={(e) => update("length_m", Number(e.target.value))} /></label>
      </div>
      <label>Pendiente (%)<input type="number" min="0" max="100" value={terrain.slope_percent} onChange={(e) => update("slope_percent", Number(e.target.value))} /></label>
      <div className="two-columns">
        <label>Clima<input value={terrain.climate} onChange={(e) => update("climate", e.target.value)} /></label>
        <label>Suelo<input value={terrain.soil_type} onChange={(e) => update("soil_type", e.target.value)} /></label>
      </div>
      <label>Disponibilidad de agua
        <select value={terrain.water_availability} onChange={(e) => update("water_availability", e.target.value)}>
          <option value="low">Baja</option><option value="medium">Media</option><option value="high">Alta</option>
        </select>
      </label>
      <label>Vegetación existente<input value={terrain.existing_vegetation} onChange={(e) => update("existing_vegetation", e.target.value)} /></label>
      <label>Estructuras existentes<input value={terrain.existing_structures} onChange={(e) => update("existing_structures", e.target.value)} /></label>
    </fieldset>
  );
}
