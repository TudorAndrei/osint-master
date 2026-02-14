import { Handle, Position, type NodeProps } from "@xyflow/react";
import { ExternalLink } from "lucide-react";

export interface EntityCardData {
  entityId: string;
  label: string;
  schema: string;
  onReveal: (entityId: string) => void;
}

export default function EntityNode({ data }: NodeProps) {
  const nodeData = data as unknown as EntityCardData;
  return (
    <div className="w-64 rounded-md border border-sky-300 bg-sky-50 p-3 shadow-sm">
      <Handle type="target" position={Position.Left} className="!h-2 !w-2 !bg-sky-500" />
      <p className="truncate text-xs font-semibold uppercase tracking-wide text-sky-700">{nodeData.schema}</p>
      <p className="mt-1 truncate text-sm font-medium text-slate-900">{nodeData.label}</p>
      <p className="truncate text-[11px] text-slate-600">{nodeData.entityId}</p>
      <button
        type="button"
        className="mt-3 inline-flex items-center gap-1 text-xs font-medium text-sky-700 hover:text-sky-900"
        onClick={() => nodeData.onReveal(nodeData.entityId)}
      >
        <ExternalLink className="h-3.5 w-3.5" />
        Reveal on graph
      </button>
      <Handle type="source" position={Position.Right} className="!h-2 !w-2 !bg-sky-500" />
    </div>
  );
}
