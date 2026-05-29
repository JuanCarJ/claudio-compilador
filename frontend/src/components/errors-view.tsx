"use client";

import { useMemo, useState } from "react";
import type { LexicoError, SyntaxDiagnostic, SemanticDiagnostic } from "@/lib/api";
import { ScrollArea } from "@/components/ui/scroll-area";
import { AlertCircle, Bot, ChevronRight, Lightbulb, Loader2, MapPin, ShieldAlert, Terminal } from "lucide-react";

interface ErrorsViewProps {
  errores: LexicoError[];
  syntaxDiagnostics: SyntaxDiagnostic[];
  semanticDiagnostics?: SemanticDiagnostic[];
  runtimeErrors: string[];
  onClickError?: (fila: number, columna: number) => void;
}

type Filter = "todos" | "lexico" | "sintactico" | "semantico";

function AIBlock({ diag }: { diag: SyntaxDiagnostic }) {
  const suggestion = diag.sugerencia_ia;
  const estado = suggestion?.estado_ia ?? diag.estado_ia;

  if (estado === "pendiente" || estado === "generando") {
    return (
      <div className="mt-2 flex items-center gap-2 rounded-md px-2 py-2 text-xs" style={{ backgroundColor: "rgba(137,180,250,.06)", color: "var(--color-muted)" }}>
        <Loader2 className="size-3.5 animate-spin" />
        Generando sugerencia IA...
      </div>
    );
  }

  if (!suggestion || estado === "no_disponible" || estado === "error") {
    return (
      <div className="mt-2 rounded-md px-2 py-2 text-xs" style={{ backgroundColor: "rgba(108,112,134,.08)", color: "var(--color-muted)", border: "1px solid var(--color-border)" }}>
        {suggestion?.explicacion_usuario || "La sugerencia IA no esta disponible para este diagnostico."}
      </div>
    );
  }

  return (
    <div className="mt-2 space-y-1 rounded-md px-2 py-2 text-xs" style={{ backgroundColor: "rgba(203,166,247,.08)", border: "1px solid rgba(203,166,247,.18)" }}>
      <div className="flex items-center gap-1.5 font-semibold" style={{ color: "var(--token-keyword)" }}>
        <Bot className="size-3.5" />
        Sugerencia IA
        <span className="ml-auto font-mono text-[0.6rem]" style={{ color: "var(--color-muted)" }}>
          confianza {Math.round((suggestion.confianza ?? 0) * 100)}%
        </span>
      </div>
      <p style={{ color: "var(--color-text)" }}>{suggestion.explicacion_usuario}</p>
      {suggestion.correccion_sugerida && (
        <p style={{ color: "var(--color-text)" }}>
          <span style={{ color: "var(--color-muted)" }}>Correccion: </span>
          {suggestion.correccion_sugerida}
        </p>
      )}
      {suggestion.mini_ejemplo && (
        <pre className="overflow-x-auto rounded px-2 py-1 font-mono text-[0.65rem]" style={{ backgroundColor: "var(--color-surface)", color: "var(--token-string)" }}>
          {suggestion.mini_ejemplo}
        </pre>
      )}
    </div>
  );
}

