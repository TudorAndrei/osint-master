/**
 * API client for OSINT Master backend
 */

import type {
  DuplicateCandidate,
  Entity,
  EntityCreate,
  EntityExpand,
  ExtractionStatus,
  MergeEntitiesRequest,
  MergeEntitiesResponse,
  EntityUpdate,
  GraphPage,
  IngestResult,
  Investigation,
  InvestigationCreate,
  InvestigationList,
  NotebookDocument,
  NotebookUpdate,
  Schema,
  YenteLinkResponse,
  YenteSearchResponse,
} from "./types";

const API_BASE = "/api";

type AuthTokenGetter = () => Promise<string | null>;

let authTokenGetter: AuthTokenGetter = async () => null;

export function setAuthTokenGetter(getter: AuthTokenGetter) {
  authTokenGetter = getter;
}

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.text();
    throw new ApiError(response.status, error || response.statusText);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json();
}

async function buildHeaders(baseHeaders?: HeadersInit): Promise<Headers> {
  const headers = new Headers(baseHeaders);
  const token = await authTokenGetter();
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  return headers;
}

export async function buildAuthHeaders(baseHeaders?: HeadersInit): Promise<Headers> {
  return buildHeaders(baseHeaders);
}

export const apiClient = {
  async get<T>(path: string): Promise<T> {
    const response = await fetch(`${API_BASE}${path}`, {
      headers: await buildHeaders(),
    });
    return handleResponse<T>(response);
  },

  async post<T>(path: string, body?: unknown): Promise<T> {
    const response = await fetch(`${API_BASE}${path}`, {
      method: "POST",
      headers: await buildHeaders({ "Content-Type": "application/json" }),
      body: body ? JSON.stringify(body) : undefined,
    });
    return handleResponse<T>(response);
  },

  async put<T>(path: string, body: unknown): Promise<T> {
    const response = await fetch(`${API_BASE}${path}`, {
      method: "PUT",
      headers: await buildHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify(body),
    });
    return handleResponse<T>(response);
  },

  async delete<T>(path: string): Promise<T> {
    const response = await fetch(`${API_BASE}${path}`, {
      method: "DELETE",
      headers: await buildHeaders(),
    });
    return handleResponse<T>(response);
  },

  async upload<T>(path: string, file: File): Promise<T> {
    const formData = new FormData();
    formData.append("file", file);
    const response = await fetch(`${API_BASE}${path}`, {
      method: "POST",
      headers: await buildHeaders(),
      body: formData,
    });
    return handleResponse<T>(response);
  },

  listInvestigations() {
    return this.get<InvestigationList>("/investigations");
  },

  createInvestigation(payload: InvestigationCreate) {
    return this.post<Investigation>("/investigations", payload);
  },

  deleteInvestigation(id: string) {
    return this.delete<void>(`/investigations/${id}`);
  },

  listEntities(investigationId: string, search?: string) {
    const query = search ? `?search=${encodeURIComponent(search)}` : "";
    return this.get<Entity[]>(`/investigations/${investigationId}/entities${query}`);
  },

  createEntity(investigationId: string, payload: EntityCreate) {
    return this.post<Entity>(`/investigations/${investigationId}/entities`, payload);
  },

  deleteEntity(investigationId: string, entityId: string) {
    return this.delete<void>(`/investigations/${investigationId}/entities/${entityId}`);
  },

  updateEntity(investigationId: string, entityId: string, payload: EntityUpdate) {
    return this.put<Entity>(`/investigations/${investigationId}/entities/${entityId}`, payload);
  },

  expandEntity(investigationId: string, entityId: string) {
    return this.get<EntityExpand>(`/investigations/${investigationId}/entities/${entityId}/expand`);
  },

  findDuplicateCandidates(investigationId: string, schema?: string, threshold = 0.7, limit = 100) {
    const params = new URLSearchParams({ threshold: String(threshold), limit: String(limit) });
    if (schema && schema !== "all") {
      params.set("schema", schema);
    }
    return this.get<DuplicateCandidate[]>(
      `/investigations/${investigationId}/entities/deduplicate/candidates?${params.toString()}`
    );
  },

  mergeEntities(investigationId: string, payload: MergeEntitiesRequest) {
    return this.post<MergeEntitiesResponse>(`/investigations/${investigationId}/entities/merge`, payload);
  },

  getGraph(investigationId: string, skip = 0, limit = 500) {
    return this.get<GraphPage>(
      `/investigations/${investigationId}/graph?skip=${skip}&limit=${limit}`
    );
  },

  getNotebook(investigationId: string) {
    return this.get<NotebookDocument>(`/investigations/${investigationId}/notebook`);
  },

  saveNotebook(investigationId: string, payload: NotebookUpdate) {
    return this.put<NotebookDocument>(`/investigations/${investigationId}/notebook`, payload);
  },

  ingestFile(investigationId: string, file: File) {
    return this.upload<IngestResult>(`/investigations/${investigationId}/ingest`, file);
  },

  getIngestStatus(investigationId: string, workflowId: string) {
    return this.get<ExtractionStatus>(
      `/investigations/${investigationId}/ingest/${workflowId}/status`
    );
  },

  listSchemata() {
    return this.get<Schema[]>("/schema");
  },

  searchYente(query: string, limit = 20) {
    const params = new URLSearchParams({ query, limit: String(limit) });
    return this.get<YenteSearchResponse>(`/enrich/yente?${params.toString()}`);
  },

  linkYenteEntity(investigationId: string, entityId: string) {
    return this.post<YenteLinkResponse>(`/enrich/yente/link/${investigationId}/${entityId}`);
  },
};
