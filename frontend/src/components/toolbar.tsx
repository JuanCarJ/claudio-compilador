"use client";

import { useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Play, Loader2, FileCode, Braces, Table2, LayoutGrid, ShieldCheck } from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

export type AnalysisMethod = "lexico" | "recursivo" | "ll1" | "semantico";

interface ToolbarProps {
  method: AnalysisMethod;
  onMethodChange: (m: AnalysisMethod) => void;
  programas: Record<string, string>;
  selectedProgram: string;
  onProgramChange: (name: string) => void;
  onAnalyze: () => void;
  isLoading: boolean;
  onOpenGallery?: () => void;
}

const METHODS: { value: AnalysisMethod; label: string; shortLabel: string; icon: typeof FileCode; tooltip: string }[] = [
  { value: "lexico", label: "Lexico", shortLabel: "LEX", icon: FileCode, tooltip: "Divide el codigo en tokens (lexemas) con su tipo, fila y columna. Primera fase de cualquier compilador." },
  { value: "recursivo", label: "Desc. Recursivo", shortLabel: "RD", icon: Braces, tooltip: "Una funcion por cada no-terminal de la gramatica. Construye el arbol de derivacion mediante llamadas recursivas." },
  { value: "ll1", label: "Predictivo LL(1)", shortLabel: "LL1", icon: Table2, tooltip: "Usa una tabla M[A,a] y una pila explicita para analizar la entrada paso a paso. Muestra conjuntos FIRST/FOLLOW." },
  { value: "semantico", label: "Semantico", shortLabel: "SEM", icon: ShieldCheck, tooltip: "Aplica reglas semanticas sobre el AST: tipos, ambitos, constantes, condiciones y ciclos. Incluye tabla de simbolos." },
];

export function Toolbar({
  method,
  onMethodChange,
  programas,
  selectedProgram,
  onAnalyze,
  isLoading,
  onOpenGallery,
}: ToolbarProps) {
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        e.preventDefault();
        onAnalyze();
      }
    },
    [onAnalyze]
  );

  const programKeys = Object.keys(programas);

  return (
    <header
      role="banner"
      className="flex h-12 shrink-0 items-center gap-2 px-3"
      style={{ backgroundColor: "var(--color-surface)", borderBottom: "1px solid var(--color-border)" }}
      onKeyDown={handleKeyDown}
    >
      {/* Logo */}
      <div className="flex items-center gap-2 select-none">
        <div
          className="flex h-7 w-7 items-center justify-center rounded-md text-xs font-bold"
          style={{ backgroundColor: "var(--color-accent)", color: "var(--color-bg)" }}
          aria-hidden="true"
        >
          C
        </div>
        <span
          className="hidden text-sm font-semibold tracking-tight sm:inline"
          style={{ color: "var(--color-text)" }}
        >
          Claudio
        </span>
      </div>

      <Separator orientation="vertical" className="!h-5" style={{ backgroundColor: "var(--color-border)" }} />

      {/* Method selector — segmented control style */}
      <TooltipProvider delay={200}>
        <div
          className="flex items-center gap-0.5 rounded-md p-0.5"
          style={{ backgroundColor: "var(--color-bg)" }}
          role="radiogroup"
          aria-label="Metodo de analisis"
        >
          {METHODS.map((m) => {
            const isActive = method === m.value;
            const Icon = m.icon;
            return (
              <Tooltip key={m.value}>
                <TooltipTrigger
                  role="radio"
                  aria-checked={isActive}
                  onClick={() => onMethodChange(m.value)}
                  className="flex items-center gap-1.5 rounded px-2.5 py-1 text-xs font-medium transition-all duration-100 cursor-pointer"
                  style={{
                    backgroundColor: isActive ? "var(--color-accent)" : "transparent",
                    color: isActive ? "var(--color-bg)" : "var(--color-muted)",
                  }}
                >
                  <Icon className="size-3.5" />
                  <span className="hidden lg:inline">{m.label}</span>
                  <span className="lg:hidden">{m.shortLabel}</span>
                </TooltipTrigger>
                <TooltipContent
                  side="bottom"
                  className="max-w-[260px] text-xs"
                  style={{
                    backgroundColor: "var(--color-surface-2)",
                    color: "var(--color-text)",
                    border: "1px solid var(--color-border)",
                  }}
                >
                  <p className="font-semibold" style={{ color: "var(--color-accent)" }}>{m.label}</p>
                  <p style={{ color: "var(--color-muted)" }}>{m.tooltip}</p>
                </TooltipContent>
              </Tooltip>
            );
          })}
        </div>
      </TooltipProvider>

      <Separator orientation="vertical" className="!h-5" style={{ backgroundColor: "var(--color-border)" }} />

      {/* Program gallery button */}
      {programKeys.length > 0 && onOpenGallery && (
        <button
          onClick={onOpenGallery}
          className="flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium cursor-pointer transition-colors"
          style={{
            color: "var(--color-text)",
            backgroundColor: "var(--color-surface-2)",
            border: "1px solid var(--color-border)",
          }}
        >
          <LayoutGrid className="size-3.5" />
          <span>{selectedProgram || "Programas de ejemplo"}</span>
        </button>
      )}

      <div className="flex-1" />

      {/* Analyze button */}
      <Button
        size="sm"
        onClick={onAnalyze}
        disabled={isLoading}
        className="gap-1.5 cursor-pointer"
        style={{
          backgroundColor: "var(--color-accent)",
          color: "var(--color-bg)",
        }}
        aria-label="Ejecutar analisis"
      >
        {isLoading ? (
          <Loader2 className="size-3.5 animate-spin" />
        ) : (
          <Play className="size-3.5" />
        )}
        <span className="hidden sm:inline">Analizar</span>
      </Button>

      {/* Keyboard shortcut hint */}
      <kbd
        className="hidden text-[0.65rem] md:inline-block"
        style={{ color: "var(--color-muted)" }}
        aria-hidden="true"
      >
        Ctrl+Enter
      </kbd>
    </header>
  );
}
