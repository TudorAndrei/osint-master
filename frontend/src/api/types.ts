/**
 * API type definitions matching backend models
 */

// Investigation types
export interface Investigation {
  id: string;
  name: string;
  description?: string;
  created_at: string;
  entity_count: number;
}

export interface InvestigationCreate {
  name: string;
  description?: string;
}

export interface InvestigationList {
  items: Investigation[];
  total: number;
}

// Entity types
export interface Entity {
  id: string;
  schema: string;
  properties: Record<string, string[]>;
}

export interface EntityCreate {
  id?: string;
  schema: string;
  properties: Record<string, string[]>;
}

export interface EntityUpdate {
  properties: Record<string, string[]>;
}

export interface EntityExpand {
  entity: Entity;
  neighbors: Entity[];
  edges: Edge[];
}

export interface DuplicateCandidate {
  left: Entity;
  right: Entity;
  similarity: number;
  reason: string;
}

export interface MergeEntitiesRequest {
  source_ids: string[];
  target_id: string;
  merged_properties?: Record<string, string[]>;
}

export interface MergeEntitiesResponse {
  target: Entity;
  merged_source_ids: string[];
}

// Graph types
export interface GraphNode {
  id: string;
  schema: string;
  label: string;
  properties: Record<string, string[]>;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  schema: string;
  label: string;
  properties: Record<string, string[]>;
}

export interface Edge {
  id: string;
  source: string;
  target: string;
  schema: string;
  properties: Record<string, string[]>;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface GraphPage {
  nodes: GraphNode[];
  edges: GraphEdge[];
  total_nodes: number;
  total_edges: number;
}

// Schema types
export interface SchemaProperty {
  name: string;
  label: string;
  type: string;
  multiple: boolean;
}

export interface Schema {
  name: string;
  label: string;
  plural: string;
  abstract: boolean;
  matchable: boolean;
  properties?: SchemaProperty[];
}

export interface IngestResult {
  processed: number;
  nodes_created: number;
  edges_created: number;
  errors: string[];
  status?: string | null;
  workflow_id?: string | null;
  message?: string | null;
}

export interface ExtractionStatus {
  workflow_id: string;
  status: string;
  result?: Record<string, unknown> | null;
  error?: string | null;
}

export interface YenteSearchResult {
  id: string;
  schema: string;
  caption: string;
  score: number | null;
  datasets: string[];
  properties: Record<string, string[]>;
}

export interface YenteSearchResponse {
  query: string;
  total: number;
  results: YenteSearchResult[];
}

export interface YenteLinkResponse {
  investigation_id: string;
  entity_id: string;
  linked_to: string[];
  links_applied: number;
}