function SemanticAIBlock({ diag }: { diag: SemanticDiagnostic }) {
  const suggestion = diag.sugerencia_ia;
  const estado = suggestion?.estado_ia ?? diag.estado_ia;

  if (estado === "pendiente" || estado === "generando") {
    return (
      <div className="mt-2 flex items-center gap-2 rounded-md px-2 py-2 text-xs" style={{ backgroundColor: "rgba(137,180,250,.06)", color: "var(--color-muted)" }}>
        <Loader2 className="size-3.5 animate-spin" />
        Generando sugerencia IA...
      </div>
    );
  }

  if (!suggestion || estado === "no_disponible" || estado === "error") {
    return (
      <div className="mt-2 rounded-md px-2 py-2 text-xs" style={{ backgroundColor: "rgba(108,112,134,.08)", color: "var(--color-muted)", border: "1px solid var(--color-border)" }}>
        {suggestion?.explicacion_usuario || "La sugerencia IA no esta disponible para este diagnostico."}
      </div>
    );
  }

  return (
    <div className="mt-2 space-y-1 rounded-md px-2 py-2 text-xs" style={{ backgroundColor: "rgba(203,166,247,.08)", border: "1px solid rgba(203,166,247,.18)" }}>
      <div className="flex items-center gap-1.5 font-semibold" style={{ color: "var(--token-keyword)" }}>
        <Bot className="size-3.5" />
        Sugerencia IA
        <span className="ml-auto font-mono text-[0.6rem]" style={{ color: "var(--color-muted)" }}>
          confianza {Math.round((suggestion.confianza ?? 0) * 100)}%
        </span>
      </div>
      <p style={{ color: "var(--color-text)" }}>{suggestion.explicacion_usuario}</p>
      {suggestion.correccion_sugerida && (
        <p style={{ color: "var(--color-text)" }}>
          <span style={{ color: "var(--color-muted)" }}>Correccion: </span>
          {suggestion.correccion_sugerida}
        </p>
      )}
      {suggestion.mini_ejemplo && (
        <pre className="overflow-x-auto rounded px-2 py-1 font-mono text-[0.65rem]" style={{ backgroundColor: "var(--color-surface)", color: "var(--token-string)" }}>
          {suggestion.mini_ejemplo}
        </pre>
      )}
    </div>
  );
}

