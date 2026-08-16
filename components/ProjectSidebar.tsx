"use client";

import type { Design } from "../lib/types";

type Props = { designs: Design[]; selectedId?: string; onSelect: (design: Design) => void };

export function ProjectSidebar({ designs, selectedId, onSelect }: Props) {
  return (
    <section className="alternatives" aria-label="Alternativas generadas">
      <h2>Alternativas</h2>
      {designs.length === 0 ? <p className="muted">Genera un diseño para comparar alternativas.</p> : designs.map((design) => (
        <button key={design.id} className={`alternative ${design.id === selectedId ? "active" : ""}`} onClick={() => onSelect(design)}>
          <span>{design.alternative.replace("Alternative ", "")}</span><strong>{design.score.toFixed(0)}/100</strong>
          <small>{design.validation.valid ? "Validada" : "Requiere cambios"}</small>
        </button>
      ))}
    </section>
  );
}
