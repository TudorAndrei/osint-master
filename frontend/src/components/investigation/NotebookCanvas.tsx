import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  addEdge,
  Background,
  type Connection,
  Controls,
  MiniMap,
  type Edge,
  type Node,
  ReactFlow,
  ReactFlowProvider,
  useEdgesState,
  useNodesState,
  useReactFlow,
} from "@xyflow/react";
import type { JSONContent } from "@tiptap/react";
import { Plus } from "lucide-react";

import { apiClient, ApiError } from "@/api/client";
import type { NotebookCanvas as NotebookCanvasPayload } from "@/api/types";
import { Button } from "@/components/ui/button";
import EntityNode from "@/components/investigation/nodes/EntityNode";
import NoteNode, { type MentionEntity } from "@/components/investigation/nodes/NoteNode";

import "@xyflow/react/dist/style.css";

interface InvestigationEntitySummary {
  id: string;
  label: string;
  schema: string;
}

interface NotebookCanvasProps {
  investigationId: string;
  entities: InvestigationEntitySummary[];
  onRevealEntity: (entityId: string) => void;
}

type PersistedNoteData = {
  title: string;
  content: JSONContent;
};

type PersistedEntityData = {
  entityId: string;
  label: string;
  schema: string;
};

type PersistedNode = Node<Record<string, unknown>>;

const EMPTY_DOC: JSONContent = {
  type: "doc",
  content: [{ type: "paragraph" }],
};

function defaultCanvas(): NotebookCanvasPayload {
  return {
    nodes: [],
    edges: [],
    viewport: {
      x: 0,
      y: 0,
      zoom: 1,
    },
  };
}

function asPosition(value: unknown): { x: number; y: number } {
  const input = value as Record<string, unknown>;
  return {
    x: typeof input?.x === "number" ? input.x : 0,
    y: typeof input?.y === "number" ? input.y : 0,
  };
}

function hydrateNode(rawNode: unknown): PersistedNode | null {
  if (!rawNode || typeof rawNode !== "object") {
    return null;
  }

  const node = rawNode as Record<string, unknown>;
  if (typeof node.id !== "string") {
    return null;
  }

  const type = node.type === "entity" ? "entity" : "note";
  const base: Node = {
    id: node.id,
    type,
    position: asPosition(node.position),
    data: {
      title: "Note",
      content: EMPTY_DOC,
    },
  };

  const data = (node.data ?? {}) as Record<string, unknown>;
  if (type === "entity") {
    return {
      ...base,
      data: {
        entityId: typeof data.entityId === "string" ? data.entityId : "",
        label: typeof data.label === "string" ? data.label : "Entity",
        schema: typeof data.schema === "string" ? data.schema : "Entity",
      },
    };
  }

  return {
    ...base,
    data: {
      title: typeof data.title === "string" ? data.title : "Note",
      content: (data.content as JSONContent | undefined) ?? EMPTY_DOC,
    },
  };
}

function hydrateEdge(rawEdge: unknown): Edge | null {
  if (!rawEdge || typeof rawEdge !== "object") {
    return null;
  }
  const edge = rawEdge as Record<string, unknown>;
  if (typeof edge.id !== "string" || typeof edge.source !== "string" || typeof edge.target !== "string") {
    return null;
  }
  return {
    id: edge.id,
    source: edge.source,
    target: edge.target,
    type: typeof edge.type === "string" ? edge.type : "smoothstep",
  };
}

