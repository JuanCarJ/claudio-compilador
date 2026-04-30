"use client";

import { useState, useMemo } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ChevronDown, ChevronRight, Search } from "lucide-react";

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
  filter,
}: {
  title: string;
  data: Record<string, string[]>;
  filter: string;
}) {
  const [open, setOpen] = useState(true);
  const entries = Object.entries(data);
  const q = filter.toLowerCase();

  const filteredEntries = q
    ? entries.filter(([nt, symbols]) =>
        nt.toLowerCase().includes(q) || symbols.some((s) => s.toLowerCase().includes(q))
      )
    : entries;

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
        {q && <span style={{ color: "var(--color-accent)", fontSize: ".65rem", fontWeight: 400, textTransform: "none" }}> ({filteredEntries.length}/{entries.length})</span>}
      </button>
      {open && (
        <div className="mb-3 flex flex-wrap gap-2">
          {filteredEntries.map(([nt, symbols]) => {
            const isMatch = q && nt.toLowerCase().includes(q);
            return (
              <div
                key={nt}
                className="rounded-md px-2 py-1 text-xs font-mono"
                style={{
                  backgroundColor: isMatch ? "rgba(137,180,250,.1)" : "var(--color-surface-2)",
                  border: isMatch ? "1.5px solid var(--color-accent)" : "1px solid var(--color-border)",
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
            );
          })}
          {filteredEntries.length === 0 && (
            <p className="text-xs" style={{ color: "var(--color-muted)" }}>
              Sin resultados para &quot;{filter}&quot;
            </p>
          )}
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
  const [tableSearch, setTableSearch] = useState("");
  const [setsSearch, setSetsSearch] = useState("");

  const filteredNTs = useMemo(() => {
    if (!tableSearch.trim()) return noTerminales;
    const q = tableSearch.toLowerCase();
    return noTerminales.filter((nt) => {
      if (nt.toLowerCase().includes(q)) return true;
      const row = tablaLL1[nt];
      if (row) {
        return Object.values(row).some((prod) => prod.toLowerCase().includes(q));
      }
      return false;
    });
  }, [noTerminales, tablaLL1, tableSearch]);

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

        {/* Search for FIRST / FOLLOW */}
        <div
          className="flex items-center gap-1.5 rounded-md px-2 py-1.5 mb-2"
          style={{ backgroundColor: "var(--color-surface-2)", border: "1px solid var(--color-border)" }}
        >
          <Search className="size-3" style={{ color: "var(--color-muted)" }} />
          <input
            type="text"
            value={setsSearch}
            onChange={(e) => setSetsSearch(e.target.value)}
            placeholder="Buscar en FIRST/FOLLOW... (ej: arg_lista, sentencia)"
            className="flex-1 bg-transparent text-[0.7rem] outline-none"
            style={{ color: "var(--color-text)" }}
          />
          {setsSearch && (
            <button
              onClick={() => setSetsSearch("")}
              className="text-[0.6rem] px-1.5 py-0.5 rounded cursor-pointer"
              style={{ color: "var(--color-muted)", backgroundColor: "var(--color-surface)" }}
            >
              limpiar
            </button>
          )}
        </div>

        {/* FIRST / FOLLOW */}
        <SetSection title="FIRST (Primero)" data={primero} filter={setsSearch} />
        <SetSection title="FOLLOW (Siguiente)" data={siguiente} filter={setsSearch} />

        {/* M[A,a] table */}
        <section aria-label="Tabla M[A,a]">
          <div className="flex items-center gap-3 mb-2">
            <h3
              className="text-xs font-semibold uppercase tracking-wider"
              style={{ color: "var(--color-muted)" }}
            >
              Tabla M[A,a]
            </h3>
            <div
              className="flex items-center gap-1.5 rounded-md px-2 py-1 flex-1 max-w-[280px]"
              style={{ backgroundColor: "var(--color-surface-2)", border: "1px solid var(--color-border)" }}
            >
              <Search className="size-3" style={{ color: "var(--color-muted)" }} />
              <input
                type="text"
                value={tableSearch}
                onChange={(e) => setTableSearch(e.target.value)}
                placeholder="Buscar no-terminal o produccion..."
                className="flex-1 bg-transparent text-[0.7rem] outline-none"
                style={{ color: "var(--color-text)" }}
              />
            </div>
            {tableSearch && (
              <span className="text-[0.6rem]" style={{ color: "var(--color-muted)" }}>
                {filteredNTs.length}/{noTerminales.length} filas
              </span>
            )}
          </div>
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
                {filteredNTs.map((nt) => (
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
