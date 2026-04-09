"use client";

import { useState } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ChevronDown, ChevronRight } from "lucide-react";

interface LL1TableProps {
  primero: Record<string, string[]>;
  siguiente: Record<string, string[]>;
  tablaLL1: Record<string, Record<string, string>>;
  terminales: string[];
  noTerminales: string[];
  esLL1: boolean;
  conflictos: string[];
  highlightedCell?: { nt: string; terminal: string } | null;
}

function SetSection({
  title,
  data,
}: {
  title: string;
  data: Record<string, string[]>;
}) {
  const [open, setOpen] = useState(true);
  const entries = Object.entries(data);

  return (
    <section aria-label={title}>
      <button
        onClick={() => setOpen(!open)}
        className="flex w-full items-center gap-1.5 py-1.5 text-xs font-semibold uppercase tracking-wider transition-colors duration-150 ease-out"
        style={{ color: "var(--color-muted)" }}
        aria-expanded={open}
      >
        {open ? <ChevronDown className="size-3" /> : <ChevronRight className="size-3" />}
        {title}
      </button>
      {open && (
        <div className="mb-3 flex flex-wrap gap-2">
          {entries.map(([nt, symbols]) => (
            <div
              key={nt}
              className="rounded-md px-2 py-1 text-xs font-mono"
              style={{
                backgroundColor: "var(--color-surface-2)",
                border: "1px solid var(--color-border)",
                color: "var(--color-text)",
              }}
            >
              <span style={{ color: "var(--tree-nonterminal)" }} className="font-semibold">
                {nt}
              </span>
              <span style={{ color: "var(--color-muted)" }}> = {"{ "}</span>
              {symbols.map((s, i) => (
                <span key={i}>
                  <span style={{ color: "var(--tree-terminal)" }}>{s}</span>
                  {i < symbols.length - 1 && (
                    <span style={{ color: "var(--color-muted)" }}>, </span>
                  )}
                </span>
              ))}
              <span style={{ color: "var(--color-muted)" }}>{" }"}</span>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

export function LL1Table({
  primero,
  siguiente,
  tablaLL1,
  terminales,
  noTerminales,
  esLL1,
  conflictos,
  highlightedCell,
}: LL1TableProps) {
  const hasData = noTerminales.length > 0;

  if (!hasData) {
    return (
      <div className="flex h-full items-center justify-center" style={{ color: "var(--color-muted)" }}>
        <p className="text-sm">Ejecuta el analisis LL(1) para ver la tabla.</p>
      </div>
    );
  }

  return (
    <ScrollArea className="h-full">
      <div className="p-3 space-y-2">
        {/* LL(1) status */}
        <div className="flex items-center gap-2 text-xs">
          <span
            className="inline-flex items-center rounded-md px-2 py-0.5 font-semibold"
            style={{
              backgroundColor: esLL1 ? "var(--color-success)" : "var(--color-error)",
              color: "var(--color-bg)",
            }}
          >
            {esLL1 ? "Es LL(1)" : "No es LL(1)"}
          </span>
          {conflictos.length > 0 && (
            <span style={{ color: "var(--color-error)" }}>
              {conflictos.length} conflicto{conflictos.length !== 1 ? "s" : ""}
            </span>
          )}
        </div>

        {/* Conflicts */}
        {conflictos.length > 0 && (
          <div
            className="rounded-md p-2 text-xs font-mono"
            style={{
              backgroundColor: "rgba(243, 139, 168, 0.08)",
              border: "1px solid var(--color-error)",
              color: "var(--color-error)",
            }}
          >
            {conflictos.map((c, i) => (
              <p key={i}>{c}</p>
            ))}
          </div>
        )}

        {/* FIRST / FOLLOW */}
        <SetSection title="FIRST (Primero)" data={primero} />
        <SetSection title="FOLLOW (Siguiente)" data={siguiente} />

        {/* M[A,a] table */}
        <section aria-label="Tabla M[A,a]">
          <h3
            className="mb-2 text-xs font-semibold uppercase tracking-wider"
            style={{ color: "var(--color-muted)" }}
          >
            Tabla M[A,a]
          </h3>
          <div
            className="overflow-auto rounded-md"
            style={{ border: "1px solid var(--color-border)", maxHeight: "400px" }}
          >
            <table
              className="ll1-table w-full text-[0.65rem] font-mono"
              style={{ color: "var(--color-text)" }}
            >
              <thead>
                <tr>
                  <th
                    className="px-2 py-1.5 text-left font-semibold"
                    style={{
                      backgroundColor: "var(--color-surface)",
                      borderBottom: "1px solid var(--color-border)",
                      borderRight: "1px solid var(--color-border)",
                      color: "var(--color-muted)",
                      minWidth: "80px",
                    }}
                  >
                    M[A,a]
                  </th>
                  {terminales.map((t) => (
                    <th
                      key={t}
                      className="px-2 py-1.5 text-center font-semibold whitespace-nowrap"
                      style={{
                        backgroundColor: "var(--color-surface)",
                        borderBottom: "1px solid var(--color-border)",
                        color: "var(--tree-terminal)",
                        minWidth: "60px",
                      }}
                    >
                      {t}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {noTerminales.map((nt) => (
                  <tr key={nt}>
                    <td
                      className="px-2 py-1 font-semibold whitespace-nowrap"
                      style={{
                        borderBottom: "1px solid var(--color-border)",
                        borderRight: "1px solid var(--color-border)",
                        color: "var(--tree-nonterminal)",
                        backgroundColor: "var(--color-surface)",
                      }}
                    >
                      {nt}
                    </td>
                    {terminales.map((t) => {
                      const production = tablaLL1[nt]?.[t] || "";
                      const isHighlighted =
                        highlightedCell?.nt === nt && highlightedCell?.terminal === t;
                      return (
                        <td
                          key={t}
                          className="px-2 py-1 text-center whitespace-nowrap transition-colors duration-150 ease-out"
                          style={{
                            borderBottom: "1px solid var(--color-border)",
                            backgroundColor: isHighlighted
                              ? "rgba(137, 180, 250, 0.15)"
                              : production
                              ? "var(--color-surface-2)"
                              : "transparent",
                            color: production ? "var(--color-text)" : "var(--color-border)",
                          }}
                        >
                          {production || "\u2014"}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </ScrollArea>
  );
}
