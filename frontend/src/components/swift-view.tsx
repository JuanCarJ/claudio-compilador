"use client";

import { useMemo, useState } from "react";
import {
  AlertTriangle,
  ArrowRight,
  Bot,
  CheckCircle2,
  Clipboard,
  Download,
  FileCode2,
  GitCompareArrows,
  Layers3,
  Sparkles,
  XCircle,
} from "lucide-react";
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

function Metric({ label, value, tone = "neutral" }: { label: string; value: string | number; tone?: "neutral" | "swift" | "ok" | "warn" }) {
  const color =
    tone === "swift" ? "var(--color-warning)" :
    tone === "ok" ? "var(--color-success)" :
    tone === "warn" ? "var(--color-error)" :
    "var(--color-muted)";
  return (
    <div
      className="min-w-[5.25rem] rounded-md px-2 py-1.5"
      style={{ backgroundColor: "rgba(255,255,255,.035)", border: "1px solid var(--color-border)" }}
    >
      <div className="font-mono text-[0.78rem] font-semibold tabular-nums" style={{ color }}>{value}</div>
      <div className="text-[0.58rem] uppercase tracking-wide" style={{ color: "var(--color-muted)" }}>{label}</div>
    </div>
  );
}

function PhaseRibbon({ state }: { state: "waiting" | "blocked" | "generated" }) {
  const phases = [
    { label: "Codigo", active: true },
    { label: "Lexico", active: state !== "waiting" },
    { label: "Sintactico", active: state !== "waiting" },
    { label: "Semantico", active: state !== "waiting" && state !== "blocked" },
    { label: "Swift", active: state === "generated" },
  ];
  return (
    <div className="flex flex-wrap items-center gap-1.5">
      {phases.map((phase, index) => (
        <div key={phase.label} className="flex items-center gap-1.5">
          {index > 0 && <ArrowRight className="size-3" style={{ color: "var(--color-muted)" }} />}
          <span
            className="rounded px-2 py-1 text-[0.62rem] font-semibold uppercase tracking-wide"
            style={{
              backgroundColor: phase.active ? "rgba(166,227,161,.10)" : "rgba(108,112,134,.08)",
              border: phase.active ? "1px solid rgba(166,227,161,.22)" : "1px solid var(--color-border)",
              color: phase.active ? "var(--color-success)" : "var(--color-muted)",
            }}
          >
            {phase.label}
          </span>
        </div>
      ))}
    </div>
  );
}

