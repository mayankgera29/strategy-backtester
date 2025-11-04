// src/components/FlowEditor.tsx
import React, { useCallback, useEffect, useMemo, useState } from "react";
import ReactFlow, {
  addEdge,
  applyEdgeChanges,
  applyNodeChanges,
  Background,
  Controls,
  MiniMap,
  Connection,
  Edge,
  Node,
  NodeChange,
  EdgeChange,
  MarkerType,
  ReactFlowProvider,
} from "reactflow";
import "reactflow/dist/style.css";

import CustomNode from "./nodes/CustomNode";
import NodeProperties from "./NodeProperties";
import { saveStrategy, listStrategies } from "../api";

type RFNode = Node<any>;
type RFEdge = Edge;

const nodeTypes = { customNode: CustomNode };

export default function FlowEditorWrapper() {
  return (
    <ReactFlowProvider>
      <FlowEditor />
    </ReactFlowProvider>
  );
}

function FlowEditor() {
  // nodes + edges
  const [nodes, setNodes] = useState<RFNode[]>([]);
  const [edges, setEdges] = useState<RFEdge[]>([]);

  // selection / properties
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [savedList, setSavedList] = useState<any[]>([]);
  const [name, setName] = useState("New Strategy");

  // seed single Start node on first mount if empty
  useEffect(() => {
    if (nodes.length === 0) {
      setNodes([
        {
          id: "n-start",
          type: "customNode",
          position: { x: 300, y: 180 },
          data: { label: "Start", nodeType: "start", params: {} },
        },
      ]);
    }
    // run once only
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Node / Edge change handlers
  const onNodesChange = useCallback((changes: NodeChange[]) => {
    setNodes((nds) => applyNodeChanges(changes, nds));
  }, []);
  const onEdgesChange = useCallback((changes: EdgeChange[]) => {
    setEdges((eds) => applyEdgeChanges(changes, eds));
  }, []);
  const onConnect = useCallback((connection: Connection) => {
    setEdges((eds) =>
      addEdge(
        {
          ...connection,
          markerEnd: { type: MarkerType.ArrowClosed, color: "#111827" },
        },
        eds
      )
    );
  }, []);

  // click handler to capture selected node
  const onNodeClick = useCallback((_e: any, node: Node) => {
    setSelectedNodeId(node.id);
  }, []);

  // add new node helper
  const addNewNode = (type: string) => {
    const id = `${type}-${Date.now()}`;
    const newNode: RFNode = {
      id,
      type: "customNode",
      position: { x: Math.random() * 600 + 50, y: Math.random() * 300 + 50 },
      data: { label: `${type}`.toUpperCase(), nodeType: type, params: {} },
    };
    setNodes((nds) => [...nds, newNode]);
  };

  // delete selected node
  const deleteSelectedNode = () => {
    if (!selectedNodeId) return;
    setNodes((nds) => nds.filter((n) => n.id !== selectedNodeId));
    setEdges((eds) => eds.filter((e) => e.source !== selectedNodeId && e.target !== selectedNodeId));
    setSelectedNodeId(null);
  };

  // Save + Load interactions
  const handleSave = async () => {
    try {
      const graph = { nodes, edges };
      const res = await saveStrategy(name, graph, { created_by: "local" });
      alert("✅ Saved: id=" + res.id + " name=" + res.name);
    } catch (err: any) {
      console.error("Save failed - axios error object:", err);
      // show network / response details:
      if (err.response) {
        // server responded with non-2xx
        console.error("status:", err.response.status, "data:", err.response.data);
        alert("Save failed: " + (err.response.data?.detail ?? JSON.stringify(err.response.data)));
      } else if (err.request) {
        // request made but no response
        console.error("no response, request:", err.request);
        alert("Save failed: No response from server (check backend).");
      } else {
        // something else happened
        console.error("axios setup error:", err.message);
        alert("Save failed: " + err.message);
      }
    }
  };
  

  const refreshList = async () => {
    try {
      const list = await listStrategies();
      setSavedList(list || []);
    } catch (err: any) {
      console.error(err);
      alert("List failed: " + (err?.message ?? JSON.stringify(err)));
    }
  };

  // load strategy (replace nodes+edges)
  const loadStrategy = async (id: number) => {
    try {
      const r = await fetch(`http://127.0.0.1:8000/api/v1/strategies/${id}`);
      if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
      const json = await r.json();
      const graph = json.graph ?? json.result?.graph ?? json;
      // defensive fallback
      const loadedNodes = graph.nodes ?? graph;
      const loadedEdges = graph.edges ?? [];
      // ensure unique ids if needed (we assume saved ids are unique)
      setNodes(loadedNodes);
      setEdges(loadedEdges);
      alert("Loaded placeholder strategy id=" + id);
    } catch (err) {
      console.error(err);
      alert("Load failed: " + (err as any).message);
    }
  };

  const selectedNode = useMemo(() => nodes.find((n) => n.id === selectedNodeId) ?? null, [nodes, selectedNodeId]);

  return (
    <div className="flex h-screen">
      {/* left palette */}
      <div style={{ width: 140, padding: 8, borderRight: "1px solid #e5e7eb", background: "#fff" }}>
        <div style={{ marginBottom: 8, fontWeight: 700 }}>Palette</div>
        <button onClick={() => addNewNode("buy")} style={{ display: "block", width: "100%", marginBottom: 6 }}>
          + Add Buy
        </button>
        <button onClick={() => addNewNode("sell")} style={{ display: "block", width: "100%", marginBottom: 6 }}>
          + Add Sell
        </button>
        <button onClick={() => addNewNode("indicator")} style={{ display: "block", width: "100%", marginBottom: 6 }}>
          + Add Indicator
        </button>
        <button
          style={{ display: "block", width: "100%", marginBottom: 10 }}
          onClick={() =>
            setNodes([
              {
                id: "n-start",
                type: "customNode",
                position: { x: 300, y: 180 },
                data: { label: "Start", nodeType: "start", params: {} },
              },
            ])
          }
        >
          Load Example
        </button>

        <div style={{ marginTop: 12, fontWeight: 700 }}>Saved</div>
        <button onClick={refreshList} style={{ display: "block", width: "100%", marginBottom: 6 }}>
          Refresh list
        </button>
        <div style={{ maxHeight: 220, overflow: "auto", marginTop: 6 }}>
          {savedList.map((s) => (
            <div key={s.id} style={{ marginBottom: 6 }}>
              <button onClick={() => loadStrategy(s.id)} style={{ width: "100%", textAlign: "left" }}>
                {s.name} <small style={{ color: "#6b7280" }}>id: {s.id}</small>
              </button>
            </div>
          ))}
        </div>

        <div style={{ position: "absolute", bottom: 16, left: 8 }}>
          <div style={{ marginBottom: 6 }}>
            <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Strategy name" />
          </div>
          <button onClick={handleSave} style={{ display: "block", width: "100%" }}>
            Save Strategy
          </button>
        </div>
      </div>

      {/* main canvas */}
      <div style={{ flex: 1, position: "relative" }}>
        <div style={{ position: "absolute", right: 14, top: 10, zIndex: 10 }}>
          <div style={{ padding: 6, background: "#fff", border: "1px solid #e5e7eb", borderRadius: 6 }}>
            Nodes: {nodes.length} • Edges: {edges.length}
          </div>
        </div>

        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={onNodeClick}
          nodeTypes={nodeTypes}
          fitView
          style={{ width: "100%", height: "100vh" }}
        >
          <MiniMap />
          <Controls />
          <Background gap={16} color="#e6e7eb" />
        </ReactFlow>
      </div>

      {/* right properties panel */}
      <div style={{ width: 300, padding: 12, borderLeft: "1px solid #e5e7eb", background: "#fff" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h3 style={{ margin: 0 }}>Node properties</h3>
          <button onClick={deleteSelectedNode} disabled={!selectedNodeId}>
            Delete
          </button>
        </div>

        <div style={{ marginTop: 12 }}>
          {selectedNode ? (
            <NodeProperties
              node={selectedNode}
              onUpdate={(newData) => {
                setNodes((nds) => nds.map((n) => (n.id === selectedNode.id ? { ...n, data: { ...n.data, ...newData } } : n)));
              }}
            />
          ) : (
            <div style={{ color: "#6b7280" }}>Select a node to edit</div>
          )}
        </div>
      </div>
    </div>
  );
}
