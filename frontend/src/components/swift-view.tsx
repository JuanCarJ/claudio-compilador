"use client";

import { useMemo, useState } from "react";
import { AlertTriangle, Bot, CheckCircle2, Clipboard, Download, FileCode2, GitCompareArrows } from "lucide-react";
import type { FinalDiagnostic, MapeoLinea, SwiftAIValidation } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";

interface SwiftViewProps {
  claudioCode: string;
  swiftCode: string;
  mapeo: MapeoLinea[];
  finalValido?: boolean;
  erroresFinales?: FinalDiagnostic[];
  validacionIA?: SwiftAIValidation | null;
  tablaSimbolosCount?: number;
}

const SWIFT_KEYWORDS = new Set([
  "import", "let", "var", "func", "class", "return", "if", "else", "for",
  "in", "stride", "from", "through", "by", "while", "break", "continue",
  "true", "false", "nil", "self", "print",
]);

const SWIFT_TYPES = new Set(["Int", "Double", "String", "Bool", "Void"]);

function colorForToken(token: string) {
  if (token.startsWith("//")) return "var(--token-comment)";
  if (token.startsWith("\"")) return "var(--token-string)";
  if (SWIFT_TYPES.has(token)) return "var(--token-type)";
  if (SWIFT_KEYWORDS.has(token)) return "var(--token-keyword)";
  if (/^\d+(\.\d+)?$/.test(token)) return "var(--token-number)";
  if (/^[=+\-*/%<>!&|]+$/.test(token)) return "var(--token-operator)";
  if (/^[{}()[\].,:]$/.test(token)) return "var(--token-delimiter)";
  return "var(--color-text)";
}

function renderSwiftLine(line: string, lineNumber: number) {
  const parts: { text: string; color: string }[] = [];
  const pattern = /(\/\/.*|"(?:\\.|[^"\\])*"|\b[A-Za-z_][A-Za-z0-9_]*\b|\d+(?:\.\d+)?|==|!=|<=|>=|&&|\|\||[-+*/%=<>{}()[\].,:])/g;
  let last = 0;
  for (const match of line.matchAll(pattern)) {
    const index = match.index ?? 0;
    if (index > last) {
      parts.push({ text: line.slice(last, index), color: "var(--color-text)" });
    }
    parts.push({ text: match[0], color: colorForToken(match[0]) });
    last = index + match[0].length;
  }
  if (last < line.length) {
    parts.push({ text: line.slice(last), color: "var(--color-text)" });
  }
  if (parts.length === 0) {
    return <span>&nbsp;</span>;
  }
  return parts.map((part, index) => (
    <span key={`${lineNumber}-${index}`} style={{ color: part.color }}>
      {part.text}
    </span>
  ));
}

function groupErrors(errores: FinalDiagnostic[] = []) {
  return errores.reduce<Record<string, number>>((acc, error) => {
    acc[error.fase] = (acc[error.fase] ?? 0) + 1;
    return acc;
  }, {});
}

