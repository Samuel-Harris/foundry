/**
 * Paste this into a canvas. A canvas is one file, so this cannot be imported.
 * Merge the import below into the canvas's own `cursor/canvas` import.
 */
import { useHostTheme } from "cursor/canvas";

type Side = "t" | "b" | "l" | "r";

type NodeKind = "state" | "accent" | "decision" | "terminal";

type ChartNode = {
  id: string;
  x: number;
  y: number;
  w: number;
  h: number;
  title: string;
  sub?: string[];
  kind?: NodeKind;
};

type ChartEdge = {
  from: string;
  to: string;
  fromSide: Side;
  toSide: Side;
  fromOff?: number;
  toOff?: number;
  label?: string[];
  dashed?: boolean;
  bend?: number;
  labelT?: number;
  labelDx?: number;
  labelDy?: number;
};

type Point = { x: number; y: number };

const NORMALS: Record<Side, Point> = {
  t: { x: 0, y: -1 },
  b: { x: 0, y: 1 },
  l: { x: -1, y: 0 },
  r: { x: 1, y: 0 },
};

function anchor(node: ChartNode, side: Side, off: number): Point {
  if (side === "t") return { x: node.x + node.w / 2 + off, y: node.y };
  if (side === "b") return { x: node.x + node.w / 2 + off, y: node.y + node.h };
  if (side === "l") return { x: node.x, y: node.y + node.h / 2 + off };
  return { x: node.x + node.w, y: node.y + node.h / 2 + off };
}

function controlDistance(side: Side, a: Point, b: Point, sameSide: boolean, bend?: number): number {
  if (bend !== undefined) return bend;
  if (sameSide) return 50;
  const delta = side === "t" || side === "b" ? Math.abs(b.y - a.y) : Math.abs(b.x - a.x);
  return delta * 0.5;
}

function cubicAt(p0: Point, p1: Point, p2: Point, p3: Point, t: number): Point {
  const u = 1 - t;
  return {
    x: u * u * u * p0.x + 3 * u * u * t * p1.x + 3 * u * t * t * p2.x + t * t * t * p3.x,
    y: u * u * u * p0.y + 3 * u * u * t * p1.y + 3 * u * t * t * p2.y + t * t * t * p3.y,
  };
}

function StateChart({
  id,
  width,
  height,
  nodes,
  edges,
}: {
  id: string;
  width: number;
  height: number;
  nodes: ChartNode[];
  edges: ChartEdge[];
}) {
  const theme = useHostTheme();
  const byId = new Map(nodes.map((node) => [node.id, node]));
  const lineColor = theme.text.tertiary;

  return (
    <div style={{ overflowX: "auto" }}>
      <svg
        viewBox={`0 0 ${width} ${height}`}
        width="100%"
        style={{ minWidth: width * 0.8, maxWidth: width, display: "block" }}
        role="img"
      >
        <defs>
          <marker id={`${id}-arrow`} viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">
            <path d="M 0 0 L 10 5 L 0 10 z" fill={lineColor} />
          </marker>
        </defs>
        {edges.map((edge, index) => {
          const from = byId.get(edge.from);
          const to = byId.get(edge.to);
          if (!from || !to) return null;
          const a = anchor(from, edge.fromSide, edge.fromOff ?? 0);
          const b = anchor(to, edge.toSide, edge.toOff ?? 0);
          const sameSide = edge.fromSide === edge.toSide;
          const d1 = controlDistance(edge.fromSide, a, b, sameSide, edge.bend);
          const d2 = controlDistance(edge.toSide, b, a, sameSide, edge.bend);
          const c1 = { x: a.x + NORMALS[edge.fromSide].x * d1, y: a.y + NORMALS[edge.fromSide].y * d1 };
          const c2 = { x: b.x + NORMALS[edge.toSide].x * d2, y: b.y + NORMALS[edge.toSide].y * d2 };
          const mid = cubicAt(a, c1, c2, b, edge.labelT ?? 0.5);
          const lines = edge.label ?? [];
          const labelWidth = Math.max(0, ...lines.map((line) => line.length)) * 6.1 + 12;
          const labelHeight = lines.length * 14 + 4;
          const lx = mid.x + (edge.labelDx ?? 0);
          const ly = mid.y + (edge.labelDy ?? 0);
          return (
            <g key={`${edge.from}-${edge.to}-${index}`}>
              <path
                d={`M ${a.x} ${a.y} C ${c1.x} ${c1.y}, ${c2.x} ${c2.y}, ${b.x} ${b.y}`}
                fill="none"
                stroke={lineColor}
                strokeWidth={1.2}
                strokeDasharray={edge.dashed ? "5 4" : undefined}
                markerEnd={`url(#${id}-arrow)`}
              />
              {lines.length > 0 && (
                <g>
                  <rect
                    x={lx - labelWidth / 2}
                    y={ly - labelHeight / 2}
                    width={labelWidth}
                    height={labelHeight}
                    fill={theme.bg.editor}
                  />
                  {lines.map((line, lineIndex) => (
                    <text
                      key={lineIndex}
                      x={lx}
                      y={ly - ((lines.length - 1) * 14) / 2 + lineIndex * 14 + 4}
                      textAnchor="middle"
                      fontSize={11}
                      fill={theme.text.secondary}
                    >
                      {line}
                    </text>
                  ))}
                </g>
              )}
            </g>
          );
        })}
        {nodes.map((node) => {
          const kind = node.kind ?? "state";
          const sub = node.sub ?? [];
          const lineCount = 1 + sub.length;
          const firstY = node.y + node.h / 2 - ((lineCount - 1) * 15) / 2 + 4;
          const stroke = kind === "accent" ? theme.accent.primary : theme.stroke.primary;
          const fill =
            kind === "decision" ? theme.bg.editor : kind === "terminal" ? theme.fill.secondary : theme.fill.tertiary;
          return (
            <g key={node.id}>
              <rect
                x={node.x}
                y={node.y}
                width={node.w}
                height={node.h}
                rx={kind === "decision" ? node.h / 2 : 6}
                fill={fill}
                stroke={stroke}
                strokeWidth={kind === "accent" ? 1.6 : 1}
                strokeDasharray={kind === "decision" ? "4 3" : undefined}
              />
              <text
                x={node.x + node.w / 2}
                y={firstY}
                textAnchor="middle"
                fontSize={12}
                fontWeight={600}
                fill={theme.text.primary}
              >
                {node.title}
              </text>
              {sub.map((line, lineIndex) => (
                <text
                  key={lineIndex}
                  x={node.x + node.w / 2}
                  y={firstY + (lineIndex + 1) * 15}
                  textAnchor="middle"
                  fontSize={10.5}
                  fill={theme.text.secondary}
                >
                  {line}
                </text>
              ))}
            </g>
          );
        })}
      </svg>
    </div>
  );
}
