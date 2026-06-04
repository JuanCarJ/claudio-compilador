"use client";

import { useState, useCallback } from "react";
import { TokensView } from "@/components/tokens-view";
import { TreeView } from "@/components/tree-view";
import { LL1Table } from "@/components/ll1-table";
import { TraceView } from "@/components/trace-view";
import { SwiftView } from "@/components/swift-view";
import { ErrorsView } from "@/components/errors-view";
import { SymbolTableView } from "@/components/symbol-table-view";
import type {
  LexicoResponse,
  RecursivoResponse,
  LL1Response,
  TraducirResponse,
  CompilarResponse,
  SyntaxDiagnostic,
  SemanticoResponse,
  SemanticDiagnostic,
} from "@/lib/api";

export type ResultTab = "tokens" | "arbol" | "tabla" | "traza" | "swift" | "errores" | "simbolos";
export type AnalysisMethod = "lexico" | "recursivo" | "ll1" | "semantico";

interface ResultsPanelProps {
  activeTab: ResultTab;
  onTabChange: (tab: ResultTab) => void;
  method: AnalysisMethod;
  lexico: LexicoResponse | null;
  recursivo: RecursivoResponse | null;
  ll1: LL1Response | null;
  semantico: SemanticoResponse | null;
  traduccion: TraducirResponse | null;
  compilacionFinal: CompilarResponse | null;
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
  semantico: [
    { value: "tokens", label: "Tokens" },
    { value: "simbolos", label: "Tabla Simbolos" },
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
  semantico,
  traduccion,
  compilacionFinal,
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

  const activeLexico =
    method === "ll1" ? ll1?.lexico ?? lexico :
    method === "semantico" ? semantico?.lexico ?? lexico :
    method === "recursivo" || method === "lexico" ? recursivo?.lexico ?? lexico :
    lexico;

  const syntaxDiagnostics: SyntaxDiagnostic[] =
    method === "ll1"
      ? ll1?.errores_sintacticos ?? []
      : method === "recursivo" || method === "lexico" || method === "semantico"
      ? recursivo?.errores_sintacticos ?? []
      : [];

  const semanticDiagnostics: SemanticDiagnostic[] =
    method === "semantico" ? semantico?.errores_semanticos ?? [] : [];

  const lexErrors = activeLexico?.errores?.length ?? 0;
  const runtimeErrors = syntaxErrors.length;
  const totalErrors = lexErrors + syntaxDiagnostics.length + semanticDiagnostics.length + runtimeErrors;

  /* Extra counts for badges */
  const tokenCount = activeLexico?.total_tokens ?? 0;
  const traceCount = ll1?.total_pasos ?? 0;
  const simbolCount = semantico?.tabla_simbolos?.length ?? 0;

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
              {tab.value === "simbolos" && simbolCount > 0 && (
                <span className="text-[0.6rem] tabular-nums" style={{ color: "var(--color-muted)" }}>
                  {simbolCount}
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
            tokens={activeLexico?.tokens ?? []}
            tablaSimbolos={activeLexico?.tabla_simbolos ?? []}
          />
        )}
        {activeTab === "arbol" && (
          <TreeView
            arbol={
              recursivo?.arbol ??
              recursivo?.arbol_parcial ??
              ll1?.arbol ??
              ll1?.arbol_parcial ??
              semantico?.arbol_parcial ??
              null
            }
            totalNodos={recursivo?.total_nodos ?? ll1?.total_nodos}
            profundidad={recursivo?.profundidad ?? ll1?.profundidad}
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
            key={`${ll1?.total_pasos ?? 0}-${ll1?.valido ?? "empty"}-${ll1?.traza?.[Math.max(0, (ll1?.traza?.length ?? 1) - 1)]?.accion ?? ""}`}
            traza={ll1?.traza ?? []}
            valido={ll1?.valido ?? false}
            onHighlightCell={handleHighlightCell}
          />
        )}
        {activeTab === "simbolos" && (
          <SymbolTableView
            simbolos={semantico?.tabla_simbolos ?? []}
            valido={semantico?.valido ?? false}
          />
        )}
        {activeTab === "swift" && (
          <SwiftView
            claudioCode={claudioCode}
            swiftCode={traduccion?.swift ?? ""}
            mapeo={traduccion?.mapeo ?? []}
            finalValido={compilacionFinal?.valido}
            erroresFinales={compilacionFinal?.errores ?? []}
            validacionIA={compilacionFinal?.validacion_ia ?? null}
            tablaSimbolosCount={compilacionFinal?.tabla_simbolos?.length ?? semantico?.tabla_simbolos?.length ?? 0}
          />
        )}
        {activeTab === "errores" && (
          <ErrorsView
            errores={activeLexico?.errores ?? []}
            syntaxDiagnostics={syntaxDiagnostics}
            semanticDiagnostics={semanticDiagnostics}
            runtimeErrors={syntaxErrors}
            onClickError={onClickError}
          />
        )}
      </div>
    </div>
  );
}
