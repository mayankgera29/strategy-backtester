// src/components/NodeProperties.tsx
import React, { useState } from "react";
import { Node } from "reactflow";

type Props = {
  node: Node<any>;
  onUpdate: (data: any) => void;
};

export default function NodeProperties({ node, onUpdate }: Props) {
  const data = node.data ?? {};
  const [label, setLabel] = useState<string>(data.label ?? "");
  const [nodeType, setNodeType] = useState<string>(data.nodeType ?? "");
  const [windowParam, setWindowParam] = useState<string>(data.params?.window ?? "");

  const save = () => {
    onUpdate({
      label,
      nodeType,
      params: { ...data.params, window: windowParam },
    });
    alert("Saved node properties");
  };

  return (
    <div>
      <div style={{ marginBottom: 8 }}>
        <label>Label</label>
        <input style={{ width: "100%" }} value={label} onChange={(e) => setLabel(e.target.value)} />
      </div>

      <div style={{ marginBottom: 8 }}>
        <label>Type</label>
        <select style={{ width: "100%" }} value={nodeType} onChange={(e) => setNodeType(e.target.value)}>
          <option value="start">Start</option>
          <option value="buy">Buy</option>
          <option value="sell">Sell</option>
          <option value="indicator">Indicator</option>
        </select>
      </div>

      <div style={{ marginBottom: 8 }}>
        <label>Params (window)</label>
        <input style={{ width: "100%" }} value={windowParam} onChange={(e) => setWindowParam(e.target.value)} />
      </div>

      <div>
        <button onClick={save}>Save properties</button>
      </div>
    </div>
  );
}
