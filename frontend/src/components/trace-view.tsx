"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import type { TrazaPaso } from "@/lib/api";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import {
  SkipBack,
  ChevronLeft,
  ChevronRight,
  SkipForward,
  Play,
  Pause,
  Gauge,
  CheckCircle2,
  XCircle,
} from "lucide-react";

interface TraceViewProps {
  traza: TrazaPaso[];
  valido: boolean;
  onHighlightCell?: (cell: { nt: string; terminal: string } | null) => void;
}

const SPEEDS = [500, 300, 150, 75];
const SPEED_LABELS = ["1x", "2x", "3x", "4x"];

export function TraceView({ traza, valido, onHighlightCell }: TraceViewProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [speedIdx, setSpeedIdx] = useState(0);
  const rowRefs = useRef<Map<number, HTMLTableRowElement>>(new Map());
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const total = traza.length;
  const current = traza[currentStep] ?? null;

  /* Auto-play */
  useEffect(() => {
    if (isPlaying && total > 0) {
      intervalRef.current = setInterval(() => {
        setCurrentStep((prev) => {
          if (prev >= total - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, SPEEDS[speedIdx]);
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [isPlaying, speedIdx, total]);

  /* Scroll into view */
  useEffect(() => {
    const row = rowRefs.current.get(currentStep);
    if (row) {
      row.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }, [currentStep]);

  /* Highlight LL1 cell — parse production actions */
  useEffect(() => {
    if (!current || !onHighlightCell) {
      onHighlightCell?.(null);
      return;
    }
    const accion = current.accion ?? "";
    /* Productions look like "sent_si → si expresion entonces..." */
    const prodMatch = accion.match(/^(\S+)\s*→/);
    if (prodMatch && current.entrada) {
      const nt = prodMatch[1];
      const firstToken = current.entrada.split(/\s+/)[0];
      if (nt && firstToken) {
        onHighlightCell({ nt, terminal: firstToken });
        return;
      }
    }
    /* Match actions look like "Emparejar 'xxx'" */
    if (accion.startsWith("Emparejar") || accion === "ACEPTAR") {
      onHighlightCell(null);
      return;
    }
    onHighlightCell(null);
  }, [current, onHighlightCell]);

  const goTo = useCallback(
    (step: number) => {
      setCurrentStep(Math.max(0, Math.min(step, total - 1)));
    },
    [total]
  );

  if (total === 0) {
    return (
      <div className="flex h-full items-center justify-center" style={{ color: "var(--color-muted)" }}>
        <p className="text-sm">Ejecuta el analisis LL(1) para ver la traza paso a paso.</p>
      </div>
    );
  }

  /* Parse the stack string for visual display */
  const pilaItems = current?.pila?.split(/\s+/).filter(Boolean) ?? [];
  const isError = current?.accion?.includes("ERROR") ?? false;
  const isRecovery = current?.accion?.includes("RECUPERACION") ?? false;
  const isAccept = current?.accion === "ACEPTAR";
  const isMatch = current?.accion?.startsWith("Emparejar") ?? false;

  return (
    <div className="flex h-full flex-col">
      {/* Result banner */}
      <div
        className="flex shrink-0 items-center gap-2 px-3 py-2"
        style={{
          backgroundColor: valido
            ? "rgba(166, 227, 161, 0.08)"
            : "rgba(243, 139, 168, 0.08)",
          borderBottom: "1px solid var(--color-border)",
        }}
      >
        {valido ? (
          <CheckCircle2 className="size-5" style={{ color: "var(--color-success)" }} />
        ) : (
          <XCircle className="size-5" style={{ color: "var(--color-error)" }} />
        )}
        <span
          className="text-sm font-bold"
          style={{ color: valido ? "var(--color-success)" : "var(--color-error)" }}
        >
          {valido ? "CADENA VALIDA" : "CADENA INVALIDA"}
        </span>
        <span className="text-xs" style={{ color: "var(--color-muted)" }}>
          — {total} pasos
        </span>
      </div>

      {/* Playback controls */}
      <div
        className="flex shrink-0 items-center gap-1.5 px-3 py-1.5"
        style={{ borderBottom: "1px solid var(--color-border)" }}
      >
        <Button size="icon-xs" variant="ghost" onClick={() => goTo(0)} aria-label="Ir al inicio" className="cursor-pointer">
          <SkipBack className="size-3" />
        </Button>
        <Button
          size="icon-xs"
          variant="ghost"
          onClick={() => goTo(currentStep - 1)}
          disabled={currentStep <= 0}
          aria-label="Paso anterior"
          className="cursor-pointer"
        >
          <ChevronLeft className="size-3" />
        </Button>
        <Button
          size="icon-xs"
          variant="ghost"
          onClick={() => setIsPlaying(!isPlaying)}
          aria-label={isPlaying ? "Pausar" : "Reproducir"}
          className="cursor-pointer"
          style={{
            backgroundColor: isPlaying ? "rgba(137, 180, 250, 0.15)" : undefined,
          }}
        >
          {isPlaying ? <Pause className="size-3" /> : <Play className="size-3" />}
        </Button>
        <Button
          size="icon-xs"
          variant="ghost"
          onClick={() => goTo(currentStep + 1)}
          disabled={currentStep >= total - 1}
          aria-label="Paso siguiente"
          className="cursor-pointer"
        >
          <ChevronRight className="size-3" />
        </Button>
        <Button size="icon-xs" variant="ghost" onClick={() => goTo(total - 1)} aria-label="Ir al final" className="cursor-pointer">
          <SkipForward className="size-3" />
        </Button>

        {/* Progress bar */}
        <div className="mx-2 flex-1">
          <div
            className="h-1 w-full overflow-hidden rounded-full"
            style={{ backgroundColor: "var(--color-surface-2)" }}
          >
            <div
              className="h-full rounded-full transition-all duration-150 ease-out"
              style={{
                width: `${((currentStep + 1) / total) * 100}%`,
                backgroundColor: "var(--color-accent)",
              }}
            />
          </div>
        </div>

        <span className="text-[0.65rem] tabular-nums font-mono" style={{ color: "var(--color-muted)" }}>
          {currentStep + 1}/{total}
        </span>

        {/* Speed toggle */}
        <Button
          size="icon-xs"
          variant="ghost"
          onClick={() => setSpeedIdx((prev) => (prev + 1) % SPEEDS.length)}
          aria-label={`Velocidad: ${SPEED_LABELS[speedIdx]}`}
          className="gap-0.5 cursor-pointer"
        >
          <Gauge className="size-3" />
          <span className="text-[0.6rem]">{SPEED_LABELS[speedIdx]}</span>
        </Button>
      </div>

      {/* Current action highlight */}
      {current && (
        <div
          className="shrink-0 px-3 py-1.5 text-xs font-mono"
          style={{
            backgroundColor: isError
              ? "rgba(243, 139, 168, 0.08)"
              : isRecovery
              ? "rgba(249, 226, 175, 0.08)"
              : isAccept
              ? "rgba(166, 227, 161, 0.08)"
              : isMatch
              ? "rgba(249, 226, 175, 0.08)"
              : "rgba(137, 180, 250, 0.06)",
            borderBottom: "1px solid var(--color-border)",
            color: isError
              ? "var(--color-error)"
              : isRecovery
              ? "var(--color-warning)"
              : isAccept
              ? "var(--color-success)"
              : isMatch
              ? "var(--color-warning)"
              : "var(--color-accent)",
          }}
        >
          <span style={{ color: "var(--color-muted)" }}>Paso {current.paso}: </span>
          {current.accion}
        </div>
      )}

      {/* Main area: table + stack */}
      <div className="flex flex-1 overflow-hidden">
        {/* Trace table */}
        <ScrollArea className="flex-1">
          <div className="p-2">
            <table className="w-full text-[0.65rem] font-mono" style={{ color: "var(--color-text)" }}>
              <thead>
                <tr>
                  {["#", "Pila", "Entrada", "Accion"].map((h) => (
                    <th
                      key={h}
                      className="sticky top-0 z-10 px-2 py-1 text-left font-semibold uppercase tracking-wider whitespace-nowrap"
                      style={{
                        backgroundColor: "var(--color-surface)",
                        borderBottom: "1px solid var(--color-border)",
                        color: "var(--color-muted)",
                      }}
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {traza.map((paso, idx) => {
                  const isActive = idx === currentStep;
                  const isPast = idx < currentStep;
                  const isErrRow = paso.accion?.includes("ERROR");
                  const isRecoveryRow = paso.accion?.includes("RECUPERACION");
                  const isAcceptRow = paso.accion === "ACEPTAR";
                  return (
                    <tr
                      key={paso.paso}
                      ref={(el) => {
                        if (el) rowRefs.current.set(idx, el);
                      }}
                      onClick={() => {
                        setCurrentStep(idx);
                        setIsPlaying(false);
                      }}
                      className="cursor-pointer transition-colors duration-100 ease-out"
                      style={{
                        backgroundColor: isActive
                          ? isErrRow
                            ? "rgba(243, 139, 168, 0.12)"
                            : isRecoveryRow
                            ? "rgba(249, 226, 175, 0.12)"
                            : isAcceptRow
                            ? "rgba(166, 227, 161, 0.12)"
                            : "rgba(137, 180, 250, 0.12)"
                          : "transparent",
                        opacity: isPast ? 0.5 : 1,
                      }}
                      aria-current={isActive ? "step" : undefined}
                    >
                      <td className="px-2 py-0.5 whitespace-nowrap" style={{ color: "var(--color-muted)" }}>
                        {paso.paso}
                      </td>
                      <td className="px-2 py-0.5 max-w-[200px] truncate">{paso.pila}</td>
                      <td className="px-2 py-0.5 max-w-[150px] truncate">{paso.entrada}</td>
                      <td
                        className="px-2 py-0.5 max-w-[280px] truncate"
                        style={{
                          color: isErrRow
                            ? "var(--color-error)"
                            : isRecoveryRow
                            ? "var(--color-warning)"
                            : isAcceptRow
                            ? "var(--color-success)"
                            : paso.accion?.startsWith("Emparejar")
                            ? "var(--color-warning)"
                            : "var(--color-accent)",
                        }}
                      >
                        {paso.accion}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </ScrollArea>

        {/* Stack visualization (sidebar) — animated tower */}
        <div
          className="hidden w-32 shrink-0 flex-col md:flex"
          style={{ borderLeft: "1px solid var(--color-border)" }}
        >
          <div
            className="px-2 py-1 text-center text-[0.6rem] font-semibold uppercase tracking-wider"
            style={{ color: "var(--color-muted)", borderBottom: "1px solid var(--color-border)" }}
          >
            Pila ({pilaItems.length})
          </div>
          <ScrollArea className="flex-1">
            <div className="flex flex-col-reverse gap-0.5 p-1.5">
              {pilaItems.map((item, i) => {
                const isTop = i === 0;
                const isTerminal = item === item.toLowerCase() && !item.includes("_") && item.length <= 3;
                return (
                  <div
                    key={`${currentStep}-${item}-${i}`}
                    className="flex items-center justify-center rounded px-1.5 py-1 text-[0.6rem] font-mono leading-tight transition-all duration-150 ease-out"
                    style={{
                      backgroundColor: isTop
                        ? "rgba(137, 180, 250, 0.2)"
                        : "var(--color-surface-2)",
                      border: isTop
                        ? "1.5px solid var(--color-accent)"
                        : "1px solid var(--color-border)",
                      color: isTop
                        ? "var(--color-accent)"
                        : isTerminal
                        ? "var(--color-success)"
                        : "var(--color-text)",
                      fontWeight: isTop ? 600 : 400,
                      transform: isTop ? "scale(1.05)" : "scale(1)",
                    }}
                  >
                    {item}
                  </div>
                );
              })}
            </div>
          </ScrollArea>
        </div>
      </div>
    </div>
  );
}
