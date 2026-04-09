"use client";

import { useState } from "react";
import type { MapeoLinea } from "@/lib/api";
import { ScrollArea } from "@/components/ui/scroll-area";

interface SwiftViewProps {
  claudioCode: string;
  swiftCode: string;
  mapeo: MapeoLinea[];
}

export function SwiftView({ claudioCode, swiftCode, mapeo }: SwiftViewProps) {
  const [hoveredLine, setHoveredLine] = useState<number | null>(null);

  if (!swiftCode) {
    return (
      <div className="flex h-full items-center justify-center" style={{ color: "var(--color-muted)" }}>
        <p className="text-sm">Ejecuta la traduccion para ver el codigo Swift.</p>
      </div>
    );
  }

  const claudioLines = claudioCode.split("\n");
  const swiftLines = swiftCode.split("\n");

  return (
    <div className="flex h-full flex-col md:flex-row">
      {/* Claudio side */}
      <div className="flex flex-1 flex-col overflow-hidden" style={{ borderRight: "1px solid var(--color-border)" }}>
        <div
          className="shrink-0 px-3 py-1.5 text-[0.65rem] font-semibold uppercase tracking-wider"
          style={{
            backgroundColor: "var(--color-surface)",
            borderBottom: "1px solid var(--color-border)",
            color: "var(--token-keyword)",
          }}
        >
          Claudio
        </div>
        <ScrollArea className="flex-1">
          <pre className="p-2 text-[0.7rem] leading-5 font-mono" style={{ color: "var(--color-text)" }}>
            {claudioLines.map((line, i) => (
              <div
                key={i}
                className="flex transition-colors duration-150 ease-out"
                style={{
                  backgroundColor:
                    hoveredLine === i ? "rgba(137, 180, 250, 0.1)" : "transparent",
                }}
                onMouseEnter={() => setHoveredLine(i)}
                onMouseLeave={() => setHoveredLine(null)}
              >
                <span
                  className="mr-3 inline-block w-6 shrink-0 text-right select-none"
                  style={{ color: "var(--color-muted)" }}
                  aria-hidden="true"
                >
                  {i + 1}
                </span>
                <span className="whitespace-pre">{line}</span>
              </div>
            ))}
          </pre>
        </ScrollArea>
      </div>

      {/* Swift side */}
      <div className="flex flex-1 flex-col overflow-hidden">
        <div
          className="shrink-0 px-3 py-1.5 text-[0.65rem] font-semibold uppercase tracking-wider"
          style={{
            backgroundColor: "var(--color-surface)",
            borderBottom: "1px solid var(--color-border)",
            color: "var(--color-warning)",
          }}
        >
          Swift
        </div>
        <ScrollArea className="flex-1">
          <pre className="p-2 text-[0.7rem] leading-5 font-mono" style={{ color: "var(--color-text)" }}>
            {swiftLines.map((line, i) => (
              <div
                key={i}
                className="flex transition-colors duration-150 ease-out"
                style={{
                  backgroundColor:
                    hoveredLine === i ? "rgba(137, 180, 250, 0.1)" : "transparent",
                }}
                onMouseEnter={() => setHoveredLine(i)}
                onMouseLeave={() => setHoveredLine(null)}
              >
                <span
                  className="mr-3 inline-block w-6 shrink-0 text-right select-none"
                  style={{ color: "var(--color-muted)" }}
                  aria-hidden="true"
                >
                  {i + 1}
                </span>
                <span className="whitespace-pre">{line}</span>
              </div>
            ))}
          </pre>
        </ScrollArea>
      </div>

      {/* Mapping overlay (shown in a tooltip-like fashion on wider screens) */}
      {mapeo.length > 0 && (
        <div
          className="hidden w-36 shrink-0 flex-col lg:flex"
          style={{ borderLeft: "1px solid var(--color-border)" }}
        >
          <div
            className="shrink-0 px-2 py-1.5 text-[0.6rem] font-semibold uppercase tracking-wider"
            style={{
              backgroundColor: "var(--color-surface)",
              borderBottom: "1px solid var(--color-border)",
              color: "var(--color-muted)",
            }}
          >
            Mapeo
          </div>
          <ScrollArea className="flex-1">
            <div className="p-1 text-[0.55rem] font-mono">
              {mapeo.map((m, i) => (
                <div
                  key={i}
                  className="rounded px-1 py-0.5 transition-colors duration-150 ease-out"
                  style={{
                    backgroundColor:
                      hoveredLine === i ? "rgba(137, 180, 250, 0.1)" : "transparent",
                    color: "var(--color-text)",
                  }}
                  onMouseEnter={() => setHoveredLine(i)}
                  onMouseLeave={() => setHoveredLine(null)}
                >
                  <span style={{ color: "var(--token-keyword)" }}>{m.claudio}</span>
                  <span style={{ color: "var(--color-muted)" }}> {"\u2192"} </span>
                  <span style={{ color: "var(--color-warning)" }}>{m.swift}</span>
                </div>
              ))}
            </div>
          </ScrollArea>
        </div>
      )}
    </div>
  );
}