function AIStatus({ validation }: { validation?: SwiftAIValidation | null }) {
  if (!validation) return null;
  const isOk = validation.estado_ia === "lista" && validation.valido === true;
  const isWarn = validation.estado_ia === "lista" && validation.valido === false;
  const Icon = isOk ? CheckCircle2 : isWarn ? AlertTriangle : Bot;
  const color = isOk ? "var(--color-success)" : isWarn ? "var(--color-error)" : "var(--token-keyword)";

  return (
    <section
      className="shrink-0 border-t px-4 py-3 text-sm"
      style={{
        borderColor: "rgba(166,227,161,.24)",
        background:
          "linear-gradient(135deg, rgba(166,227,161,.12), rgba(203,166,247,.13) 48%, rgba(137,180,250,.09))",
        boxShadow: "inset 0 1px 0 rgba(255,255,255,.055)",
      }}
    >
      <div className="flex flex-wrap items-center gap-2 font-semibold" style={{ color }}>
        <span
          className="flex size-8 items-center justify-center rounded-md"
          style={{ backgroundColor: "rgba(166,227,161,.12)", border: "1px solid rgba(166,227,161,.30)" }}
        >
          <Icon className="size-4.5" />
        </span>
        <span className="text-base">Validacion IA Swift</span>
        <span
          className="rounded-md px-2 py-1 text-[0.62rem] uppercase tracking-wide"
          style={{
            backgroundColor: "rgba(203,166,247,.13)",
            border: "1px solid rgba(203,166,247,.24)",
            color: "var(--token-keyword)",
          }}
        >
          Revision destino
        </span>
        <span className="ml-auto rounded-md px-2 py-1 font-mono text-[0.68rem]" style={{ backgroundColor: "rgba(255,255,255,.065)", border: "1px solid rgba(255,255,255,.08)", color: "var(--color-text)" }}>
          {validation.estado_ia}
        </span>
      </div>
      <p
        className="mt-2 rounded-md px-3 py-2 leading-relaxed"
        style={{
          backgroundColor: "rgba(12,14,24,.36)",
          border: "1px solid rgba(166,227,161,.13)",
          color: "var(--color-text)",
        }}
      >
        {validation.resumen}
      </p>
      {(validation.problemas.length > 0 || validation.sugerencias.length > 0) && (
        <div className="mt-2 grid gap-2 lg:grid-cols-2">
          {validation.problemas.length > 0 && (
            <div className="rounded-md px-2 py-2" style={{ backgroundColor: "rgba(243,139,168,.06)", border: "1px solid rgba(243,139,168,.16)" }}>
              <p className="mb-1 font-semibold" style={{ color: "var(--color-error)" }}>Problemas</p>
              <ul className="space-y-1">
                {validation.problemas.map((item, index) => (
                  <li key={`p-${index}`} style={{ color: "var(--color-muted)" }}>{item}</li>
                ))}
              </ul>
            </div>
          )}
          {validation.sugerencias.length > 0 && (
            <div className="rounded-md px-2 py-2" style={{ backgroundColor: "rgba(166,227,161,.06)", border: "1px solid rgba(166,227,161,.16)" }}>
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

function EmptySwiftState() {
  return (
    <div className="flex h-full items-center justify-center px-4 py-6">
      <div
        className="w-full max-w-3xl overflow-hidden rounded-lg"
        style={{ backgroundColor: "var(--color-surface)", border: "1px solid var(--color-border)" }}
      >
        <div
          className="px-5 py-4"
          style={{ background: "linear-gradient(135deg, rgba(249,226,175,.12), rgba(137,180,250,.08) 55%, rgba(166,227,161,.06))", borderBottom: "1px solid var(--color-border)" }}
        >
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-md" style={{ backgroundColor: "rgba(249,226,175,.14)", color: "var(--color-warning)", border: "1px solid rgba(249,226,175,.28)" }}>
              <FileCode2 className="size-5" />
            </div>
            <div>
              <h3 className="text-base font-semibold" style={{ color: "var(--color-text)" }}>Lenguaje destino Swift</h3>
              <p className="text-xs" style={{ color: "var(--color-muted)" }}>La salida aparece cuando el programa supera la cadena completa de compilacion.</p>
            </div>
          </div>
          <div className="mt-4">
            <PhaseRibbon state="waiting" />
          </div>
        </div>
        <div className="grid gap-3 p-4 md:grid-cols-[1fr_.85fr]">
          <div className="rounded-md p-3" style={{ backgroundColor: "var(--color-surface-2)", border: "1px solid var(--color-border)" }}>
            <div className="mb-2 flex items-center gap-2 text-xs font-semibold" style={{ color: "var(--color-warning)" }}>
              <Sparkles className="size-3.5" />
              Etapa SDT
            </div>
            <pre className="overflow-hidden rounded px-3 py-2 font-mono text-[0.72rem] leading-5" style={{ backgroundColor: "var(--color-bg)", color: "var(--color-muted)" }}>
{`func resultado(...) {
    // Swift generado por Claudio
}`}
            </pre>
          </div>
          <div className="space-y-2 text-xs">
            <div className="rounded-md px-3 py-2" style={{ backgroundColor: "rgba(137,180,250,.07)", border: "1px solid rgba(137,180,250,.18)" }}>
              <p className="font-semibold" style={{ color: "var(--color-accent)" }}>Visible en todos los modos</p>
              <p className="mt-1" style={{ color: "var(--color-muted)" }}>Lexico, recursivo, LL(1) y semantico pueden abrir esta pestaña y ver el estado final.</p>
            </div>
            <div className="rounded-md px-3 py-2" style={{ backgroundColor: "rgba(166,227,161,.06)", border: "1px solid rgba(166,227,161,.16)" }}>
              <p className="font-semibold" style={{ color: "var(--color-success)" }}>Sin errores: Swift</p>
              <p className="mt-1" style={{ color: "var(--color-muted)" }}>Cuando la compilacion es valida, se muestra el contraste entre Claudio y Swift.</p>
            </div>
            <div className="rounded-md px-3 py-2" style={{ backgroundColor: "rgba(243,139,168,.06)", border: "1px solid rgba(243,139,168,.16)" }}>
              <p className="font-semibold" style={{ color: "var(--color-error)" }}>Con errores: bloqueado</p>
              <p className="mt-1" style={{ color: "var(--color-muted)" }}>Si alguna fase falla, la salida destino no se muestra.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function BlockedSwiftState({ erroresFinales }: { erroresFinales: FinalDiagnostic[] }) {
  const errorGroups = groupErrors(erroresFinales);
  return (
    <div className="flex h-full flex-col">
      <div
        className="shrink-0 border-b px-4 py-3"
        style={{ borderColor: "var(--color-border)", background: "linear-gradient(135deg, rgba(243,139,168,.14), rgba(203,166,247,.08))" }}
      >
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex size-9 items-center justify-center rounded-md" style={{ backgroundColor: "rgba(243,139,168,.14)", color: "var(--color-error)", border: "1px solid rgba(243,139,168,.28)" }}>
            <XCircle className="size-5" />
          </div>
          <div>
            <h3 className="text-base font-semibold" style={{ color: "var(--color-text)" }}>Swift bloqueado</h3>
            <p className="text-xs" style={{ color: "var(--color-muted)" }}>La salida destino se detiene hasta que las fases previas queden validas.</p>
          </div>
          <div className="ml-auto">
            <PhaseRibbon state="blocked" />
          </div>
        </div>
      </div>
      <ScrollArea className="min-h-0 flex-1">
        <div className="space-y-3 p-4">
          <div className="flex flex-wrap gap-2">
            {Object.entries(errorGroups).map(([fase, total]) => (
              <span
                key={fase}
                className="rounded-md px-2.5 py-1.5 text-[0.68rem] font-mono font-semibold"
                style={{ backgroundColor: "rgba(243,139,168,.08)", border: "1px solid rgba(243,139,168,.22)", color: "var(--color-error)" }}
              >
                {fase}: {total}
              </span>
            ))}
          </div>
          <div className="grid gap-2">
            {erroresFinales.slice(0, 8).map((error, index) => (
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
  const [showTrace, setShowTrace] = useState(false);
  const swiftLines = swiftCode.split("\n");
  const claudioLines = claudioCode.split("\n");
  const metrics = useMemo(() => {
    const nonEmpty = swiftLines.filter((line) => line.trim()).length;
    return {
      lineas: swiftCode ? swiftLines.length : 0,
      efectivas: nonEmpty,
      simbolos: tablaSimbolosCount,
      reglas: mapeo.length,
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
      return <BlockedSwiftState erroresFinales={erroresFinales} />;
    }
    return <EmptySwiftState />;
  }

  return (
    <div className="flex h-full flex-col">
      <header
        className="shrink-0 border-b px-3 py-3"
        style={{ borderColor: "var(--color-border)", background: "linear-gradient(135deg, rgba(249,226,175,.13), rgba(166,227,161,.065) 52%, rgba(137,180,250,.07))" }}
      >
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex size-10 items-center justify-center rounded-md" style={{ backgroundColor: "rgba(249,226,175,.16)", color: "var(--color-warning)", border: "1px solid rgba(249,226,175,.3)" }}>
            <Sparkles className="size-5" />
          </div>
          <div className="min-w-[12rem]">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="size-4" style={{ color: "var(--color-success)" }} />
              <h3 className="text-base font-semibold" style={{ color: "var(--color-text)" }}>Swift generado</h3>
            </div>
            <p className="text-xs" style={{ color: "var(--color-muted)" }}>Lenguaje destino listo despues de validar Claudio.</p>
          </div>
          <div className="hidden lg:block">
            <PhaseRibbon state="generated" />
          </div>
          <div className="ml-auto flex items-center gap-1">
            {mapeo.length > 0 && (
              <Button size="xs" variant="ghost" onClick={() => setShowTrace((value) => !value)} className="gap-1">
                <GitCompareArrows className="size-3" />
                {showTrace ? "Ocultar SDT" : "Detalle SDT"}
              </Button>
            )}
            <Button size="xs" variant="outline" onClick={copySwift} className="gap-1">
              <Clipboard className="size-3" />
              {copied ? "Copiado" : "Copiar"}
            </Button>
            <Button size="xs" variant="outline" onClick={downloadSwift} className="gap-1">
              <Download className="size-3" />
              Swift
            </Button>
          </div>
        </div>
        <div className="mt-3 grid grid-cols-2 gap-2 md:flex">
          <Metric label="lineas" value={metrics.lineas} tone="swift" />
          <Metric label="efectivas" value={metrics.efectivas} tone="ok" />
          <Metric label="simbolos" value={metrics.simbolos} />
          <Metric label="reglas" value={metrics.reglas} tone="swift" />
        </div>
      </header>

      <div className="grid min-h-0 flex-1 grid-cols-1 lg:grid-cols-2">
        <section className="flex min-h-0 flex-col border-r" style={{ borderColor: "var(--color-border)" }}>
          <div
            className="flex shrink-0 items-center gap-2 border-b px-3 py-2 text-[0.74rem] font-bold uppercase tracking-wide"
            style={{
              borderColor: "rgba(137,180,250,.24)",
              background: "linear-gradient(90deg, rgba(137,180,250,.13), rgba(137,180,250,.035))",
              color: "var(--token-keyword)",
              boxShadow: "inset 0 -1px 0 rgba(137,180,250,.10)",
            }}
          >
            <Layers3 className="size-4" />
            Claudio origen
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

        <section className="flex min-h-0 flex-col" style={{ backgroundColor: "rgba(249,226,175,.025)" }}>
          <div
            className="flex shrink-0 items-center gap-2 border-b px-3 py-2 text-[0.74rem] font-bold uppercase tracking-wide"
            style={{
              borderColor: "rgba(249,226,175,.27)",
              background: "linear-gradient(90deg, rgba(249,226,175,.14), rgba(166,227,161,.045))",
              color: "var(--color-warning)",
              boxShadow: "inset 0 -1px 0 rgba(249,226,175,.10)",
            }}
          >
            <FileCode2 className="size-4" />
            Swift destino
            <span className="ml-auto rounded-md px-2 py-1 text-[0.6rem] font-mono" style={{ backgroundColor: "rgba(249,226,175,.14)", border: "1px solid rgba(249,226,175,.30)", color: "var(--color-warning)" }}>
              generado
            </span>
          </div>
          <ScrollArea className="min-h-0 flex-1">
            <pre className="p-2 font-mono text-[0.74rem] leading-5" style={{ color: "var(--color-text)" }}>
              {swiftLines.map((line, i) => (
                <div
                  key={`sw-${i}`}
                  className="flex min-h-5 transition-colors duration-150 ease-out"
                  style={{ backgroundColor: hoveredLine === i ? "rgba(249, 226, 175, 0.11)" : "transparent" }}
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

      {showTrace && (
        <section className="max-h-48 shrink-0 border-t" style={{ borderColor: "var(--color-border)", backgroundColor: "var(--color-surface)" }}>
          <div className="flex shrink-0 items-center gap-2 border-b px-3 py-2 text-[0.72rem] font-bold uppercase tracking-wide" style={{ borderColor: "rgba(203,166,247,.22)", background: "linear-gradient(90deg, rgba(203,166,247,.11), rgba(255,255,255,.02))", color: "var(--token-keyword)" }}>
            <GitCompareArrows className="size-3.5" />
            Detalle SDT aplicado
          </div>
          <ScrollArea className="h-36">
            <div className="grid gap-1 p-2 text-[0.62rem] md:grid-cols-2 xl:grid-cols-3">
              {mapeo.map((linea, i) => (
                <div
                  key={`map-${i}`}
                  className="rounded-md px-2 py-1.5 transition-colors duration-150 ease-out"
                  style={{
                    backgroundColor: hoveredLine === i ? "rgba(249, 226, 175, 0.1)" : "rgba(255,255,255,.02)",
                    border: hoveredLine === i ? "1px solid rgba(249,226,175,.24)" : "1px solid var(--color-border)",
                  }}
                  onMouseEnter={() => setHoveredLine(i)}
                  onMouseLeave={() => setHoveredLine(null)}
                >
                  <div className="mb-1 flex items-center gap-1 font-mono" style={{ color: "var(--token-keyword)" }}>
                    <span className="text-[0.55rem]" style={{ color: "var(--color-muted)" }}>{i + 1}</span>
                    {linea.claudio || "\u00a0"}
                  </div>
                  <div className="font-mono" style={{ color: "var(--color-warning)" }}>{linea.swift || "\u00a0"}</div>
                </div>
              ))}
            </div>
          </ScrollArea>
        </section>
      )}

      <AIStatus validation={validacionIA} />
    </div>
  );
}
