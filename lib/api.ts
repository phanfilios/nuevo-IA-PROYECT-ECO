import type { Design, Project, ProjectDraft } from "./types";

// IPv4 loopback avoids browsers that resolve localhost to an unavailable IPv6 address.
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail ?? "La solicitud no se pudo completar");
  }
  return response.status === 204 ? (undefined as T) : response.json() as Promise<T>;
}

export const api = {
  createProject: (draft: ProjectDraft) => request<Project>("/projects", { method: "POST", body: JSON.stringify(draft) }),
  updateProject: (id: string, draft: ProjectDraft) => request<Project>(`/projects/${id}`, { method: "PATCH", body: JSON.stringify(draft) }),
  generate: (projectId: string) => request<Design[]>(`/projects/${projectId}/designs/generate`, { method: "POST", body: JSON.stringify({ alternatives: 3 }) }),
  regenerate: (designId: string, draft: ProjectDraft) => request<Design>(`/designs/${designId}/regenerate`, { method: "POST", body: JSON.stringify({ requirements: draft.requirements }) }),
  validate: (designId: string) => request<Design>(`/designs/${designId}/validate`, { method: "POST", body: "{}" }),
  exportUrl: (designId: string, format: "dxf" | "geojson" | "svg") => `${API_URL}/designs/${designId}/export/${format}`,
};
