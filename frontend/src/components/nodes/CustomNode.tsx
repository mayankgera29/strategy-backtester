// src/components/nodes/CustomNode.tsx
import React from "react";
import { Handle, Position, NodeProps } from "reactflow";
import "reactflow/dist/style.css";

type DataShape = {
  label?: string;
  subtitle?: string;
  nodeType?: string;
  params?: Record<string, any>;
};

export default function CustomNode({ id, data }: NodeProps<DataShape>) {
  const label = data?.label ?? "Node";
  const subtitle = data?.subtitle;

  return (
    <div
      style={{
        padding: 8,
        minWidth: 120,
        border: "1px solid #1f2937",
        borderRadius: 4,
        background: "white",
        boxShadow: "0 1px 0 rgba(0,0,0,0.03)",
        fontFamily: "system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial",
      }}
      data-node-id={id}
    >
      <Handle type="target" position={Position.Top} style={{ background: "#111827", width: 8, height: 8, borderRadius: 999 }} />
      <div style={{ textAlign: "left", padding: "2px 4px" }}>
        <div style={{ fontSize: 14, fontWeight: 600, color: "#111827", lineHeight: "1.1" }}>{label}</div>
        {subtitle ? <div style={{ fontSize: 12, color: "#6b7280", marginTop: 4 }}>{subtitle}</div> : null}
      </div>
      <Handle type="source" position={Position.Bottom} style={{ background: "#111827", width: 8, height: 8, borderRadius: 999 }} />
    </div>
  );
}