function NotebookCanvasInner({ investigationId, entities, onRevealEntity }: NotebookCanvasProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState<PersistedNode>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [version, setVersion] = useState(1);
  const [viewport, setViewport] = useState({ x: 0, y: 0, zoom: 1 });
  const [isHydrated, setIsHydrated] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const flow = useReactFlow();
  const lastSavedHashRef = useRef("");

  const notebookQuery = useQuery({
    queryKey: ["notebook", investigationId],
    queryFn: () => apiClient.getNotebook(investigationId),
    enabled: Boolean(investigationId),
  });

  const saveMutation = useMutation({
    mutationFn: (payload: NotebookCanvasPayload) =>
      apiClient.saveNotebook(investigationId, {
        version,
        canvas_doc: payload,
      }),
    onSuccess: (saved) => {
      setVersion(saved.version);
      setSaveError(null);
      lastSavedHashRef.current = JSON.stringify(saved.canvas_doc);
    },
    onError: (error: unknown) => {
      if (error instanceof ApiError && error.status === 409) {
        setSaveError("Notebook changed elsewhere. Reload the page to sync latest version.");
        return;
      }
      setSaveError(error instanceof ApiError ? error.message : "Could not save notebook");
    },
  });

  useEffect(() => {
    if (!notebookQuery.data) {
      return;
    }
    const payload = notebookQuery.data.canvas_doc ?? defaultCanvas();
    const parsedNodes = payload.nodes.map(hydrateNode).filter((item): item is PersistedNode => item !== null);
    const parsedEdges = payload.edges.map(hydrateEdge).filter((item): item is Edge => item !== null);

    setNodes(parsedNodes);
    setEdges(parsedEdges);
    setVersion(notebookQuery.data.version);
    setViewport(payload.viewport ?? { x: 0, y: 0, zoom: 1 });
    flow.setViewport(payload.viewport ?? { x: 0, y: 0, zoom: 1 }, { duration: 0 });
    lastSavedHashRef.current = JSON.stringify(payload);
    setIsHydrated(true);
  }, [flow, notebookQuery.data, setEdges, setNodes]);

  const entityMap = useMemo(() => {
    return new Map(entities.map((entity) => [entity.id, entity]));
  }, [entities]);

  const mentionEntities = useMemo<MentionEntity[]>(() => {
    return entities.map((entity) => ({ id: entity.id, label: entity.label }));
  }, [entities]);

  const onConnect = useCallback(
    (connection: Connection) => {
      setEdges((current) => addEdge({ ...connection, type: "smoothstep" }, current));
    },
    [setEdges]
  );

  const addNote = useCallback(() => {
    const point = flow.screenToFlowPosition({ x: window.innerWidth * 0.42, y: window.innerHeight * 0.35 });
    const nextNode: PersistedNode = {
      id: crypto.randomUUID(),
      type: "note",
      position: point,
      data: {
        title: "Note",
        content: EMPTY_DOC,
      },
    };
    setNodes((current) => [...current, nextNode]);
  }, [flow, setNodes]);

  const onNoteContentChange = useCallback(
    (nodeId: string, content: JSONContent) => {
      setNodes((current) =>
        current.map((node) => {
          if (node.id !== nodeId || node.type !== "note") {
            return node;
          }
          return {
            ...node,
            data: {
              ...(node.data as PersistedNoteData),
              content,
            },
          };
        })
      );
    },
    [setNodes]
  );

  const onMentionClick = useCallback(
    (entityId: string, sourceNodeId: string) => {
      const sourceNode = nodes.find((node) => node.id === sourceNodeId);
      const entity = entityMap.get(entityId);
      if (!sourceNode || !entity) {
        return;
      }

      const entityNodeId = `entity-${entityId}-${crypto.randomUUID().slice(0, 8)}`;
      const entityNode: PersistedNode = {
        id: entityNodeId,
        type: "entity",
        position: {
          x: sourceNode.position.x + 360,
          y: sourceNode.position.y + 40,
        },
        data: {
          entityId: entity.id,
          label: entity.label,
          schema: entity.schema,
        },
      };

      setNodes((current) => [...current, entityNode]);
      setEdges((current) =>
        addEdge(
          {
            id: `edge-${sourceNodeId}-${entityNodeId}`,
            source: sourceNodeId,
            target: entityNodeId,
            type: "smoothstep",
          },
          current
        )
      );
    },
    [entityMap, nodes, setEdges, setNodes]
  );

  const renderedNodes = useMemo(() => {
    return nodes.map((node) => {
      if (node.type === "entity") {
        const data = node.data as PersistedEntityData;
        return {
          ...node,
          data: {
            ...data,
            onReveal: onRevealEntity,
          },
        };
      }
      const data = node.data as PersistedNoteData;
      return {
        ...node,
        data: {
          ...data,
          entities: mentionEntities,
          onContentChange: onNoteContentChange,
          onMentionClick,
        },
      };
    });
  }, [mentionEntities, nodes, onMentionClick, onNoteContentChange, onRevealEntity]);

  const serializedCanvas = useMemo<NotebookCanvasPayload>(() => {
    const serializedNodes = nodes.map((node) => {
      if (node.type === "entity") {
        const data = node.data as PersistedEntityData;
        return {
          id: node.id,
          type: "entity",
          position: node.position,
          data: {
            entityId: data.entityId,
            label: data.label,
            schema: data.schema,
          },
        };
      }
      const data = node.data as PersistedNoteData;
      return {
        id: node.id,
        type: "note",
        position: node.position,
        data: {
          title: data.title,
          content: data.content,
        },
      };
    });

    const serializedEdges = edges.map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      type: edge.type,
    }));

    return {
      nodes: serializedNodes,
      edges: serializedEdges,
      viewport,
    };
  }, [edges, nodes, viewport]);

  useEffect(() => {
    if (!isHydrated) {
      return;
    }

    const payloadHash = JSON.stringify(serializedCanvas);
    if (payloadHash === lastSavedHashRef.current) {
      return;
    }

    const timeout = window.setTimeout(() => {
      if (!saveMutation.isPending) {
        saveMutation.mutate(serializedCanvas);
      }
    }, 1300);

    return () => window.clearTimeout(timeout);
  }, [isHydrated, saveMutation, serializedCanvas]);

  return (
    <div className="relative h-full min-h-[360px] overflow-hidden rounded-md border bg-slate-50">
      <div className="absolute left-3 top-3 z-20 flex items-center gap-2">
        <Button size="sm" variant="secondary" onClick={addNote}>
          <Plus className="mr-1.5 h-4 w-4" />
          Add note
        </Button>
        {saveMutation.isPending ? <span className="text-xs text-muted-foreground">Saving...</span> : null}
        {saveError ? <span className="text-xs text-destructive">{saveError}</span> : null}
      </div>
      <ReactFlow
        nodes={renderedNodes}
        edges={edges}
        nodeTypes={{
          note: NoteNode,
          entity: EntityNode,
        } as any}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onMoveEnd={(_event, currentViewport) => setViewport(currentViewport)}
        fitView
      >
        <Background gap={18} size={1} />
        <MiniMap pannable zoomable />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  );
}

export default function NotebookCanvas(props: NotebookCanvasProps) {
  return (
    <ReactFlowProvider>
      <NotebookCanvasInner {...props} />
    </ReactFlowProvider>
  );
}