function AIStatus({ validation }: { validation?: SwiftAIValidation | null }) {
  if (!validation) return null;
  const isOk = validation.estado_ia === "lista" && validation.valido === true;
  const isWarn = validation.estado_ia === "lista" && validation.valido === false;
  const Icon = isOk ? CheckCircle2 : isWarn ? AlertTriangle : Bot;
  const color = isOk ? "var(--color-success)" : isWarn ? "var(--color-error)" : "var(--token-keyword)";

  return (
    <section className="shrink-0 border-t px-3 py-2 text-xs" style={{ borderColor: "var(--color-border)", backgroundColor: "var(--color-surface)" }}>
      <div className="flex items-center gap-2 font-semibold" style={{ color }}>
        <Icon className="size-3.5" />
        Validacion IA Swift
        <span className="ml-auto font-mono text-[0.62rem]" style={{ color: "var(--color-muted)" }}>
          {validation.estado_ia}
        </span>
      </div>
      <p className="mt-1" style={{ color: "var(--color-text)" }}>{validation.resumen}</p>
      {(validation.problemas.length > 0 || validation.sugerencias.length > 0) && (
        <div className="mt-2 grid gap-2 lg:grid-cols-2">
          {validation.problemas.length > 0 && (
            <div>
              <p className="mb-1 font-semibold" style={{ color: "var(--color-error)" }}>Problemas</p>
              <ul className="space-y-1">
                {validation.problemas.map((item, index) => (
                  <li key={`p-${index}`} style={{ color: "var(--color-muted)" }}>{item}</li>
                ))}
              </ul>
            </div>
          )}
          {validation.sugerencias.length > 0 && (
            <div>
              <p className="mb-1 font-semibold" style={{ color: "var(--color-success)" }}>Sugerencias</p>
              <ul className="space-y-1">
                {validation.sugerencias.map((item, index) => (
                  <li key={`s-${index}`} style={{ color: "var(--color-muted)" }}>{item}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </section>
  );
}

export function SwiftView({
  claudioCode,
  swiftCode,
  mapeo,
  finalValido,
  erroresFinales = [],
  validacionIA,
  tablaSimbolosCount = 0,
}: SwiftViewProps) {
  const [hoveredLine, setHoveredLine] = useState<number | null>(null);
  const [copied, setCopied] = useState(false);
  const swiftLines = swiftCode.split("\n");
  const claudioLines = claudioCode.split("\n");
  const errorGroups = groupErrors(erroresFinales);
  const metrics = useMemo(() => {
    const nonEmpty = swiftLines.filter((line) => line.trim()).length;
    return {
      lineas: swiftCode ? swiftLines.length : 0,
      efectivas: nonEmpty,
      simbolos: tablaSimbolosCount,
      mapeos: mapeo.length,
    };
  }, [mapeo.length, swiftCode, swiftLines, tablaSimbolosCount]);

  const copySwift = async () => {
    await navigator.clipboard.writeText(swiftCode);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1300);
  };

  const downloadSwift = () => {
    const blob = new Blob([swiftCode], { type: "text/x-swift;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "claudio_generado.swift";
    link.click();
    URL.revokeObjectURL(url);
  };

  if (!swiftCode) {
    if (finalValido === false && erroresFinales.length > 0) {
      return (
        <div className="flex h-full flex-col">
          <div className="flex shrink-0 items-center gap-2 border-b px-3 py-2" style={{ borderColor: "var(--color-border)" }}>
            <AlertTriangle className="size-4" style={{ color: "var(--color-error)" }} />
            <span className="text-sm font-semibold" style={{ color: "var(--color-text)" }}>Swift bloqueado</span>
            <span className="text-xs" style={{ color: "var(--color-muted)" }}>corrige las fases anteriores para generar salida destino</span>
          </div>
          <ScrollArea className="min-h-0 flex-1">
            <div className="space-y-3 p-3">
              <div className="flex flex-wrap gap-2">
                {Object.entries(errorGroups).map(([fase, total]) => (
                  <span
                    key={fase}
                    className="rounded px-2 py-1 text-[0.68rem] font-mono"
                    style={{ backgroundColor: "rgba(243,139,168,.08)", border: "1px solid rgba(243,139,168,.2)", color: "var(--color-error)" }}
                  >
                    {fase}: {total}
                  </span>
                ))}
              </div>
              <div className="space-y-2">
                {erroresFinales.slice(0, 6).map((error, index) => (
                  <div
                    key={`${error.fase}-${error.fila}-${error.columna}-${index}`}
                    className="rounded-md px-3 py-2 text-xs"
                    style={{ backgroundColor: "var(--color-surface-2)", border: "1px solid var(--color-border)" }}
                  >
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="rounded px-1.5 py-px font-mono text-[0.6rem]" style={{ backgroundColor: "var(--color-error)", color: "var(--color-bg)" }}>
                        {error.fase}
                      </span>
                      <span className="font-mono text-[0.65rem]" style={{ color: "var(--color-muted)" }}>{error.fila}:{error.columna}</span>
                      {error.regla && <span className="font-mono text-[0.65rem]" style={{ color: "var(--token-keyword)" }}>{error.regla}</span>}
                      <code style={{ color: "var(--color-warning)" }}>{error.lexema}</code>
                    </div>
                    <p className="mt-1" style={{ color: "var(--color-text)" }}>{error.mensaje}</p>
                  </div>
                ))}
              </div>
            </div>
          </ScrollArea>
        </div>
      );
    }

    return (
      <div className="flex h-full items-center justify-center px-6 text-center" style={{ color: "var(--color-muted)" }}>
        <div>
          <FileCode2 className="mx-auto mb-3 size-7" />
          <p className="text-sm">Ejecuta el analisis para ver el codigo Swift generado.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      <header className="flex shrink-0 flex-wrap items-center gap-2 border-b px-3 py-2" style={{ borderColor: "var(--color-border)", backgroundColor: "var(--color-surface)" }}>
        <div className="flex items-center gap-2">
          <CheckCircle2 className="size-4" style={{ color: "var(--color-success)" }} />
          <span className="text-sm font-semibold" style={{ color: "var(--color-text)" }}>Swift generado</span>
        </div>
        <div className="flex flex-wrap items-center gap-1 text-[0.65rem] font-mono" style={{ color: "var(--color-muted)" }}>
          <span>{metrics.lineas} lineas</span>
          <span>·</span>
          <span>{metrics.efectivas} efectivas</span>
          <span>·</span>
          <span>{metrics.simbolos} simbolos</span>
          <span>·</span>
          <span>{metrics.mapeos} mapeos</span>
        </div>
        <div className="ml-auto flex items-center gap-1">
          <Button size="xs" variant="outline" onClick={copySwift} className="gap-1">
            <Clipboard className="size-3" />
            {copied ? "Copiado" : "Copiar"}
          </Button>
          <Button size="xs" variant="outline" onClick={downloadSwift} className="gap-1">
            <Download className="size-3" />
            Swift
          </Button>
        </div>
      </header>

      <div className="grid min-h-0 flex-1 grid-cols-1 lg:grid-cols-[minmax(0,1fr)_17rem]">
        <div className="grid min-h-0 grid-cols-1 md:grid-cols-2">
          <section className="flex min-h-0 flex-col border-r" style={{ borderColor: "var(--color-border)" }}>
            <div className="flex shrink-0 items-center gap-2 border-b px-3 py-1.5 text-[0.68rem] font-semibold uppercase" style={{ borderColor: "var(--color-border)", color: "var(--token-keyword)" }}>
              Claudio
            </div>
            <ScrollArea className="min-h-0 flex-1">
              <pre className="p-2 font-mono text-[0.72rem] leading-5" style={{ color: "var(--color-text)" }}>
                {claudioLines.map((line, i) => (
                  <div
                    key={`cl-${i}`}
                    className="flex min-h-5 transition-colors duration-150 ease-out"
                    style={{ backgroundColor: hoveredLine === i ? "rgba(137, 180, 250, 0.1)" : "transparent" }}
                    onMouseEnter={() => setHoveredLine(i)}
                    onMouseLeave={() => setHoveredLine(null)}
                  >
                    <span className="mr-3 inline-block w-7 shrink-0 text-right select-none" style={{ color: "var(--color-muted)" }} aria-hidden="true">{i + 1}</span>
                    <span className="whitespace-pre">{line || "\u00a0"}</span>
                  </div>
                ))}
              </pre>
            </ScrollArea>
          </section>

          <section className="flex min-h-0 flex-col">
            <div className="flex shrink-0 items-center gap-2 border-b px-3 py-1.5 text-[0.68rem] font-semibold uppercase" style={{ borderColor: "var(--color-border)", color: "var(--color-warning)" }}>
              Swift
            </div>
            <ScrollArea className="min-h-0 flex-1">
              <pre className="p-2 font-mono text-[0.72rem] leading-5" style={{ color: "var(--color-text)" }}>
                {swiftLines.map((line, i) => (
                  <div
                    key={`sw-${i}`}
                    className="flex min-h-5 transition-colors duration-150 ease-out"
                    style={{ backgroundColor: hoveredLine === i ? "rgba(137, 180, 250, 0.1)" : "transparent" }}
                    onMouseEnter={() => setHoveredLine(i)}
                    onMouseLeave={() => setHoveredLine(null)}
                  >
                    <span className="mr-3 inline-block w-7 shrink-0 text-right select-none" style={{ color: "var(--color-muted)" }} aria-hidden="true">{i + 1}</span>
                    <span className="whitespace-pre">{renderSwiftLine(line, i)}</span>
                  </div>
                ))}
              </pre>
            </ScrollArea>
          </section>
        </div>

        <aside className="hidden min-h-0 flex-col border-l lg:flex" style={{ borderColor: "var(--color-border)" }}>
          <div className="flex shrink-0 items-center gap-2 border-b px-3 py-1.5 text-[0.68rem] font-semibold uppercase" style={{ borderColor: "var(--color-border)", color: "var(--color-muted)" }}>
            <GitCompareArrows className="size-3.5" />
            Mapeo
          </div>
          <ScrollArea className="min-h-0 flex-1">
            <div className="space-y-1 p-2 text-[0.62rem]">
              {mapeo.map((linea, i) => (
                <div
                  key={`map-${i}`}
                  className="rounded px-2 py-1 transition-colors duration-150 ease-out"
                  style={{
                    backgroundColor: hoveredLine === i ? "rgba(137, 180, 250, 0.1)" : "transparent",
                    border: hoveredLine === i ? "1px solid rgba(137,180,250,.22)" : "1px solid transparent",
                  }}
                  onMouseEnter={() => setHoveredLine(i)}
                  onMouseLeave={() => setHoveredLine(null)}
                >
                  <div className="font-mono" style={{ color: "var(--token-keyword)" }}>{linea.claudio || "\u00a0"}</div>
                  <div className="font-mono" style={{ color: "var(--color-warning)" }}>{linea.swift || "\u00a0"}</div>
                </div>
              ))}
            </div>
          </ScrollArea>
        </aside>
      </div>

      <AIStatus validation={validacionIA} />
    </div>
  );
}
