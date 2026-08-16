"use client";

import { api } from "../lib/api";
import type { Design } from "../lib/types";

export function ExportPanel({ design }: { design?: Design }) {
  if (!design) return <section className="export-panel"><h2>Exportar</h2><p className="muted">Selecciona una alternativa validada.</p></section>;
  const disabled = !design.validation.valid;
  return <section className="export-panel"><h2>Exportar</h2><div className="export-actions">
    {(["dxf", "geojson", "svg"] as const).map((format) => <a key={format} href={disabled ? undefined : api.exportUrl(design.id, format)} aria-disabled={disabled} className={`button secondary ${disabled ? "disabled" : ""}`}>.{format.toUpperCase()}</a>)}
  </div>{disabled ? <p className="error">La validación debe aprobarse antes de exportar.</p> : <p className="muted">DXF se exporta por capas compatibles con CAD. No controla AutoCAD directamente.</p>}</section>;
}
