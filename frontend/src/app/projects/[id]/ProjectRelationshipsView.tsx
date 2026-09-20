"use client";

import React, { useState, useMemo, useCallback, useEffect } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Position,
  Handle,
  MarkerType,
  Node,
  Edge
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import dagre from "@dagrejs/dagre";
import {
  GitFork,
  Layers,
  FileCode,
  Box,
  ArrowRight,
  RefreshCw,
  Info,
  CheckCircle2,
  Workflow,
  Sparkles,
  Search,
  ExternalLink,
  CornerDownRight,
  ShieldCheck,
  Cpu
} from "lucide-react";

// ============================================================================
// Types
// ============================================================================
export interface RelationshipData {
  file_nodes: Array<{
    id: string;
    type: string;
    data: {
      label: string;
      module: string;
      role: string;
      badgeColor: string;
      level: number;
      classes: string[];
      functions: string[];
      dependsOn: string[];
      dependedBy: string[];
      classesCount: number;
      functionsCount: number;
    };
  }>;
  file_edges: Array<{
    id: string;
    source: string;
    target: string;
    label: string;
    type: string;
    animated?: boolean;
    style?: any;
  }>;
  class_nodes: Array<{
    id: string;
    type: string;
    data: {
      label: string;
      file: string;
      level: number;
      isException: boolean;
      isEnum: boolean;
      bases: string[];
      methodsCount: number;
      methods: string[];
    };
  }>;
  class_edges: Array<{
    id: string;
    source: string;
    target: string;
    label: string;
    type: string;
    style?: any;
  }>;
  tree: {
    max_depth: number;
    levels: Record<string, string[]>;
    roots: string[];
    leafs: string[];
  };
  stats: {
    total_files: number;
    total_classes: number;
    total_dependencies: number;
    total_class_relationships: number;
  };
}

interface ProjectRelationshipsViewProps {
  data: RelationshipData | null;
  loading: boolean;
  onRefresh: () => void;
  onSelectFile?: (filename: string) => void;
}

// ============================================================================
// Dagre Auto-Layout Helper
// ============================================================================
const getLayoutedElements = (
  nodes: Node[],
  edges: Edge[],
  direction = "TB"
) => {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));

  const isHorizontal = direction === "LR";
  dagreGraph.setGraph({
    rankdir: direction,
    nodesep: 80,
    ranksep: 120,
    align: "UL"
  });

  const nodeWidth = 280;
  const nodeHeight = 140;

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  const layoutedNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    return {
      ...node,
      targetPosition: isHorizontal ? Position.Left : Position.Top,
      sourcePosition: isHorizontal ? Position.Right : Position.Bottom,
      position: {
        x: nodeWithPosition.x - nodeWidth / 2,
        y: nodeWithPosition.y - nodeHeight / 2
      }
    };
  });

  return { nodes: layoutedNodes, edges };
};

