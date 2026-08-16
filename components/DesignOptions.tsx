"use client";

import type { ParkRequirements } from "../lib/types";

type Props = { requirements: ParkRequirements; onChange: (requirements: ParkRequirements) => void };

export function DesignOptions({ requirements, onChange }: Props) {
  const update = <K extends keyof ParkRequirements>(key: K, value: ParkRequirements[K]) => onChange({ ...requirements, [key]: value });
  const check = (key: keyof ParkRequirements, label: string) => (
    <label className="check"><input type="checkbox" checked={Boolean(requirements[key])} onChange={(e) => update(key, e.target.checked as never)} />{label}</label>
  );
  return (
    <fieldset className="form-section">
      <legend>Objetivos</legend>
      <div className="two-columns">
        <label>Conservación (%)<input type="number" min="5" max="85" value={requirements.conservation_percentage} onChange={(e) => update("conservation_percentage", Number(e.target.value))} /></label>
        <label>Recreación (%)<input type="number" min="0" max="60" value={requirements.recreation_percentage} onChange={(e) => update("recreation_percentage", Number(e.target.value))} /></label>
      </div>
      <label>Educación (%)<input type="number" min="0" max="30" value={requirements.education_percentage} onChange={(e) => update("education_percentage", Number(e.target.value))} /></label>
      <label>Biodiversidad objetivo (1–10)<input type="number" min="1" max="10" value={requirements.target_biodiversity} onChange={(e) => update("target_biodiversity", Number(e.target.value))} /></label>
      <label>Presupuesto estimado (opcional)<input type="number" min="1" placeholder="Sin límite" value={requirements.estimated_budget ?? ""} onChange={(e) => update("estimated_budget", e.target.value ? Number(e.target.value) : null)} /></label>
      <label>Mantenimiento
        <select value={requirements.maintenance_level} onChange={(e) => update("maintenance_level", e.target.value as ParkRequirements["maintenance_level"])}>
          <option value="low">Bajo</option><option value="medium">Medio</option><option value="high">Alto</option>
        </select>
      </label>
      <div className="checks">
        {check("accessibility_required", "Accesibilidad")}
        {check("water_features_required", "Agua")}
        {check("pedestrian_paths_required", "Senderos peatonales")}
        {check("bicycle_paths_required", "Ruta ciclista")}
        {check("lighting_required", "Iluminación")}
      </div>
    </fieldset>
  );
}
