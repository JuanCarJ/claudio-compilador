"use client";

import type { LexicoError } from "@/lib/api";
import { ScrollArea } from "@/components/ui/scroll-area";
import { AlertCircle } from "lucide-react";

interface ErrorsViewProps {
  errores: LexicoError[];
  syntaxErrors: string[];
  onClickError?: (fila: number, columna: number) => void;
}

export function ErrorsView({ errores, syntaxErrors, onClickError }: ErrorsViewProps) {
  const totalErrors = errores.length + syntaxErrors.length;

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
      <div className="p-3 space-y-1">
        <h3
          className="mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider"
          style={{ color: "var(--color-error)" }}
        >
          <AlertCircle className="size-3.5" aria-hidden="true" />
          {totalErrors} error{totalErrors !== 1 ? "es" : ""} encontrado{totalErrors !== 1 ? "s" : ""}
        </h3>

        {/* Lexical errors */}
        {errores.map((err, i) => (
          <button
            key={`lex-${i}`}
            className="flex w-full items-start gap-2 rounded-md px-2 py-1.5 text-left text-xs transition-colors duration-150 ease-out"
            style={{
              backgroundColor: "rgba(243, 139, 168, 0.06)",
              border: "1px solid rgba(243, 139, 168, 0.15)",
              color: "var(--color-text)",
            }}
            onClick={() => onClickError?.(err.fila, err.columna)}
            aria-label={`Error en fila ${err.fila}, columna ${err.columna}: ${err.mensaje}`}
          >
            <span
              className="shrink-0 rounded px-1 py-px text-[0.6rem] font-mono font-semibold tabular-nums"
              style={{ backgroundColor: "var(--color-error)", color: "var(--color-bg)" }}
            >
              {err.fila}:{err.columna}
            </span>
            <span className="flex-1">
              {err.mensaje}
              {err.lexema && (
                <span className="ml-1 font-mono" style={{ color: "var(--color-error)" }}>
                  &quot;{err.lexema}&quot;
                </span>
              )}
            </span>
          </button>
        ))}

        {/* Syntax errors (string-only) */}
        {syntaxErrors.map((msg, i) => (
          <div
            key={`syn-${i}`}
            className="flex items-start gap-2 rounded-md px-2 py-1.5 text-xs"
            style={{
              backgroundColor: "rgba(243, 139, 168, 0.06)",
              border: "1px solid rgba(243, 139, 168, 0.15)",
              color: "var(--color-text)",
            }}
          >
            <span
              className="shrink-0 rounded px-1 py-px text-[0.6rem] font-mono font-semibold"
              style={{ backgroundColor: "var(--color-warning)", color: "var(--color-bg)" }}
            >
              SYN
            </span>
            <span className="flex-1">{msg}</span>
          </div>
        ))}
      </div>
    </ScrollArea>
  );
}
