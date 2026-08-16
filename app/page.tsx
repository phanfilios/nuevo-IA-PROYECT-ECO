"use client";

import { useState } from "react";
import { DesignOptions } from "../components/DesignOptions";
import { ExportPanel } from "../components/ExportPanel";
import { MetricsPanel } from "../components/MetricsPanel";
import { ParkCanvas } from "../components/ParkCanvas";
import { ProjectSidebar } from "../components/ProjectSidebar";
import { TerrainForm } from "../components/TerrainForm";
import { api } from "../lib/api";
import { defaultDraft, type Design, type Project, type ProjectDraft } from "../lib/types";

export default function Home() {
  const [draft, setDraft] = useState<ProjectDraft>(defaultDraft);
  const [project, setProject] = useState<Project>();
  const [designs, setDesigns] = useState<Design[]>([]);
  const [selected, setSelected] = useState<Design>();
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState("Listo para crear una propuesta preliminar.");
  const [error, setError] = useState<string>();

  const updateDraft = (partial: Partial<ProjectDraft>) => setDraft((current) => ({ ...current, ...partial }));
  const generate = async () => {
    setBusy(true); setError(undefined);
    try {
      const activeProject = project ? await api.updateProject(project.id, draft) : await api.createProject(draft);
      const alternatives = await api.generate(activeProject.id);
      setProject(activeProject); setDesigns(alternatives); setSelected(alternatives[0]);
      setNotice("Se generaron tres alternativas y se validaron con el motor geométrico.");
    } catch (cause) { setError(cause instanceof Error ? cause.message : "No se pudo generar el diseño."); }
    finally { setBusy(false); }
  };
  const regenerate = async () => {
    if (!project || !selected) return;
    setBusy(true); setError(undefined);
    try {
      const saved = await api.updateProject(project.id, draft);
      const design = await api.regenerate(selected.id, draft);
      setProject(saved); setSelected(design); setDesigns((items) => items.map((item) => item.id === design.id ? design : item));
      setNotice("La alternativa fue regenerada con los parámetros actuales y validada de nuevo.");
    } catch (cause) { setError(cause instanceof Error ? cause.message : "No se pudo regenerar."); }
    finally { setBusy(false); }
  };
  const validate = async () => {
    if (!selected) return;
    setBusy(true); setError(undefined);
    try {
      const design = await api.validate(selected.id);
      setSelected(design); setDesigns((items) => items.map((item) => item.id === design.id ? design : item));
      setNotice(design.validation.valid ? "Validación aprobada: la exportación está disponible." : "La validación encontró restricciones pendientes.");
    } catch (cause) { setError(cause instanceof Error ? cause.message : "No se pudo validar."); }
    finally { setBusy(false); }
  };
  const newProject = () => { setProject(undefined); setDesigns([]); setSelected(undefined); setDraft(defaultDraft); setNotice("Nuevo proyecto preparado."); setError(undefined); };

  return <main className="app-shell">
    <header className="topbar"><div><p className="eyebrow">PLANIFICACIÓN PRELIMINAR</p><h1>EcoPark <em>AI</em></h1></div><button className="button secondary" onClick={newProject}>Nuevo proyecto</button></header>
    <p className="disclaimer">Los diseños son preliminares y no sustituyen estudios de ingeniería, arquitectura, hidrología, impacto ambiental, normativa local ni permisos.</p>
    <div className="workspace">
      <aside className="configuration">
        <label className="project-name">Proyecto<input value={draft.name} onChange={(e) => updateDraft({ name: e.target.value })} /></label>
        <TerrainForm terrain={draft.terrain} onChange={(terrain) => updateDraft({ terrain })} />
        <DesignOptions requirements={draft.requirements} onChange={(requirements) => updateDraft({ requirements })} />
        <button className="button primary wide" onClick={generate} disabled={busy}>{busy ? "Procesando…" : "Generar 3 diseños"}</button>
        {selected && <div className="inline-actions"><button className="button secondary" onClick={regenerate} disabled={busy}>Regenerar</button><button className="button secondary" onClick={validate} disabled={busy}>Validar</button></div>}
      </aside>
      <section className="design-space"><div className="status" role="status">{error ? <span className="error">{error}</span> : notice}</div><ParkCanvas design={selected} /></section>
    </div>
    <div className="lower-grid"><MetricsPanel design={selected} /><ProjectSidebar designs={designs} selectedId={selected?.id} onSelect={setSelected} /><ExportPanel design={selected} /></div>
    {selected && !selected.validation.valid && <section className="validation-errors"><h2>Restricciones pendientes</h2><ul>{selected.validation.errors.map((item) => <li key={item}>{item}</li>)}</ul></section>}
  </main>;
}