// ============================================================================
// Custom Node: FileNode
// ============================================================================
const CustomFileNode = ({ data, selected }: any) => {
  const isRoot = data.level === 0 && data.role?.includes("Orchestrator");
  const isLeaf = data.dependsOn?.length === 0;

  return (
    <div
      className={`w-72 rounded-xl bg-gray-900/90 border transition-all duration-200 shadow-xl backdrop-blur-md overflow-hidden ${
        selected
          ? "border-indigo-500 ring-2 ring-indigo-500/30 shadow-indigo-500/20"
          : isRoot
          ? "border-indigo-500/60 shadow-indigo-950/40"
          : isLeaf
          ? "border-emerald-500/50 shadow-emerald-950/30"
          : "border-gray-800 hover:border-gray-700"
      }`}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="!bg-indigo-500 !w-2.5 !h-2.5 !border-2 !border-gray-950"
      />

      {/* Header */}
      <div className="p-3 border-b border-gray-800/80 bg-gray-950/60 flex items-center justify-between">
        <div className="flex items-center gap-2 min-w-0">
          <div
            className={`p-1.5 rounded-lg shrink-0 ${
              isRoot
                ? "bg-indigo-500/10 text-indigo-400"
                : isLeaf
                ? "bg-emerald-500/10 text-emerald-400"
                : "bg-cyan-500/10 text-cyan-400"
            }`}
          >
            <FileCode className="h-4 w-4" />
          </div>
          <span className="text-xs font-bold text-gray-200 truncate font-mono">
            {data.label}
          </span>
        </div>
        <span
          className={`text-[10px] font-semibold px-2 py-0.5 rounded-full uppercase tracking-wider shrink-0 ${
            isRoot
              ? "bg-indigo-500/20 text-indigo-300 border border-indigo-500/30"
              : isLeaf
              ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
              : "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30"
          }`}
        >
          Lvl {data.level}
        </span>
      </div>

      {/* Body */}
      <div className="p-3 space-y-2 text-xs">
        <div className="flex items-center justify-between text-gray-400 text-[11px]">
          <span className="flex items-center gap-1">
            <Box className="h-3 w-3 text-indigo-400" />
            <span>Classes:</span>
            <span className="font-semibold text-gray-200">{data.classesCount || 0}</span>
          </span>
          <span className="flex items-center gap-1">
            <Cpu className="h-3 w-3 text-purple-400" />
            <span>Funcs:</span>
            <span className="font-semibold text-gray-200">{data.functionsCount || 0}</span>
          </span>
        </div>

        {/* Classes pill badges */}
        {data.classes && data.classes.length > 0 && (
          <div className="flex flex-wrap gap-1 pt-1">
            {data.classes.slice(0, 3).map((c: string) => (
              <span
                key={c}
                className="px-1.5 py-0.5 rounded bg-gray-800 text-gray-300 text-[10px] font-mono border border-gray-700/50"
              >
                {c}
              </span>
            ))}
            {data.classes.length > 3 && (
              <span className="px-1.5 py-0.5 rounded bg-gray-800/60 text-gray-500 text-[10px]">
                +{data.classes.length - 3}
              </span>
            )}
          </div>
        )}

        {/* Dependency stats */}
        <div className="pt-2 border-t border-gray-800/60 flex items-center justify-between text-[10px] text-gray-500">
          <span>Depends on: <strong className="text-gray-300">{data.dependsOn?.length || 0}</strong></span>
          <span>Depended by: <strong className="text-gray-300">{data.dependedBy?.length || 0}</strong></span>
        </div>
      </div>

      <Handle
        type="source"
        position={Position.Bottom}
        className="!bg-indigo-500 !w-2.5 !h-2.5 !border-2 !border-gray-950"
      />
    </div>
  );
};

// ============================================================================
// Custom Node: ClassNode
// ============================================================================
const CustomClassNode = ({ data, selected }: any) => {
  return (
    <div
      className={`w-64 rounded-xl bg-gray-900/90 border transition-all duration-200 shadow-xl backdrop-blur-md overflow-hidden ${
        selected
          ? "border-purple-500 ring-2 ring-purple-500/30 shadow-purple-500/20"
          : "border-gray-800 hover:border-gray-700"
      }`}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="!bg-purple-500 !w-2.5 !h-2.5 !border-2 !border-gray-950"
      />

      <div className="p-3 border-b border-gray-800/80 bg-gray-950/60 flex items-center justify-between">
        <div className="flex items-center gap-2 min-w-0">
          <div className="p-1.5 rounded-lg bg-purple-500/10 text-purple-400 shrink-0">
            <Box className="h-4 w-4" />
          </div>
          <span className="text-xs font-bold text-gray-200 truncate font-mono">
            {data.label}
          </span>
        </div>
        {data.isException ? (
          <span className="text-[10px] bg-red-500/20 text-red-300 px-1.5 py-0.5 rounded border border-red-500/30">
            Exception
          </span>
        ) : data.isEnum ? (
          <span className="text-[10px] bg-amber-500/20 text-amber-300 px-1.5 py-0.5 rounded border border-amber-500/30">
            Enum
          </span>
        ) : (
          <span className="text-[10px] bg-purple-500/20 text-purple-300 px-1.5 py-0.5 rounded border border-purple-500/30">
            Class
          </span>
        )}
      </div>

      <div className="p-3 space-y-2 text-xs">
        <div className="text-[11px] text-gray-400 truncate">
          File: <span className="font-mono text-gray-300">{data.file}</span>
        </div>

        {data.bases && data.bases.length > 0 && (
          <div className="text-[10px] text-gray-400">
            Extends: <span className="text-indigo-300 font-mono">{data.bases.join(", ")}</span>
          </div>
        )}

        <div className="text-[10px] text-gray-500">
          Methods: <strong className="text-gray-300">{data.methodsCount || 0}</strong>
        </div>
      </div>

      <Handle
        type="source"
        position={Position.Bottom}
        className="!bg-purple-500 !w-2.5 !h-2.5 !border-2 !border-gray-950"
      />
    </div>
  );
};

