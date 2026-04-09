"use client";

import { useRef, useEffect, useState, useCallback, useMemo } from "react";
import * as d3Hierarchy from "d3-hierarchy";
import * as d3Zoom from "d3-zoom";
import { select } from "d3";
import type { TreeNode } from "@/lib/api";

interface TreeViewProps {
  arbol: TreeNode | null;
  totalNodos?: number;
  profundidad?: number;
}

interface FlatNode {
  data: TreeNode;
  x: number;
  y: number;
  parent: FlatNode | null;
  children?: FlatNode[];
  depth: number;
}

export function TreeView({ arbol, totalNodos, profundidad }: TreeViewProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const gRef = useRef<SVGGElement>(null);
  const [collapsedSet, setCollapsedSet] = useState<Set<string>>(new Set());
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

  /* Resize observer */
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const obs = new ResizeObserver((entries) => {
      const entry = entries[0];
      if (entry) {
        setDimensions({
          width: entry.contentRect.width,
          height: entry.contentRect.height,
        });
      }
    });
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  /* Generate unique node id based on path */
  const nodeId = useCallback(
    (node: TreeNode, path: string = "root"): string => `${path}/${node.simbolo}`,
    []
  );

  /* Filter tree based on collapsed nodes */
  const filterTree = useCallback(
    (node: TreeNode, path: string = "root"): TreeNode => {
      const id = nodeId(node, path);
      if (collapsedSet.has(id)) {
        return { ...node, hijos: [] };
      }
      return {
        ...node,
        hijos: (node.hijos || []).map((child, i) =>
          filterTree(child, `${id}/${i}`)
        ),
      };
    },
    [collapsedSet, nodeId]
  );

  const filteredTree = useMemo(
    () => (arbol ? filterTree(arbol) : null),
    [arbol, filterTree]
  );

  /* Compute d3 layout */
  const layoutData = useMemo(() => {
    if (!filteredTree) return null;

    const root = d3Hierarchy.hierarchy(filteredTree, (d) => d.hijos || []);
    const nodeWidth = 110;
    const nodeHeight = 50;
    const treeLayout = d3Hierarchy.tree<TreeNode>().nodeSize([nodeWidth, nodeHeight]);
    treeLayout(root);

    return root;
  }, [filteredTree]);

  /* D3 zoom */
  useEffect(() => {
    if (!svgRef.current || !gRef.current) return;

    const svg = select(svgRef.current);
    const g = select(gRef.current);

    const zoom = d3Zoom
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 3])
      .on("zoom", (event) => {
        g.attr("transform", event.transform.toString());
      });

    svg.call(zoom);

    /* Center the tree initially */
    if (layoutData) {
      const centerX = dimensions.width / 2;
      const centerY = 40;
      svg.call(
        zoom.transform,
        d3Zoom.zoomIdentity.translate(centerX, centerY).scale(0.85)
      );
    }

    return () => {
      svg.on(".zoom", null);
    };
  }, [layoutData, dimensions]);

  const toggleCollapse = useCallback(
    (id: string) => {
      setCollapsedSet((prev) => {
        const next = new Set(prev);
        if (next.has(id)) {
          next.delete(id);
        } else {
          next.add(id);
        }
        return next;
      });
    },
    []
  );

  if (!arbol || !layoutData) {
    return (
      <div className="flex h-full items-center justify-center" style={{ color: "var(--color-muted)" }}>
        <p className="text-sm">Ejecuta el analisis sintactico para ver el arbol.</p>
      </div>
    );
  }

  const nodes = layoutData.descendants() as unknown as FlatNode[];
  const links = layoutData.links() as unknown as Array<{
    source: FlatNode;
    target: FlatNode;
  }>;

  /* Build path-based IDs for toggle */
  function getNodePath(node: FlatNode, depth: number = 0): string {
    if (!node.parent) return "root/" + node.data.simbolo;
    const parentPath = getNodePath(node.parent, depth + 1);
    const idx = node.parent.children?.indexOf(node) ?? 0;
    return `${parentPath}/${idx}/${node.data.simbolo}`;
  }

  return (
    <div ref={containerRef} className="relative h-full w-full overflow-hidden">
      {/* Stats bar */}
      <div
        className="absolute top-2 left-2 z-10 flex gap-3 rounded-md px-2 py-1 text-[0.65rem]"
        style={{ backgroundColor: "var(--color-surface)", border: "1px solid var(--color-border)", color: "var(--color-muted)" }}
      >
        {totalNodos !== undefined && <span>Nodos: {totalNodos}</span>}
        {profundidad !== undefined && <span>Profundidad: {profundidad}</span>}
      </div>

      <svg
        ref={svgRef}
        width={dimensions.width}
        height={dimensions.height}
        className="h-full w-full"
        role="img"
        aria-label="Arbol de derivacion sintactica"
      >
        <g ref={gRef}>
          {/* Links */}
          {links.map((link, i) => (
            <line
              key={`link-${i}`}
              x1={link.source.x}
              y1={link.source.y}
              x2={link.target.x}
              y2={link.target.y}
              stroke="var(--tree-edge)"
              strokeWidth={1.5}
              strokeOpacity={0.6}
            />
          ))}

          {/* Nodes */}
          {nodes.map((node, i) => {
            const d = node.data;
            const isNonTerminal = !d.es_terminal && !d.es_epsilon;
            const isEpsilon = d.es_epsilon;
            const hasChildren = (d.hijos?.length ?? 0) > 0;
            const nodePath = getNodePath(node);

            let fill = "var(--tree-terminal)";
            if (isNonTerminal) fill = "var(--tree-nonterminal)";
            if (isEpsilon) fill = "var(--tree-epsilon)";

            const label = d.es_epsilon
              ? "\u03B5"
              : d.es_terminal
              ? d.lexema || d.simbolo
              : d.simbolo;

            return (
              <g
                key={`node-${i}`}
                transform={`translate(${node.x}, ${node.y})`}
                className="cursor-pointer"
                onClick={() => {
                  if (isNonTerminal && hasChildren) {
                    toggleCollapse(nodePath);
                  }
                }}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    if (isNonTerminal && hasChildren) {
                      toggleCollapse(nodePath);
                    }
                  }
                }}
                tabIndex={isNonTerminal && hasChildren ? 0 : -1}
                role={isNonTerminal && hasChildren ? "button" : "img"}
                aria-label={`${isNonTerminal ? "No terminal" : isEpsilon ? "Epsilon" : "Terminal"}: ${label}`}
                aria-expanded={
                  isNonTerminal && hasChildren
                    ? !collapsedSet.has(nodePath)
                    : undefined
                }
              >
                <rect
                  x={-45}
                  y={-14}
                  width={90}
                  height={28}
                  rx={isNonTerminal ? 6 : 12}
                  fill={fill}
                  fillOpacity={0.15}
                  stroke={fill}
                  strokeWidth={1.5}
                  className="transition-[fill-opacity] duration-150 ease-out hover:fill-opacity-25"
                />
                <text
                  textAnchor="middle"
                  dy="0.35em"
                  fill={fill}
                  fontSize={11}
                  fontFamily="var(--font-mono)"
                  fontWeight={isNonTerminal ? 600 : 400}
                  style={{ pointerEvents: "none" }}
                >
                  {label.length > 12 ? label.slice(0, 11) + "\u2026" : label}
                </text>
                {/* Collapse indicator */}
                {isNonTerminal && collapsedSet.has(nodePath) && (
                  <circle cx={38} cy={-8} r={4} fill={fill} fillOpacity={0.5} />
                )}
              </g>
            );
          })}
        </g>
      </svg>
    </div>
  );
}
