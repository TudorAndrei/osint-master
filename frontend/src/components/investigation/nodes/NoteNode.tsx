import { useEffect, useMemo } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";
import Mention from "@tiptap/extension-mention";
import StarterKit from "@tiptap/starter-kit";
import { EditorContent, type JSONContent, useEditor } from "@tiptap/react";

export interface MentionEntity {
  id: string;
  label: string;
}

export interface NoteNodeData {
  title: string;
  content: JSONContent;
  entities: MentionEntity[];
  onContentChange: (nodeId: string, content: JSONContent) => void;
  onMentionClick: (entityId: string, sourceNodeId: string) => void;
}

function suggestionRenderer(): any {
  let popupEl: HTMLDivElement | null = null;
  let selectedIndex = 0;

  const renderItems = (props: {
    items: Array<{ id: string; label: string }>;
    command: (payload: { id: string; label: string }) => void;
    clientRect?: (() => DOMRect) | null;
  }) => {
    if (!popupEl) {
      return;
    }

    popupEl.innerHTML = "";
    props.items.forEach((item, index) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = `block w-full px-2 py-1 text-left text-xs ${
        index === selectedIndex ? "bg-slate-200" : ""
      }`;
      button.textContent = `@${item.label}`;
      button.onclick = () => props.command({ id: item.id, label: item.label });
      popupEl?.appendChild(button);
    });

    const rect = props.clientRect?.();
    if (rect && popupEl) {
      popupEl.style.left = `${rect.left}px`;
      popupEl.style.top = `${rect.bottom + 6}px`;
    }
  };

  return {
    onStart: (props: {
      items: Array<{ id: string; label: string }>;
      command: (payload: { id: string; label: string }) => void;
      clientRect?: (() => DOMRect) | null;
    }) => {
      popupEl = document.createElement("div");
      popupEl.className =
        "fixed z-[100] max-h-52 w-64 overflow-auto rounded-md border bg-white p-1 shadow-lg";
      document.body.appendChild(popupEl);
      selectedIndex = 0;
      renderItems(props);
    },
    onUpdate: (props: {
      items: Array<{ id: string; label: string }>;
      command: (payload: { id: string; label: string }) => void;
      clientRect?: (() => DOMRect) | null;
    }) => {
      if (!props.items.length) {
        selectedIndex = 0;
      } else {
        selectedIndex = Math.min(selectedIndex, props.items.length - 1);
      }
      renderItems(props);
    },
    onKeyDown: (props: {
      event: KeyboardEvent;
      items: Array<{ id: string; label: string }>;
      command: (payload: { id: string; label: string }) => void;
      clientRect?: (() => DOMRect) | null;
    }) => {
      if (!props.items.length) {
        return false;
      }
      if (props.event.key === "ArrowDown") {
        selectedIndex = (selectedIndex + 1) % props.items.length;
        renderItems(props);
        return true;
      }
      if (props.event.key === "ArrowUp") {
        selectedIndex = (selectedIndex + props.items.length - 1) % props.items.length;
        renderItems(props);
        return true;
      }
      if (props.event.key === "Enter") {
        const item = props.items[selectedIndex];
        if (item) {
          props.command(item);
          return true;
        }
      }
      return false;
    },
    onExit: () => {
      if (popupEl) {
        popupEl.remove();
      }
      popupEl = null;
    },
  };
}

export default function NoteNode({ id, data }: NodeProps) {
  const nodeData = data as unknown as NoteNodeData;
  const entities = useMemo(() => nodeData.entities, [nodeData.entities]);

  const editor = useEditor({
    extensions: [
      StarterKit,
      Mention.configure({
        HTMLAttributes: {
          class: "rounded bg-sky-100 px-1 text-sky-800",
        },
        renderText({ node }) {
          return `@${node.attrs.label ?? node.attrs.id}`;
        },
        renderHTML({ node, options }) {
          return [
            "span",
            {
              ...options.HTMLAttributes,
              "data-mention-id": node.attrs.id,
            },
            `@${node.attrs.label ?? node.attrs.id}`,
          ];
        },
        suggestion: {
          char: "@",
          items: ({ query }) => {
            const term = query.toLowerCase();
            return entities
              .filter((entity) => entity.label.toLowerCase().includes(term) || entity.id.toLowerCase().includes(term))
              .slice(0, 8)
              .map((entity) => ({ id: entity.id, label: entity.label }));
          },
          render: suggestionRenderer,
        },
      }),
    ],
    content: nodeData.content,
    onUpdate({ editor: currentEditor }) {
      nodeData.onContentChange(id, currentEditor.getJSON());
    },
    editorProps: {
      attributes: {
        class: "min-h-20 rounded border border-slate-200 bg-white px-2 py-1 text-sm focus:outline-none",
      },
      handleClick(_view, _pos, event) {
        const target = event.target as HTMLElement;
        const mention = target.closest("[data-mention-id]") as HTMLElement | null;
        if (!mention) {
          return false;
        }
        const entityId = mention.dataset.mentionId;
        if (!entityId) {
          return false;
        }
        nodeData.onMentionClick(entityId, id);
        return true;
      },
    },
  });

  useEffect(() => {
    if (!editor) {
      return;
    }
    if (editor.isFocused) {
      return;
    }
    const next = JSON.stringify(nodeData.content);
    const current = JSON.stringify(editor.getJSON());
    if (next !== current) {
      editor.commands.setContent(nodeData.content as JSONContent, false);
    }
  }, [editor, nodeData.content]);

  return (
    <div className="w-80 rounded-md border border-slate-300 bg-amber-50 p-3 shadow-sm">
      <Handle type="target" position={Position.Top} className="!h-2 !w-2 !bg-amber-500" />
      <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-amber-700">{nodeData.title}</p>
      <EditorContent editor={editor} />
      <Handle type="source" position={Position.Bottom} className="!h-2 !w-2 !bg-amber-500" />
    </div>
  );
}
