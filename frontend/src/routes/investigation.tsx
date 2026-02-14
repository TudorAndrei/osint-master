import { useEffect, useMemo, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { useChat } from "@ai-sdk/react";
import { DefaultChatTransport } from "ai";
import cytoscape, { type Core, type ElementDefinition, type LayoutOptions } from "cytoscape";
import fcose from "cytoscape-fcose";
import {
  Network,
  Notebook,
  Map as MapIcon,
  Search,
  Trash2,
  Upload,
  X,
  ZoomIn,
  ZoomOut,
} from "lucide-react";
import { apiClient, ApiError, buildAuthHeaders } from "@/api/client";
import { Button } from "@/components/ui/button";
import type {
  DuplicateCandidate,
  Entity,
  EntityCreate,
  GraphEdge,
  GraphNode,
  GraphPage,
  YenteSearchResult,
} from "@/api/types";
import EntityMap from "@/components/investigation/EntityMap";
import InvestigationChatbot from "@/components/investigation/InvestigationChatbot";
import NotebookCanvas from "@/components/investigation/NotebookCanvas";

cytoscape.use(fcose);

const FCOSE_OPTIONS = {
  name: "fcose",
  quality: "proof",
  randomize: true,
  animate: true,
  animationDuration: 650,
  fit: true,
  padding: 48,
  nodeDimensionsIncludeLabels: true,
  uniformNodeDimensions: false,
  packComponents: true,
  step: "all",
  samplingType: true,
  sampleSize: 25,
  nodeRepulsion: () => 9800,
  idealEdgeLength: () => 150,
  edgeElasticity: () => 0.32,
  nestingFactor: 0.1,
  gravity: 0.06,
  numIter: 2500,
  tile: false,
  tilingPaddingVertical: 10,
  tilingPaddingHorizontal: 10,
  gravityRangeCompound: 1.5,
  gravityCompound: 1.0,
  gravityRange: 3.8,
  initialEnergyOnIncremental: 0.3,
};

const SCHEMA_COLORS: Record<string, string> = {
  Person: "#0f766e",
  Company: "#b45309",
  Document: "#374151",
  Ownership: "#be123c",
  Directorship: "#7c2d12",
};

const SCHEMA_ICON_SVG: Record<string, string> = {
  Person:
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#f8fafc" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="3.2"/><path d="M5.5 19.5c1.3-3.5 3.6-5.3 6.5-5.3s5.2 1.8 6.5 5.3"/></svg>',
  Company:
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#f8fafc" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 19.5h15"/><path d="M6.5 19.5v-11h7v11"/><path d="M13.5 19.5v-8h4v8"/><path d="M8.5 10.5h1"/><path d="M8.5 13.5h1"/><path d="M10.5 10.5h1"/><path d="M10.5 13.5h1"/></svg>',
  Document:
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#f8fafc" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M7.5 3.5h7l4 4v13h-11z"/><path d="M14.5 3.5v4h4"/><path d="M9.5 12.5h6"/><path d="M9.5 15.5h6"/></svg>',
  Ownership:
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#f8fafc" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3.5v17"/><path d="M8.2 7.4c0-1.7 1.5-3.1 3.8-3.1s3.8 1.2 3.8 2.9c0 1.4-.8 2.3-2.8 2.8l-1.9.4c-1.6.4-2.6 1.2-2.6 2.7 0 1.9 1.8 3.2 4.3 3.2 2.1 0 3.8-.9 4.5-2.3"/></svg>',
  Directorship:
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#f8fafc" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 4.5v10"/><path d="M8 8.5l4-4 4 4"/><path d="M5 19.5h14"/></svg>',
};

const SUPPORTED_UPLOAD_GROUPS = {
  ftm: [".ftm", ".ijson", ".json", ".ndjson"],
  documents: [
    ".pdf",
    ".docx",
    ".doc",
    ".xlsx",
    ".xls",
    ".pptx",
    ".eml",
    ".msg",
    ".html",
    ".htm",
    ".txt",
    ".md",
    ".rtf",
    ".png",
    ".jpg",
    ".jpeg",
    ".tiff",
  ],
} as const;

const SUPPORTED_UPLOAD_ACCEPT = [
  ...SUPPORTED_UPLOAD_GROUPS.ftm,
  ...SUPPORTED_UPLOAD_GROUPS.documents,
].join(",");

const CHAT_SUGGESTIONS = [
  "Summarize this investigation in 5 bullets",
  "Who are the key people and companies here?",
  "Show strongest relationships around the selected entity",
  "List likely duplicate entities I should review",
];

function schemaIconDataUri(schema: string): string {
  const svg =
    SCHEMA_ICON_SVG[schema] ||
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#f8fafc" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/></svg>';
  return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`;
}

function nodeLabel(node: GraphNode): string {
  return node.properties.name?.[0] || node.label || node.id;
}

function entityLabel(entity: Entity): string {
  return entity.properties.name?.[0] || entity.id;
}

function edgeLabel(edge: GraphEdge): string {
  const schema = edge.schema.trim();
  if (!schema) {
    return "";
  }

  const normalized = schema.toUpperCase();
  if (normalized === "UNKNOWNLINK" || normalized === "RELATED") {
    return "";
  }

  return schema;
}

function mergedProperties(left: Entity, right: Entity): Record<string, string[]> {
  const merged: Record<string, string[]> = {};
  const keys = new Set([...Object.keys(left.properties), ...Object.keys(right.properties)]);
  for (const key of keys) {
    const values = [...(left.properties[key] ?? []), ...(right.properties[key] ?? [])];
    merged[key] = Array.from(new Set(values));
  }
  return merged;
}

function yenteResultToEntity(result: YenteSearchResult): EntityCreate {
  const properties = { ...result.properties };
  if (!properties.name?.length && result.caption.trim()) {
    properties.name = [result.caption.trim()];
  }

  return {
    id: result.id,
    schema: result.schema,
    properties,
  };
}

function progressFromStatus(status: string | null | undefined): number {
  const value = (status ?? "").toUpperCase();
  if (value === "SUCCESS" || value === "COMPLETED") {
    return 100;
  }
  if (value === "RUNNING") {
    return 70;
  }
  if (value === "PENDING" || value === "QUEUED" || value === "PROCESSING") {
    return 25;
  }
  if (value === "ERROR" || value === "FAILED" || value === "CANCELLED") {
    return 100;
  }
  return 15;
}

export default function InvestigationPage() {
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const canvasRef = useRef<HTMLDivElement | null>(null);
  const cyRef = useRef<Core | null>(null);

  const [selectedEntityId, setSelectedEntityId] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [schemaFilter, setSchemaFilter] = useState("all");
  const [layout, setLayout] = useState<"fcose" | "grid" | "circle">("fcose");
  const [viewMode, setViewMode] = useState<"graph" | "map" | "notebook">("graph");
  const [dragActive, setDragActive] = useState(false);
  const [yenteQuery, setYenteQuery] = useState("");
  const [yenteResults, setYenteResults] = useState<YenteSearchResult[]>([]);
  const [yenteError, setYenteError] = useState<string | null>(null);
  const [addEntityError, setAddEntityError] = useState<string | null>(null);
  const [deleteEntityError, setDeleteEntityError] = useState<string | null>(null);
  const [ingestWorkflowId, setIngestWorkflowId] = useState<string | null>(null);
  const [addingEntityId, setAddingEntityId] = useState<string | null>(null);
  const [isEntityDetailsOpen, setIsEntityDetailsOpen] = useState(false);
  const [duplicateCandidates, setDuplicateCandidates] = useState<DuplicateCandidate[]>([]);
  const [duplicateThreshold, setDuplicateThreshold] = useState(0.7);
  const [duplicateError, setDuplicateError] = useState<string | null>(null);
  const [activeCandidate, setActiveCandidate] = useState<DuplicateCandidate | null>(null);
  const [mergeTargetId, setMergeTargetId] = useState<string | null>(null);
  const [chatInput, setChatInput] = useState("");

  const graphQuery = useQuery({
    queryKey: ["graph", id],
    queryFn: () => apiClient.getGraph(id!),
    enabled: Boolean(id),
  });

  const schemataQuery = useQuery({
    queryKey: ["schemata"],
    queryFn: () => apiClient.listSchemata(),
  });

  const {
    messages: chatMessages,
    sendMessage,
    status: chatStatus,
    error: chatError,
    stop: stopChat,
  } = useChat({
    id: id ? `investigation-${id}` : "investigation",
    transport: new DefaultChatTransport({
      api: "/api/chat",
      body: () => ({
        investigationId: id,
      }),
      fetch: async (input, init) => {
        const headers = await buildAuthHeaders(init?.headers);
        return fetch(input, {
          ...init,
          headers,
        });
      },
    }),
  });

  const expandMutation = useMutation({
    mutationFn: (entityId: string) => apiClient.expandEntity(id!, entityId),
    onSuccess: (expanded) => {
      queryClient.setQueryData<GraphPage | undefined>(["graph", id], (prev) => {
        if (!prev) {
          return prev;
        }

        const nodeMap = new Map<string, GraphNode>(prev.nodes.map((node: GraphNode) => [node.id, node]));
        nodeMap.set(expanded.entity.id, {
          id: expanded.entity.id,
          schema: expanded.entity.schema,
          label: expanded.entity.properties.name?.[0] ?? expanded.entity.id,
          properties: expanded.entity.properties,
        });
        expanded.neighbors.forEach((neighbor) => {
          nodeMap.set(neighbor.id, {
            id: neighbor.id,
            schema: neighbor.schema,
            label: neighbor.properties.name?.[0] ?? neighbor.id,
            properties: neighbor.properties,
          });
        });

        const edgeMap = new Map<string, GraphEdge>(prev.edges.map((edge: GraphEdge) => [edge.id, edge]));
        expanded.edges.forEach((edge) => {
          edgeMap.set(edge.id, {
            id: edge.id,
            source: edge.source,
            target: edge.target,
            schema: edge.schema,
            label: edge.schema,
            properties: edge.properties,
          });
        });

        return {
          ...prev,
          nodes: Array.from(nodeMap.values()),
          edges: Array.from(edgeMap.values()),
          total_nodes: nodeMap.size,
          total_edges: edgeMap.size,
        };
      });
    },
  });

  const uploadMutation = useMutation({
    mutationFn: (file: File) => apiClient.ingestFile(id!, file),
    onSuccess: (result) => {
      if (result.workflow_id) {
        setIngestWorkflowId(result.workflow_id);
        return;
      }
      void queryClient.invalidateQueries({ queryKey: ["graph", id] });
      void queryClient.invalidateQueries({ queryKey: ["investigations"] });
    },
  });

  const ingestStatusQuery = useQuery({
    queryKey: ["ingest-status", id, ingestWorkflowId],
    queryFn: () => apiClient.getIngestStatus(id!, ingestWorkflowId!),
    enabled: Boolean(id && ingestWorkflowId),
    refetchInterval: (query) => {
      const status = (query.state.data?.status ?? "").toUpperCase();
      if (status === "SUCCESS" || status === "COMPLETED" || status === "ERROR" || status === "FAILED") {
        return false;
      }
      return 1200;
    },
  });

  useEffect(() => {
    const status = (ingestStatusQuery.data?.status ?? "").toUpperCase();
    if (status === "SUCCESS" || status === "COMPLETED") {
      void queryClient.invalidateQueries({ queryKey: ["graph", id] });
      void queryClient.invalidateQueries({ queryKey: ["investigations"] });
    }
  }, [id, ingestStatusQuery.data?.status, queryClient]);

  const yenteSearchMutation = useMutation({
    mutationFn: () => apiClient.searchYente(yenteQuery.trim(), 20),
    onSuccess: (response) => {
      setYenteResults(response.results);
      setYenteError(null);
    },
    onError: (error: unknown) => {
      setYenteResults([]);
      setYenteError(error instanceof ApiError ? error.message : "Could not query Yente");
    },
  });

  const addYenteEntityMutation = useMutation({
    mutationFn: (result: YenteSearchResult) => apiClient.createEntity(id!, yenteResultToEntity(result)),
    onSuccess: async (createdEntity) => {
      setAddEntityError(null);
      setSelectedEntityId(createdEntity.id);
      try {
        await apiClient.linkYenteEntity(id!, createdEntity.id);
      } catch (error) {
        setAddEntityError(
          error instanceof ApiError
            ? `Entity added, but auto-linking failed: ${error.message}`
            : "Entity added, but auto-linking failed"
        );
      }
      void queryClient.invalidateQueries({ queryKey: ["graph", id] });
      void queryClient.invalidateQueries({ queryKey: ["investigations"] });
    },
    onError: (error: unknown) => {
      setAddEntityError(error instanceof ApiError ? error.message : "Could not add entity");
    },
    onSettled: () => {
      setAddingEntityId(null);
    },
  });

  const deleteEntityMutation = useMutation({
    mutationFn: (entityId: string) => apiClient.deleteEntity(id!, entityId),
    onSuccess: (_data, entityId) => {
      setDeleteEntityError(null);
      if (selectedEntityId === entityId) {
        setSelectedEntityId(null);
        setIsEntityDetailsOpen(false);
      }
      void queryClient.invalidateQueries({ queryKey: ["graph", id] });
      void queryClient.invalidateQueries({ queryKey: ["investigations"] });
    },
    onError: (error: unknown) => {
      setDeleteEntityError(error instanceof ApiError ? error.message : "Could not delete entity");
    },
  });

  const findDuplicatesMutation = useMutation({
    mutationFn: () => apiClient.findDuplicateCandidates(id!, schemaFilter, duplicateThreshold, 100),
    onSuccess: (candidates) => {
      setDuplicateCandidates(candidates);
      setDuplicateError(null);
      if (candidates.length === 0) {
        setActiveCandidate(null);
        setMergeTargetId(null);
      }
    },
    onError: (error: unknown) => {
      setDuplicateCandidates([]);
      setActiveCandidate(null);
      setMergeTargetId(null);
      setDuplicateError(error instanceof ApiError ? error.message : "Could not load duplicate candidates");
    },
  });

  const mergeMutation = useMutation({
    mutationFn: (candidate: DuplicateCandidate) => {
      const targetId = mergeTargetId ?? candidate.left.id;
      return apiClient.mergeEntities(id!, {
        source_ids: [candidate.left.id, candidate.right.id],
        target_id: targetId,
        merged_properties: mergedProperties(candidate.left, candidate.right),
      });
    },
    onSuccess: async (_result, candidate) => {
      setDuplicateError(null);
      setActiveCandidate(null);
      setMergeTargetId(null);
      setDuplicateCandidates((prev) =>
        prev.filter(
          (item) =>
            item.left.id !== candidate.left.id &&
            item.right.id !== candidate.right.id &&
            item.left.id !== candidate.right.id &&
            item.right.id !== candidate.left.id
        )
      );
      await queryClient.invalidateQueries({ queryKey: ["graph", id] });
      await queryClient.invalidateQueries({ queryKey: ["investigations"] });
    },
    onError: (error: unknown) => {
      setDuplicateError(error instanceof ApiError ? error.message : "Could not merge entities");
    },
  });

  const nodes = useMemo(() => graphQuery.data?.nodes ?? [], [graphQuery.data?.nodes]);
  const edges = useMemo(() => graphQuery.data?.edges ?? [], [graphQuery.data?.edges]);

  const visibleNodes = useMemo(() => {
    return nodes.filter((node) => {
      if (schemaFilter !== "all" && node.schema !== schemaFilter) {
        return false;
      }

      if (!search.trim()) {
        return true;
      }

      const text = `${node.id} ${node.schema} ${nodeLabel(node)}`.toLowerCase();
      return text.includes(search.trim().toLowerCase());
    });
  }, [nodes, schemaFilter, search]);

  const visibleNodeIds = useMemo(() => new Set(visibleNodes.map((node) => node.id)), [visibleNodes]);
  const visibleEdges = useMemo(
    () => edges.filter((edge) => visibleNodeIds.has(edge.source) && visibleNodeIds.has(edge.target)),
    [edges, visibleNodeIds]
  );

  const selectedEntity = useMemo(() => nodes.find((node) => node.id === selectedEntityId), [nodes, selectedEntityId]);
  const existingEntityIds = useMemo(() => new Set(nodes.map((node) => node.id)), [nodes]);
  const investigationEntities = useMemo(
    () => nodes.map((node) => ({ id: node.id, label: nodeLabel(node), schema: node.schema })),
    [nodes]
  );

  useEffect(() => {
    if (viewMode !== "graph") {
      return;
    }

    if (!canvasRef.current) {
      return;
    }

    const elements: ElementDefinition[] = [
      ...visibleNodes.map((node) => ({
        data: {
          id: node.id,
          label: nodeLabel(node),
          schema: node.schema,
          color: SCHEMA_COLORS[node.schema] ?? "#2563eb",
          icon: schemaIconDataUri(node.schema),
        },
      })),
      ...visibleEdges.map((edge) => ({
        data: {
          id: edge.id,
          source: edge.source,
          target: edge.target,
          label: edgeLabel(edge),
          weak: edge.schema.toUpperCase() === "UNKNOWNLINK" || edge.schema.toUpperCase() === "RELATED" ? 1 : 0,
        },
      })),
    ];

    if (!cyRef.current) {
      const cy = cytoscape({
        container: canvasRef.current,
        elements,
        style: [
          {
            selector: "node",
            style: {
              label: "data(label)",
              "background-color": "data(color)",
              color: "#111827",
              "text-valign": "bottom",
              "text-halign": "center",
              "text-margin-y": 8,
              "font-size": 11,
              width: 38,
              height: 38,
              "background-image": "data(icon)",
              "background-fit": "contain",
              "background-width": "65%",
              "background-height": "65%",
              "background-image-opacity": 0.95,
              "text-background-color": "#ffffff",
              "text-background-opacity": 0.75,
              "text-background-padding": "3px",
              "text-background-shape": "roundrectangle",
              "text-wrap": "wrap",
              "text-max-width": "120px",
            },
          },
          {
            selector: "node:selected",
            style: {
              "border-width": 3,
              "border-color": "#0ea5e9",
            },
          },
          {
            selector: "edge",
            style: {
              width: 2,
              "line-color": "#94a3b8",
              "target-arrow-color": "#94a3b8",
              "target-arrow-shape": "triangle",
              "curve-style": "bezier",
              label: "data(label)",
              "font-size": 9,
              color: "#64748b",
              "text-background-color": "#ffffff",
              "text-background-opacity": 0.75,
              "text-background-padding": "2px",
              "text-background-shape": "roundrectangle",
              "text-margin-y": -6,
              "text-rotation": "autorotate",
            },
          },
          {
            selector: "edge[weak = 1]",
            style: {
              "line-style": "dashed",
              opacity: 0.6,
              "target-arrow-shape": "none",
            },
          },
        ],
        });

      cy.on("tap", "node", (event) => {
        setSelectedEntityId(event.target.id());
      });

      cyRef.current = cy;
    } else {
      const cy = cyRef.current;
      cy.elements().remove();
      cy.add(elements);
    }

    const cy = cyRef.current;
    if (!cy) {
      return;
    }
    const layoutOptions: LayoutOptions =
      layout === "fcose"
        ? ({ ...FCOSE_OPTIONS, animate: visibleNodes.length < 220 } as LayoutOptions)
        : ({ name: layout, animate: true, fit: true, padding: 40 } as LayoutOptions);
    cy.layout(layoutOptions).run();
  }, [layout, visibleEdges, visibleNodes, viewMode]);

  useEffect(() => {
    const cy = cyRef.current;
    if (!cy || !selectedEntityId || viewMode !== "graph") {
      return;
    }

    cy.elements().unselect();
    const node = cy.getElementById(selectedEntityId);
    if (node.nonempty()) {
      node.select();
      cy.animate({ center: { eles: node }, duration: 250 });
    }
  }, [selectedEntityId, viewMode]);

  useEffect(() => {
    if (!isEntityDetailsOpen) {
      return;
    }

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setIsEntityDetailsOpen(false);
      }
    };

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [isEntityDetailsOpen]);

  useEffect(() => {
    if (!activeCandidate) {
      return;
    }
    setMergeTargetId(activeCandidate.left.id);
  }, [activeCandidate]);

  const onDropUpload = (file?: File) => {
    if (!file || !id) {
      return;
    }
    uploadMutation.mutate(file);
  };

  const ingestStatusLabel = ingestStatusQuery.data?.status ?? (uploadMutation.isPending ? "UPLOADING" : null);
  const ingestProgress = uploadMutation.isPending
    ? 15
    : progressFromStatus(ingestStatusQuery.data?.status ?? null);
  const isIngestTerminal =
    ingestStatusLabel !== null &&
    ["SUCCESS", "COMPLETED", "ERROR", "FAILED", "CANCELLED"].includes(ingestStatusLabel.toUpperCase());

  const onSearchYente = () => {
    if (!yenteQuery.trim()) {
      setYenteResults([]);
      setYenteError("Enter a query to search Yente");
      return;
    }

    yenteSearchMutation.mutate();
  };

  const onSubmitChat = async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || !id || chatStatus !== "ready") {
      return;
    }
    await sendMessage({ text: trimmed });
    setChatInput("");
  };

  const sendSuggestion = async (text: string) => {
    if (!id || chatStatus !== "ready") {
      return;
    }
    await sendMessage({ text });
  };

  return (
    <div className="flex h-[calc(100vh-3.5rem)] min-h-[560px] flex-col gap-4 lg:flex-row">
      <div className="flex min-w-0 flex-1 flex-col gap-3 rounded-lg border bg-background/70 p-3 lg:order-2">
        <div className="flex flex-wrap items-center gap-2">
          <div className="relative flex-1 min-w-[220px]">
            <Search className="pointer-events-none absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              className="w-full rounded-md border bg-background py-2 pl-9 pr-3 text-sm"
              placeholder="Search entities"
            />
          </div>

          <select
            value={schemaFilter}
            onChange={(event) => setSchemaFilter(event.target.value)}
            className="rounded-md border bg-background px-3 py-2 text-sm"
          >
            <option value="all">All schemata</option>
            {(schemataQuery.data ?? []).map((schema) => (
              <option key={schema.name} value={schema.name}>
                {schema.label}
              </option>
            ))}
          </select>

          <select
            value={layout}
            onChange={(event) => setLayout(event.target.value as "fcose" | "grid" | "circle")}
            className="rounded-md border bg-background px-3 py-2 text-sm"
          >
            <option value="fcose">Force Directed</option>
            <option value="grid">Grid</option>
            <option value="circle">Circle</option>
          </select>

          <div className="flex items-center rounded-md border bg-background p-1">
            <Button
              variant={viewMode === "graph" ? "secondary" : "ghost"}
              size="sm"
              className="h-7 px-3 text-xs"
              onClick={() => setViewMode("graph")}
            >
              <Network className="mr-2 h-3.5 w-3.5" />
              Graph
            </Button>
            <Button
              variant={viewMode === "map" ? "secondary" : "ghost"}
              size="sm"
              className="h-7 px-3 text-xs"
              onClick={() => setViewMode("map")}
            >
              <MapIcon className="mr-2 h-3.5 w-3.5" />
              Map
            </Button>
            <Button
              variant={viewMode === "notebook" ? "secondary" : "ghost"}
              size="sm"
              className="h-7 px-3 text-xs"
              onClick={() => setViewMode("notebook")}
            >
              <Notebook className="mr-2 h-3.5 w-3.5" />
              Notebook
            </Button>
          </div>

          <Button
            variant="outline"
            size="icon"
            onClick={() => cyRef.current?.zoom(cyRef.current.zoom() + 0.1)}
            disabled={viewMode !== "graph"}
          >
            <ZoomIn className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            onClick={() => cyRef.current?.zoom(Math.max(0.2, cyRef.current.zoom() - 0.1))}
            disabled={viewMode !== "graph"}
          >
            <ZoomOut className="h-4 w-4" />
          </Button>
        </div>

        <div
          ref={canvasRef}
          className={`h-full min-h-[360px] rounded-md border bg-gradient-to-b from-slate-100 to-slate-50 dark:from-slate-950 dark:to-slate-900 ${
            viewMode === "graph" ? "" : "hidden"
          }`}
        />

        {viewMode === "map" ? (
          <EntityMap
            nodes={visibleNodes}
            onSelect={setSelectedEntityId}
            selectedEntityId={selectedEntityId}
          />
        ) : null}

        {viewMode === "notebook" && id ? (
          <NotebookCanvas
            investigationId={id}
            entities={investigationEntities}
            onRevealEntity={(entityId) => {
              setSelectedEntityId(entityId);
              setViewMode("graph");
            }}
          />
        ) : null}

        <label
          onDragOver={(event) => {
            event.preventDefault();
            setDragActive(true);
          }}
          onDragLeave={() => setDragActive(false)}
          onDrop={(event) => {
            event.preventDefault();
            setDragActive(false);
            const file = event.dataTransfer.files?.[0];
            onDropUpload(file);
          }}
          className={`flex cursor-pointer items-center justify-center gap-2 rounded-md border border-dashed p-3 text-sm ${
            dragActive ? "border-primary bg-primary/10" : "text-muted-foreground"
          }`}
        >
          <Upload className="h-4 w-4" />
          <span>
            {uploadMutation.isPending
              ? "Uploading and ingesting..."
              : "Drop supported files here or click to upload"}
          </span>
          <input
            type="file"
            accept={SUPPORTED_UPLOAD_ACCEPT}
            className="hidden"
            onChange={(event) => onDropUpload(event.target.files?.[0])}
          />
        </label>
        <p className="text-xs text-muted-foreground">
          Supported types: FTM/JSON ({SUPPORTED_UPLOAD_GROUPS.ftm.join(", ")}) and documents (
          {SUPPORTED_UPLOAD_GROUPS.documents.join(", ")}).
        </p>
        {(uploadMutation.isPending || ingestWorkflowId) && ingestStatusLabel ? (
          <div className="space-y-1">
            <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
              <div
                className={`h-full transition-all duration-500 ${
                  ingestStatusLabel.toUpperCase() === "ERROR" || ingestStatusLabel.toUpperCase() === "FAILED"
                    ? "bg-destructive"
                    : "bg-primary"
                }`}
                style={{ width: `${ingestProgress}%` }}
              />
            </div>
            <p className="text-xs text-muted-foreground">
              Ingestion {ingestStatusLabel.toLowerCase()}
              {ingestWorkflowId ? ` (${ingestWorkflowId.slice(0, 8)})` : ""}
              {!isIngestTerminal ? "..." : ""}
            </p>
            {ingestStatusQuery.data?.error ? (
              <p className="text-xs text-destructive">{ingestStatusQuery.data.error}</p>
            ) : null}
          </div>
        ) : null}
      </div>

      <div className="w-full space-y-3 lg:order-1 lg:w-96">
        <div className="rounded-lg border bg-card p-4">
          <h2 className="font-semibold">Entity Details</h2>
          {selectedEntity ? (
            <>
              <p className="mt-1 text-sm text-muted-foreground">{selectedEntity.id}</p>
              <p className="mt-2 inline-block rounded-full bg-muted px-2 py-0.5 text-xs">
                {selectedEntity.schema}
              </p>

              <div className="mt-3 space-y-2">
                {Object.entries(selectedEntity.properties)
                  .slice(0, 3)
                  .map(([key, values]) => (
                  <div key={key}>
                    <p className="text-xs uppercase tracking-wide text-muted-foreground">{key}</p>
                    <p className="line-clamp-2 text-sm">{values.join(", ") || "-"}</p>
                  </div>
                  ))}
              </div>

              {Object.keys(selectedEntity.properties).length > 0 ? (
                <Button variant="outline" className="mt-3 w-full" onClick={() => setIsEntityDetailsOpen(true)}>
                  Open Full Details
                </Button>
              ) : null}

              <Button
                className="mt-4 w-full"
                onClick={() => selectedEntityId && expandMutation.mutate(selectedEntityId)}
                disabled={expandMutation.isPending}
              >
                {expandMutation.isPending ? "Expanding..." : "Expand Neighbors"}
              </Button>

              <Button
                variant="destructive"
                className="mt-2 w-full"
                onClick={() => selectedEntityId && deleteEntityMutation.mutate(selectedEntityId)}
                disabled={deleteEntityMutation.isPending}
              >
                <Trash2 className="h-4 w-4" />
                {deleteEntityMutation.isPending ? "Deleting..." : "Delete Entity"}
              </Button>

              {deleteEntityError ? <p className="mt-2 text-xs text-destructive">{deleteEntityError}</p> : null}
            </>
          ) : (
            <p className="mt-2 text-sm text-muted-foreground">
              Select an entity on the graph to view details.
            </p>
          )}
        </div>

        <div className="rounded-lg border bg-card p-4">
          <h3 className="mb-3 text-sm font-semibold uppercase tracking-[0.14em] text-muted-foreground">
            Yente Search
          </h3>

          <div className="flex items-center gap-2">
            <div className="relative min-w-0 flex-1">
              <Search className="pointer-events-none absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <input
                value={yenteQuery}
                onChange={(event) => setYenteQuery(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    event.preventDefault();
                    onSearchYente();
                  }
                }}
                className="w-full rounded-md border bg-background py-2 pl-9 pr-3 text-sm"
                placeholder="Query OpenSanctions via Yente"
              />
            </div>
            <Button
              variant="secondary"
              onClick={onSearchYente}
              disabled={yenteSearchMutation.isPending || !id}
            >
              {yenteSearchMutation.isPending ? "Searching..." : "Search"}
            </Button>
          </div>

          {yenteError ? <p className="mt-2 text-xs text-destructive">{yenteError}</p> : null}
          {addEntityError ? <p className="mt-2 text-xs text-destructive">{addEntityError}</p> : null}

          <div className="mt-3 max-h-[260px] space-y-2 overflow-auto">
            {yenteResults.map((result) => {
              const alreadyAdded = existingEntityIds.has(result.id);
              const scoreLabel = result.score === null ? null : `${result.score.toFixed(2)} score`;

              return (
                <div key={result.id} className="rounded-md border p-2.5">
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium">{result.caption}</p>
                      <p className="truncate text-xs text-muted-foreground">
                        {result.schema} • {result.id}
                      </p>
                      {(scoreLabel || result.datasets.length > 0) && (
                        <p className="mt-1 truncate text-[11px] text-muted-foreground">
                          {[scoreLabel, result.datasets.join(", ")].filter(Boolean).join(" • ")}
                        </p>
                      )}
                    </div>
                    <Button
                      size="sm"
                      onClick={() => {
                        setAddingEntityId(result.id);
                        setAddEntityError(null);
                        addYenteEntityMutation.mutate(result);
                      }}
                      disabled={alreadyAdded || addYenteEntityMutation.isPending || !id}
                    >
                      {alreadyAdded
                        ? "Added"
                        : addingEntityId === result.id && addYenteEntityMutation.isPending
                          ? "Adding..."
                          : "Add"}
                    </Button>
                  </div>
                </div>
              );
            })}

            {!yenteSearchMutation.isPending && yenteResults.length === 0 ? (
              <p className="rounded-md border border-dashed p-3 text-xs text-muted-foreground">
                Search Yente to find entities you can add to this investigation.
              </p>
            ) : null}
          </div>
        </div>

        <div className="rounded-lg border bg-card p-4">
          <h3 className="mb-2 text-sm font-semibold uppercase tracking-[0.14em] text-muted-foreground">
            Manual Deduplication
          </h3>

          <div className="space-y-3">
            <div className="space-y-1">
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span>Similarity threshold</span>
                <span>{duplicateThreshold.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min={0.5}
                max={0.95}
                step={0.05}
                value={duplicateThreshold}
                onChange={(event) => setDuplicateThreshold(Number(event.target.value))}
                className="w-full"
              />
            </div>

            <Button
              className="w-full"
              variant="secondary"
              onClick={() => findDuplicatesMutation.mutate()}
              disabled={findDuplicatesMutation.isPending || !id}
            >
              {findDuplicatesMutation.isPending ? "Scanning..." : "Find Duplicates"}
            </Button>

            {duplicateError ? <p className="text-xs text-destructive">{duplicateError}</p> : null}

            <div className="max-h-[220px] space-y-2 overflow-auto">
              {duplicateCandidates.map((candidate) => (
                <button
                  key={`${candidate.left.id}-${candidate.right.id}`}
                  type="button"
                  className="w-full rounded-md border p-2 text-left text-xs hover:bg-muted"
                  onClick={() => setActiveCandidate(candidate)}
                >
                  <p className="font-medium">
                    {entityLabel(candidate.left)} <span className="text-muted-foreground">vs</span>{" "}
                    {entityLabel(candidate.right)}
                  </p>
                  <p className="mt-1 text-muted-foreground">
                    {candidate.similarity.toFixed(2)} match • {candidate.reason}
                  </p>
                </button>
              ))}

              {!findDuplicatesMutation.isPending && duplicateCandidates.length === 0 ? (
                <p className="rounded-md border border-dashed p-3 text-xs text-muted-foreground">
                  No candidates loaded yet. Run duplicate scanning to review possible merges.
                </p>
              ) : null}
            </div>
          </div>
        </div>

        <div className="rounded-lg border bg-card p-4">
          <h3 className="mb-2 text-sm font-semibold uppercase tracking-[0.14em] text-muted-foreground">
            Visible Entities ({visibleNodes.length})
          </h3>
          <div className="max-h-[320px] space-y-1 overflow-auto">
            {visibleNodes.map((node) => (
              <button
                type="button"
                key={node.id}
                onClick={() => setSelectedEntityId(node.id)}
                className={`w-full rounded-md border px-3 py-2 text-left text-sm ${
                  selectedEntityId === node.id
                    ? "border-primary bg-primary/10"
                    : "border-transparent hover:border-border hover:bg-muted"
                }`}
              >
                <p className="truncate font-medium">{nodeLabel(node)}</p>
                <p className="truncate text-xs text-muted-foreground">
                  {node.schema} • {node.id}
                </p>
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="w-full lg:order-3 lg:w-96">
        <InvestigationChatbot
          error={chatError}
          input={chatInput}
          investigationId={id}
          messages={chatMessages}
          onInputChange={setChatInput}
          onSendMessage={onSubmitChat}
          onSendSuggestion={sendSuggestion}
          onStop={stopChat}
          status={chatStatus}
          suggestions={CHAT_SUGGESTIONS}
        />
      </div>

      {activeCandidate ? (
        <div className="fixed inset-0 z-[70] flex items-center justify-center bg-black/45 p-4" role="dialog" aria-modal="true">
          <button
            type="button"
            className="absolute inset-0"
            onClick={() => {
              setActiveCandidate(null);
              setMergeTargetId(null);
            }}
            aria-label="Close dedupe dialog"
          />
          <div className="relative w-full max-w-4xl rounded-lg border bg-card shadow-2xl">
            <div className="flex items-start justify-between border-b p-4">
              <div className="min-w-0">
                <h3 className="text-base font-semibold">Review Potential Duplicate</h3>
                <p className="mt-1 text-xs text-muted-foreground">
                  Similarity {activeCandidate.similarity.toFixed(2)} • {activeCandidate.reason}
                </p>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => {
                  setActiveCandidate(null);
                  setMergeTargetId(null);
                }}
                aria-label="Close dedupe dialog"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>

            <div className="grid gap-3 p-4 md:grid-cols-2">
              {[activeCandidate.left, activeCandidate.right].map((entity) => (
                <div
                  key={entity.id}
                  className={`rounded-md border p-3 ${
                    mergeTargetId === entity.id ? "border-primary bg-primary/5" : ""
                  }`}
                >
                  <label className="flex cursor-pointer items-center justify-between gap-2">
                    <div>
                      <p className="text-sm font-semibold">{entityLabel(entity)}</p>
                      <p className="text-xs text-muted-foreground">
                        {entity.schema} • {entity.id}
                      </p>
                    </div>
                    <input
                      type="radio"
                      name="merge-target"
                      checked={mergeTargetId === entity.id}
                      onChange={() => setMergeTargetId(entity.id)}
                    />
                  </label>

                  <div className="mt-3 max-h-[280px] space-y-2 overflow-auto">
                    {Object.entries(entity.properties).map(([key, values]) => (
                      <div key={key}>
                        <p className="text-[11px] uppercase tracking-wide text-muted-foreground">{key}</p>
                        <p className="text-xs break-words">{values.join(", ") || "-"}</p>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            <div className="flex items-center justify-between border-t p-4">
              <p className="text-xs text-muted-foreground">
                Merge combines all values from both entities and redirects edges to the selected target.
              </p>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  onClick={() => {
                    setActiveCandidate(null);
                    setMergeTargetId(null);
                  }}
                >
                  Cancel
                </Button>
                <Button
                  onClick={() => mergeMutation.mutate(activeCandidate)}
                  disabled={mergeMutation.isPending || mergeTargetId === null}
                >
                  {mergeMutation.isPending ? "Merging..." : "Merge Entities"}
                </Button>
              </div>
            </div>
          </div>
        </div>
      ) : null}

      {isEntityDetailsOpen && selectedEntity ? (
        <div className="fixed inset-0 z-[70] flex items-center justify-center bg-black/45 p-4" role="dialog" aria-modal="true">
          <button
            type="button"
            className="absolute inset-0"
            onClick={() => setIsEntityDetailsOpen(false)}
            aria-label="Close details"
          />
          <div className="relative w-full max-w-3xl rounded-lg border bg-card shadow-2xl">
            <div className="flex items-start justify-between border-b p-4">
              <div className="min-w-0">
                <h3 className="truncate text-base font-semibold">{nodeLabel(selectedEntity)}</h3>
                <p className="truncate text-xs text-muted-foreground">{selectedEntity.id}</p>
                <p className="mt-1 inline-block rounded-full bg-muted px-2 py-0.5 text-xs">
                  {selectedEntity.schema}
                </p>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsEntityDetailsOpen(false)}
                aria-label="Close details"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>

            <div className="max-h-[70vh] space-y-3 overflow-auto p-4">
              {Object.entries(selectedEntity.properties).map(([key, values]) => (
                <div key={key}>
                  <p className="text-xs uppercase tracking-wide text-muted-foreground">{key}</p>
                  <p className="break-words text-sm">{values.join(", ") || "-"}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
