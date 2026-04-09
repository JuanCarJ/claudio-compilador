"use client";

import { useState, useCallback } from "react";
import { TokensView } from "@/components/tokens-view";
import { TreeView } from "@/components/tree-view";
import { LL1Table } from "@/components/ll1-table";
import { TraceView } from "@/components/trace-view";
import { SwiftView } from "@/components/swift-view";
import { ErrorsView } from "@/components/errors-view";
import type {
  LexicoResponse,
  RecursivoResponse,
  LL1Response,
  TraducirResponse,
} from "@/lib/api";

export type ResultTab = "tokens" | "arbol" | "tabla" | "traza" | "swift" | "errores";
export type AnalysisMethod = "lexico" | "recursivo" | "ll1";

interface ResultsPanelProps {
  activeTab: ResultTab;
  onTabChange: (tab: ResultTab) => void;
  method: AnalysisMethod;
  lexico: LexicoResponse | null;
  recursivo: RecursivoResponse | null;
  ll1: LL1Response | null;
  traduccion: TraducirResponse | null;
  claudioCode: string;
  syntaxErrors: string[];
  onClickError?: (fila: number, columna: number) => void;
}

/* Tabs visibles segun el metodo seleccionado */
const TABS_POR_METODO: Record<AnalysisMethod, { value: ResultTab; label: string }[]> = {
  lexico: [
    { value: "tokens", label: "Tokens" },
    { value: "swift", label: "Swift" },
    { value: "errores", label: "Errores" },
  ],
  recursivo: [
    { value: "tokens", label: "Tokens" },
    { value: "arbol", label: "Arbol" },
    { value: "swift", label: "Swift" },
    { value: "errores", label: "Errores" },
  ],
  ll1: [
    { value: "tokens", label: "Tokens" },
    { value: "arbol", label: "Arbol" },
    { value: "tabla", label: "Tabla LL(1)" },
    { value: "traza", label: "Traza" },
    { value: "swift", label: "Swift" },
    { value: "errores", label: "Errores" },
  ],
};

export function ResultsPanel({
  activeTab,
  onTabChange,
  method,
  lexico,
  recursivo,
  ll1,
  traduccion,
  claudioCode,
  syntaxErrors,
  onClickError,
}: ResultsPanelProps) {
  const visibleTabs = TABS_POR_METODO[method];
  const [highlightedCell, setHighlightedCell] = useState<{ nt: string; terminal: string } | null>(null);

  const handleHighlightCell = useCallback(
    (cell: { nt: string; terminal: string } | null) => {
      setHighlightedCell(cell);
    },
    []
  );

  /* Count errors */
  const lexErrors = lexico?.errores?.length ?? 0;
  const synErrors = syntaxErrors.length;
  const recErrors = recursivo?.errores?.length ?? 0;
  const ll1SynErrors = ll1?.lexico?.errores?.length ?? 0;
  const totalErrors = lexErrors + synErrors + recErrors + ll1SynErrors;

  /* Merge all lex errors */
  const allLexErrors = [
    ...(lexico?.errores ?? []),
    ...(ll1?.lexico?.errores ?? []),
  ];

  const allSyntaxErrors = [
    ...syntaxErrors,
    ...(recursivo?.errores ?? []),
  ];

  /* Extra counts for badges */
  const tokenCount = lexico?.total_tokens ?? ll1?.lexico?.total_tokens ?? 0;
  const traceCount = ll1?.total_pasos ?? 0;

  return (
    <div className="flex h-full flex-col">
      {/* Custom tab bar */}
      <div
        className="flex shrink-0 items-center gap-1 overflow-x-auto px-2 py-1"
        style={{
          backgroundColor: "var(--color-surface)",
          borderBottom: "1px solid var(--color-border)",
        }}
        role="tablist"
      >
        {visibleTabs.map((tab) => {
          const isActive = activeTab === tab.value;
          return (
            <button
              key={tab.value}
              role="tab"
              aria-selected={isActive}
              onClick={() => onTabChange(tab.value)}
              className="relative inline-flex items-center gap-1 rounded px-2.5 py-1.5 text-xs font-medium whitespace-nowrap transition-colors duration-100 cursor-pointer"
              style={{
                color: isActive ? "var(--color-text)" : "var(--color-muted)",
                backgroundColor: isActive ? "var(--color-surface-2)" : "transparent",
              }}
            >
              {tab.label}
              {/* Token count badge */}
              {tab.value === "tokens" && tokenCount > 0 && (
                <span className="text-[0.6rem] tabular-nums" style={{ color: "var(--color-muted)" }}>
                  {tokenCount}
                </span>
              )}
              {/* Trace steps badge */}
              {tab.value === "traza" && traceCount > 0 && (
                <span className="text-[0.6rem] tabular-nums" style={{ color: "var(--color-muted)" }}>
                  {traceCount}
                </span>
              )}
              {/* Error badge */}
              {tab.value === "errores" && totalErrors > 0 && (
                <span
                  className="inline-flex h-4 min-w-4 items-center justify-center rounded-full px-1 text-[0.55rem] font-bold"
                  style={{ backgroundColor: "var(--color-error)", color: "var(--color-bg)" }}
                >
                  {totalErrors}
                </span>
              )}
              {/* Active underline */}
              {isActive && (
                <span
                  className="absolute bottom-0 left-0 right-0 h-0.5"
                  style={{ backgroundColor: "var(--color-accent)" }}
                />
              )}
            </button>
          );
        })}
      </div>

      {/* Tab content — render active tab only */}
      <div className="flex-1 overflow-hidden">
        {activeTab === "tokens" && (
          <TokensView
            tokens={lexico?.tokens ?? ll1?.lexico?.tokens ?? []}
            tablaSimbolos={lexico?.tabla_simbolos ?? ll1?.lexico?.tabla_simbolos ?? []}
          />
        )}
        {activeTab === "arbol" && (
          <TreeView
            arbol={recursivo?.arbol ?? ll1?.arbol ?? null}
            totalNodos={recursivo?.total_nodos}
            profundidad={recursivo?.profundidad}
          />
        )}
        {activeTab === "tabla" && (
          <LL1Table
            primero={ll1?.primero ?? {}}
            siguiente={ll1?.siguiente ?? {}}
            tablaLL1={ll1?.tabla_ll1 ?? {}}
            terminales={ll1?.terminales ?? []}
            noTerminales={ll1?.no_terminales ?? []}
            esLL1={ll1?.es_ll1 ?? false}
            conflictos={ll1?.conflictos ?? []}
            highlightedCell={highlightedCell}
          />
        )}
        {activeTab === "traza" && (
          <TraceView
            traza={ll1?.traza ?? []}
            valido={ll1?.valido ?? false}
            onHighlightCell={handleHighlightCell}
          />
        )}
        {activeTab === "swift" && (
          <SwiftView
            claudioCode={claudioCode}
            swiftCode={traduccion?.swift ?? ""}
            mapeo={traduccion?.mapeo ?? []}
          />
        )}
        {activeTab === "errores" && (
          <ErrorsView
            errores={allLexErrors}
            syntaxErrors={allSyntaxErrors}
            onClickError={onClickError}
          />
        )}
      </div>
    </div>
  );
}