export function ErrorsView({ errores, syntaxDiagnostics, semanticDiagnostics = [], runtimeErrors, onClickError }: ErrorsViewProps) {
  const [filter, setFilter] = useState<Filter>("todos");
  const totalErrors = errores.length + syntaxDiagnostics.length + semanticDiagnostics.length + runtimeErrors.length;
  const filterOptions = useMemo<{ value: Filter; label: string }[]>(
    () => [
      { value: "todos", label: "Todos" },
      ...(semanticDiagnostics.length > 0 ? [{ value: "semantico" as const, label: "Semantico" }] : []),
      ...(syntaxDiagnostics.length > 0 ? [{ value: "sintactico" as const, label: "Sintaxis" }] : []),
      ...(errores.length > 0 ? [{ value: "lexico" as const, label: "Lexico" }] : []),
    ],
    [errores.length, semanticDiagnostics.length, syntaxDiagnostics.length]
  );
  const effectiveFilter = filterOptions.some((option) => option.value === filter) ? filter : "todos";
  const showLex = effectiveFilter === "todos" || effectiveFilter === "lexico";
  const showSyn = effectiveFilter === "todos" || effectiveFilter === "sintactico";
  const showSem = effectiveFilter === "todos" || effectiveFilter === "semantico";

  if (totalErrors === 0) {
    return (
      <div className="flex h-full items-center justify-center gap-2" style={{ color: "var(--color-success)" }}>
        <svg
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="none"
          aria-hidden="true"
        >
          <circle cx="8" cy="8" r="7" stroke="currentColor" strokeWidth="1.5" />
          <path d="M5 8l2 2 4-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        <p className="text-sm font-medium">Sin errores detectados</p>
      </div>
    );
  }

  return (
    <ScrollArea className="h-full">
      <div className="p-3 space-y-2">
        <div className="flex flex-wrap items-center gap-2">
          <h3
            className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider"
            style={{ color: "var(--color-error)" }}
          >
            <AlertCircle className="size-3.5" aria-hidden="true" />
            {totalErrors} error{totalErrors !== 1 ? "es" : ""} encontrado{totalErrors !== 1 ? "s" : ""}
          </h3>
          <div className="ml-auto flex rounded-md p-0.5" style={{ backgroundColor: "var(--color-surface-2)", border: "1px solid var(--color-border)" }}>
            {filterOptions.map(({ value, label }) => (
              <button
                key={value}
                onClick={() => setFilter(value)}
                className="rounded px-2 py-1 text-[0.65rem] font-medium"
                style={{
                  backgroundColor: effectiveFilter === value ? "var(--color-surface)" : "transparent",
                  color: effectiveFilter === value ? "var(--color-text)" : "var(--color-muted)",
                }}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* Lexical errors */}
        {showLex && errores.map((err, i) => (
          <button
            key={`lex-${i}`}
            className="block w-full rounded-md px-3 py-2 text-left text-xs transition-colors duration-150 ease-out"
            style={{
              backgroundColor: "rgba(243, 139, 168, 0.06)",
              border: "1px solid rgba(243, 139, 168, 0.15)",
              color: "var(--color-text)",
            }}
            onClick={() => onClickError?.(err.fila, err.columna)}
            aria-label={`Error en fila ${err.fila}, columna ${err.columna}: ${err.mensaje}`}
          >
            <div className="flex flex-wrap items-center gap-2">
              <span
                className="shrink-0 rounded px-1.5 py-px text-[0.6rem] font-mono font-semibold tabular-nums"
                style={{ backgroundColor: "var(--color-error)", color: "var(--color-bg)" }}
              >
                {err.fila}:{err.columna}
              </span>
              <span className="text-xs">{err.mensaje}</span>
              {err.lexema && (
                <span className="rounded px-1 font-mono" style={{ backgroundColor: "rgba(243, 139, 168, 0.08)", color: "var(--color-error)" }}>
                  {err.lexema}
                </span>
              )}
            </div>

            <div className="mt-2 flex flex-wrap gap-1">
              {err.esperado && (
                <span className="rounded px-1.5 py-px text-[0.62rem]" style={{ backgroundColor: "var(--color-surface-2)", border: "1px solid var(--color-border)", color: "var(--tree-terminal)" }}>
                  Esperado: {err.esperado}
                </span>
              )}
              {err.simbolo_probable && (
                <span className="rounded px-1.5 py-px text-[0.62rem] font-mono" style={{ backgroundColor: "rgba(249,226,175,.08)", border: "1px solid rgba(249,226,175,.18)", color: "var(--color-warning)" }}>
                  Simbolo probable: {err.simbolo_probable}
                </span>
              )}
            </div>

            {err.sugerencia_deterministica && (
              <div className="mt-2 rounded-md px-2 py-2" style={{ backgroundColor: "rgba(166,227,161,.07)", border: "1px solid rgba(166,227,161,.16)" }}>
                <div className="mb-1 flex items-center gap-1.5 font-semibold" style={{ color: "var(--color-success)" }}>
                  <Lightbulb className="size-3.5" />
                  Sugerencia deterministica
                </div>
                <p style={{ color: "var(--color-text)" }}>{err.sugerencia_deterministica}</p>
              </div>
            )}
          </button>
        ))}

        {/* Structured syntax diagnostics */}
        {showSyn && syntaxDiagnostics.map((diag) => (
          <button
            key={`syn-${diag.indice}`}
            className="block w-full rounded-md px-3 py-2 text-left transition-colors duration-150 ease-out"
            style={{
              backgroundColor: "rgba(243, 139, 168, 0.06)",
              border: "1px solid rgba(243, 139, 168, 0.15)",
              color: "var(--color-text)",
            }}
            onClick={() => onClickError?.(diag.fila, diag.columna)}
          >
            <div className="flex flex-wrap items-center gap-2">
              <span className="rounded px-1.5 py-px text-[0.6rem] font-mono font-semibold" style={{ backgroundColor: "var(--color-warning)", color: "var(--color-bg)" }}>
                SYN-{diag.indice}
              </span>
              <span className="flex items-center gap-1 text-[0.7rem] font-mono" style={{ color: "var(--color-muted)" }}>
                <MapPin className="size-3" />
                {diag.fila}:{diag.columna}
              </span>
              <span className="text-xs">
                encontrado <code style={{ color: "var(--color-error)" }}>{diag.lexema_encontrado}</code>
              </span>
              <ChevronRight className="ml-auto size-3.5" style={{ color: "var(--color-muted)" }} />
            </div>

            <div className="mt-2 flex flex-wrap gap-1">
              {diag.esperados.map((esperado) => (
                <span key={`${diag.indice}-${esperado}`} className="rounded px-1.5 py-px text-[0.62rem] font-mono" style={{ backgroundColor: "var(--color-surface-2)", border: "1px solid var(--color-border)", color: "var(--tree-terminal)" }}>
                  {esperado}
                </span>
              ))}
            </div>

            <div className="mt-2 grid gap-2 lg:grid-cols-2">
              <div className="rounded-md px-2 py-2 text-xs" style={{ backgroundColor: "rgba(166,227,161,.07)", border: "1px solid rgba(166,227,161,.16)" }}>
                <div className="mb-1 flex items-center gap-1.5 font-semibold" style={{ color: "var(--color-success)" }}>
                  <Lightbulb className="size-3.5" />
                  Sugerencia deterministica
                </div>
                <p>{diag.sugerencia_deterministica}</p>
              </div>
              <div className="rounded-md px-2 py-2 text-xs" style={{ backgroundColor: "rgba(249,226,175,.07)", border: "1px solid rgba(249,226,175,.16)" }}>
                <div className="mb-1 flex items-center gap-1.5 font-semibold" style={{ color: "var(--color-warning)" }}>
                  <Terminal className="size-3.5" />
                  Regla gramatical
                </div>
                <p>
                  Contexto <code>{diag.contexto}</code>. {diag.recuperacion}
                </p>
              </div>
            </div>

            <AIBlock diag={diag} />
          </button>
        ))}

        {/* Semantic diagnostics */}
        {showSem && semanticDiagnostics.map((diag) => (
          <button
            key={`sem-${diag.indice}`}
            className="block w-full rounded-md px-3 py-2 text-left transition-colors duration-150 ease-out"
            style={{
              backgroundColor: "rgba(203,166,247,0.06)",
              border: "1px solid rgba(203,166,247,0.2)",
              color: "var(--color-text)",
            }}
            onClick={() => onClickError?.(diag.fila, diag.columna)}
          >
            <div className="flex flex-wrap items-center gap-2">
              <span className="rounded px-1.5 py-px text-[0.6rem] font-mono font-semibold" style={{ backgroundColor: "rgba(203,166,247,.25)", color: "var(--token-keyword)" }}>
                {diag.regla}
              </span>
              <span className="flex items-center gap-1 text-[0.7rem] font-mono" style={{ color: "var(--color-muted)" }}>
                <MapPin className="size-3" />
                {diag.fila}:{diag.columna}
              </span>
              <span className="text-xs">
                <code style={{ color: "var(--color-error)" }}>{diag.lexema}</code>
              </span>
              <span className="shrink-0">
                <ShieldAlert className="size-3.5" style={{ color: "rgba(203,166,247,.7)" }} />
              </span>
              <ChevronRight className="ml-auto size-3.5" style={{ color: "var(--color-muted)" }} />
            </div>

            <p className="mt-1.5 text-xs" style={{ color: "var(--color-text)" }}>
              {diag.mensaje}
            </p>

            <div className="mt-2 rounded-md px-2 py-2 text-xs" style={{ backgroundColor: "rgba(166,227,161,.07)", border: "1px solid rgba(166,227,161,.16)" }}>
              <div className="mb-1 flex items-center gap-1.5 font-semibold" style={{ color: "var(--color-success)" }}>
                <Lightbulb className="size-3.5" />
                Sugerencia deterministica
              </div>
              <p>{diag.sugerencia}</p>
            </div>

            <SemanticAIBlock diag={diag} />
          </button>
        ))}

        {runtimeErrors.map((msg, i) => (
          <div key={`runtime-${i}`} className="rounded-md px-2 py-1.5 text-xs" style={{ backgroundColor: "rgba(243,139,168,.06)", border: "1px solid rgba(243,139,168,.15)" }}>
            {msg}
          </div>
        ))}
      </div>
    </ScrollArea>
  );
}