const nodeTypes = {
  fileNode: CustomFileNode,
  classNode: CustomClassNode
};

// ============================================================================
// Main View Component
// ============================================================================
export const ProjectRelationshipsView: React.FC<ProjectRelationshipsViewProps> = ({
  data,
  loading,
  onRefresh,
  onSelectFile
}) => {
  const [viewMode, setViewMode] = useState<"files" | "classes" | "tree">("files");
  const [layoutDir, setLayoutDir] = useState<"TB" | "LR">("TB");
  const [selectedNode, setSelectedNode] = useState<any | null>(null);

  // Raw elements based on selected mode
  const { initialNodes, initialEdges } = useMemo(() => {
    if (!data) return { initialNodes: [], initialEdges: [] };

    let n: Node[] = [];
    let e: Edge[] = [];

    if (viewMode === "files") {
      n = data.file_nodes.map((fn) => ({
        id: fn.id,
        type: "fileNode",
        position: { x: 0, y: 0 },
        data: fn.data
      }));

      e = data.file_edges.map((fe) => ({
        id: fe.id,
        source: fe.source,
        target: fe.target,
        label: fe.label,
        type: "smoothstep",
        animated: true,
        markerEnd: { type: MarkerType.ArrowClosed, color: fe.style?.stroke || "#6366f1" },
        style: fe.style || { stroke: "#6366f1", strokeWidth: 2 }
      }));
    } else if (viewMode === "classes") {
      n = data.class_nodes.map((cn) => ({
        id: cn.id,
        type: "classNode",
        position: { x: 0, y: 0 },
        data: cn.data
      }));

      e = data.class_edges.map((ce) => ({
        id: ce.id,
        source: ce.source,
        target: ce.target,
        label: ce.label,
        type: "smoothstep",
        markerEnd: { type: MarkerType.ArrowClosed, color: ce.style?.stroke || "#a855f7" },
        style: ce.style || { stroke: "#a855f7", strokeWidth: 2 }
      }));
    }

    const layouted = getLayoutedElements(n, e, layoutDir);
    return { initialNodes: layouted.nodes, initialEdges: layouted.edges };
  }, [data, viewMode, layoutDir]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  useEffect(() => {
    setNodes(initialNodes);
    setEdges(initialEdges);
  }, [initialNodes, initialEdges, setNodes, setEdges]);

  const onNodeClick = useCallback((_: any, node: Node) => {
    setSelectedNode(node);
  }, []);

  if (loading) {
    return (
      <div className="w-full h-full flex flex-col items-center justify-center bg-gray-950 text-gray-400 gap-3">
        <RefreshCw className="h-8 w-8 animate-spin text-indigo-500" />
        <p className="text-xs font-semibold">Analyzing project architecture and relationships...</p>
      </div>
    );
  }

  if (!data || data.stats.total_files === 0) {
    return (
      <div className="w-full h-full flex flex-col items-center justify-center bg-gray-950 text-gray-500 p-8 text-center">
        <Workflow className="h-12 w-12 text-gray-700 mb-3" />
        <h3 className="text-base font-bold text-gray-300 mb-1">No Files Uploaded Yet</h3>
        <p className="text-xs text-gray-500 max-w-sm">
          Upload Python source files to TestForge to automatically map file-to-file imports,
          class hierarchies, and multi-component dependency trees.
        </p>
      </div>
    );
  }

  return (
    <div className="w-full h-full flex flex-col bg-gray-950 overflow-hidden relative">
      {/* Top Header Bar */}
      <div className="px-6 py-2.5 border-b border-gray-900 bg-gray-950/80 backdrop-blur-md flex flex-wrap items-center justify-between gap-3 shrink-0">
        {/* Left: View Mode Pills */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => { setViewMode("files"); setSelectedNode(null); }}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              viewMode === "files"
                ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/30"
                : "bg-gray-900 text-gray-400 hover:text-white border border-gray-800"
            }`}
          >
            <GitFork className="h-3.5 w-3.5" />
            <span>File Tree Graph</span>
          </button>

          <button
            onClick={() => { setViewMode("classes"); setSelectedNode(null); }}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              viewMode === "classes"
                ? "bg-purple-600 text-white shadow-lg shadow-purple-600/30"
                : "bg-gray-900 text-gray-400 hover:text-white border border-gray-800"
            }`}
          >
            <Box className="h-3.5 w-3.5" />
            <span>Class Architecture</span>
          </button>

          <button
            onClick={() => { setViewMode("tree"); setSelectedNode(null); }}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              viewMode === "tree"
                ? "bg-cyan-600 text-white shadow-lg shadow-cyan-600/30"
                : "bg-gray-900 text-gray-400 hover:text-white border border-gray-800"
            }`}
          >
            <Layers className="h-3.5 w-3.5" />
            <span>Hierarchical Levels</span>
          </button>
        </div>

        {/* Middle Stats Badges */}
        <div className="hidden lg:flex items-center gap-4 text-xs font-mono text-gray-400">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-indigo-500"></span>
            Files: <strong className="text-white">{data.stats.total_files}</strong>
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-purple-500"></span>
            Classes: <strong className="text-white">{data.stats.total_classes}</strong>
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
            Dependencies: <strong className="text-white">{data.stats.total_dependencies}</strong>
          </span>
        </div>

        {/* Right Actions: Layout orientation + Refresh */}
        <div className="flex items-center gap-2">
          {viewMode !== "tree" && (
            <button
              onClick={() => setLayoutDir(layoutDir === "TB" ? "LR" : "TB")}
              title="Toggle Layout (Top-to-Bottom vs Left-to-Right)"
              className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-gray-900 border border-gray-800 text-gray-400 hover:text-white text-xs font-semibold transition-all cursor-pointer"
            >
              <span>{layoutDir === "TB" ? "Vertical Tree (TB)" : "Horizontal Tree (LR)"}</span>
            </button>
          )}

          <button
            onClick={onRefresh}
            title="Re-analyze relationships"
            className="p-1.5 rounded-lg bg-gray-900 border border-gray-800 text-gray-400 hover:text-white transition-all cursor-pointer"
          >
            <RefreshCw className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 relative overflow-hidden">
        {viewMode === "tree" ? (
          /* Hierarchical Levels View */
          <div className="h-full overflow-y-auto p-6 max-w-5xl mx-auto space-y-6">
            <div className="p-4 rounded-xl bg-gray-900/60 border border-gray-800 flex items-start gap-3">
              <Info className="h-5 w-5 text-cyan-400 shrink-0 mt-0.5" />
              <div className="text-xs text-gray-300 leading-relaxed">
                <strong className="text-white font-semibold">Topological Tree Hierarchy:</strong> TestForge
                analyzed the module dependency graph to discover the exact architectural layers of your codebase.
                High-level orchestrators run at Level 0, while independent domain entities, models, and exceptions reside at the leaf levels.
              </div>
            </div>

            {/* Tree Levels */}
            <div className="space-y-4">
              {Object.entries(data.tree.levels).map(([levelName, files]) => {
                const isRootLevel = levelName === "Level 0";
                return (
                  <div
                    key={levelName}
                    className="p-5 rounded-2xl bg-gray-900/40 border border-gray-800/80 hover:border-gray-700 transition-all space-y-3"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span
                          className={`px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider ${
                            isRootLevel
                              ? "bg-indigo-500/20 text-indigo-300 border border-indigo-500/30"
                              : "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30"
                          }`}
                        >
                          {levelName}
                        </span>
                        <span className="text-xs font-semibold text-gray-400">
                          {isRootLevel
                            ? "— Root Orchestrators & Entrypoints"
                            : files.some((f) => data.tree.leafs.includes(f))
                            ? "— Leaf Models & Standalone Modules"
                            : "— Domain Components & Services"}
                        </span>
                      </div>
                      <span className="text-xs text-gray-500 font-mono">
                        {files.length} {files.length === 1 ? "file" : "files"}
                      </span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                      {files.map((fn) => {
                        const fileNode = data.file_nodes.find((n) => n.data.label === fn);
                        const isLeaf = data.tree.leafs.includes(fn);
                        return (
                          <div
                            key={fn}
                            className="p-3.5 rounded-xl bg-gray-950/70 border border-gray-800/80 hover:border-indigo-500/50 transition-all flex flex-col justify-between space-y-2 group"
                          >
                            <div className="flex items-start justify-between gap-2">
                              <div className="flex items-center gap-2 min-w-0">
                                <FileCode className="h-4 w-4 text-indigo-400 shrink-0" />
                                <span className="text-xs font-bold font-mono text-gray-200 truncate group-hover:text-indigo-300 transition-colors">
                                  {fn}
                                </span>
                              </div>
                              {onSelectFile && (
                                <button
                                  onClick={() => onSelectFile(fn)}
                                  title="Inspect file"
                                  className="text-gray-500 hover:text-indigo-400 transition-colors p-1 rounded cursor-pointer"
                                >
                                  <ExternalLink className="h-3.5 w-3.5" />
                                </button>
                              )}
                            </div>

                            {fileNode && fileNode.data.classes.length > 0 && (
                              <div className="flex flex-wrap gap-1">
                                {fileNode.data.classes.map((cls) => (
                                  <span
                                    key={cls}
                                    className="px-1.5 py-0.5 rounded bg-gray-900 border border-gray-800 text-[10px] font-mono text-gray-300"
                                  >
                                    {cls}
                                  </span>
                                ))}
                              </div>
                            )}

                            <div className="pt-2 border-t border-gray-900 text-[10px] text-gray-500 flex items-center justify-between">
                              <span>Depends on: <strong className="text-gray-300">{fileNode?.data.dependsOn.length || 0}</strong></span>
                              <span>Depended by: <strong className="text-gray-300">{fileNode?.data.dependedBy.length || 0}</strong></span>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ) : (
          /* React Flow Interactive Graph Canvas */
          <div className="w-full h-full relative">
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onNodeClick={onNodeClick}
              nodeTypes={nodeTypes}
              fitView
              className="bg-gray-950"
            >
              <Background color="#1f2937" gap={20} size={1} />
              <Controls className="!bg-gray-900 !border-gray-800 !text-white [&>button]:!border-gray-800 [&>button]:!bg-gray-900 [&>button]:!text-gray-300" />
              <MiniMap
                nodeColor={(n) => (n.type === "fileNode" ? "#6366f1" : "#a855f7")}
                className="!bg-gray-900/90 !border-gray-800 rounded-xl overflow-hidden"
              />
            </ReactFlow>

            {/* Side Detail Drawer (When Node Clicked) */}
            {selectedNode && (
              <div className="absolute top-4 right-4 w-80 max-h-[85%] overflow-y-auto rounded-2xl bg-gray-900/95 border border-gray-800 shadow-2xl backdrop-blur-xl p-5 space-y-4 z-10 transition-all animate-in fade-in slide-in-from-right-4">
                <div className="flex items-center justify-between border-b border-gray-800 pb-3">
                  <div className="flex items-center gap-2 min-w-0">
                    <Box className="h-4 w-4 text-indigo-400 shrink-0" />
                    <span className="text-xs font-bold text-white font-mono truncate">
                      {selectedNode.data.label}
                    </span>
                  </div>
                  <button
                    onClick={() => setSelectedNode(null)}
                    className="text-gray-500 hover:text-white text-xs cursor-pointer p-1 rounded"
                  >
                    ✕
                  </button>
                </div>

                {selectedNode.type === "fileNode" ? (
                  <>
                    <div className="space-y-1.5 text-xs">
                      <div className="text-gray-400 text-[11px]">Architectural Role:</div>
                      <div className="font-semibold text-indigo-300">{selectedNode.data.role}</div>
                      <div className="text-gray-500 text-[10px]">Hierarchy Level: {selectedNode.data.level}</div>
                    </div>

                    {selectedNode.data.classes?.length > 0 && (
                      <div className="space-y-1.5 text-xs">
                        <div className="text-gray-400 text-[11px]">Classes Defined:</div>
                        <div className="flex flex-wrap gap-1">
                          {selectedNode.data.classes.map((cls: string) => (
                            <span key={cls} className="px-2 py-0.5 rounded bg-gray-800 border border-gray-700 text-gray-200 text-[11px] font-mono">
                              {cls}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {selectedNode.data.dependsOn?.length > 0 && (
                      <div className="space-y-1.5 text-xs">
                        <div className="text-gray-400 text-[11px]">Depends On ({selectedNode.data.dependsOn.length}):</div>
                        <div className="space-y-1">
                          {selectedNode.data.dependsOn.map((dep: string) => (
                            <div key={dep} className="flex items-center gap-1 text-emerald-400 text-[11px] font-mono bg-emerald-950/30 px-2 py-1 rounded border border-emerald-900/30">
                              <ArrowRight className="h-3 w-3" />
                              <span>{dep}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {selectedNode.data.dependedBy?.length > 0 && (
                      <div className="space-y-1.5 text-xs">
                        <div className="text-gray-400 text-[11px]">Depended By ({selectedNode.data.dependedBy.length}):</div>
                        <div className="space-y-1">
                          {selectedNode.data.dependedBy.map((dep: string) => (
                            <div key={dep} className="flex items-center gap-1 text-indigo-300 text-[11px] font-mono bg-indigo-950/30 px-2 py-1 rounded border border-indigo-900/30">
                              <CornerDownRight className="h-3 w-3" />
                              <span>{dep}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {onSelectFile && (
                      <button
                        onClick={() => onSelectFile(selectedNode.data.label)}
                        className="w-full mt-2 flex items-center justify-center gap-1.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition-all cursor-pointer shadow-lg shadow-indigo-600/30"
                      >
                        <FileCode className="h-3.5 w-3.5" />
                        <span>Inspect in Code View</span>
                      </button>
                    )}
                  </>
                ) : (
                  <>
                    <div className="space-y-1.5 text-xs">
                      <div className="text-gray-400 text-[11px]">Belongs to File:</div>
                      <div className="font-mono text-gray-200">{selectedNode.data.file}</div>
                    </div>

                    {selectedNode.data.bases?.length > 0 && (
                      <div className="space-y-1.5 text-xs">
                        <div className="text-gray-400 text-[11px]">Inheritance Bases:</div>
                        <div className="font-mono text-purple-300">{selectedNode.data.bases.join(", ")}</div>
                      </div>
                    )}

                    {selectedNode.data.methods?.length > 0 && (
                      <div className="space-y-1.5 text-xs">
                        <div className="text-gray-400 text-[11px]">Methods ({selectedNode.data.methods.length}):</div>
                        <div className="flex flex-wrap gap-1 max-h-32 overflow-y-auto">
                          {selectedNode.data.methods.map((m: string) => (
                            <span key={m} className="px-1.5 py-0.5 rounded bg-gray-800 text-gray-300 text-[10px] font-mono">
                              {m}()
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
