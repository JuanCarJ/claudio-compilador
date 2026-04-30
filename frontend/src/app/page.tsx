"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { Toolbar, type AnalysisMethod } from "@/components/toolbar";
import { CodeEditor } from "@/components/code-editor";
import { ResultsPanel, type ResultTab } from "@/components/results-panel";
import {
  fetchProgramas,
  analizarLexico,
  analizarRecursivo,
  analizarLL1,
  traducirSwift,
  generarSugerenciasIA,
  type LexicoResponse,
  type RecursivoResponse,
  type LL1Response,
  type TraducirResponse,
  type SyntaxDiagnostic,
  type AISuggestion,
} from "@/lib/api";
import { GrammarPanel } from "@/components/grammar-panel";
import { ProgramGallery } from "@/components/program-gallery";

const DEFAULT_CODE = `// Escribe codigo en Claudio o selecciona un programa de ejemplo
var entero x = 10
var cadena nombre = "Mundo"

si x > 5 entonces
    imprimir("Hola")
sino
    imprimir("x es menor o igual a 5")
fin_si

para i desde 1 hasta x paso 1 hacer
    imprimir(i)
fin_para
`;

/* Map method to default active tab */
const METHOD_TAB: Record<AnalysisMethod, ResultTab> = {
  lexico: "tokens",
  recursivo: "arbol",
  ll1: "traza",
};

const METHOD_DESCRIPTIONS: Record<AnalysisMethod, string> = {
  lexico: "Tokeniza el codigo fuente en lexemas con tipo, fila y columna",
  recursivo: "Una funcion por cada no-terminal — construye el arbol de derivacion",
  ll1: "Tabla M[A,a] + pila explicita — traza paso a paso del analisis",
};

function attachAISuggestions(
  diagnostics: SyntaxDiagnostic[] = [],
  suggestions: AISuggestion[] = []
) {
  const byIndex = new Map(suggestions.map((item) => [item.indice, item]));
  return diagnostics.map((diag) => {
    const suggestion = byIndex.get(diag.indice);
    if (!suggestion) return diag;
    return {
      ...diag,
      sugerencia_ia: suggestion,
      estado_ia: suggestion.estado_ia,
    };
  });
}

function syntaxLines(diagnostics: SyntaxDiagnostic[] = []) {
  return diagnostics.map((d) => d.fila).filter((line) => Number.isFinite(line) && line > 0);
}

import { Suspense } from "react";

export default function Home() {
  return (
    <Suspense>
      <HomeContent />
    </Suspense>
  );
}

function HomeContent() {
  const searchParams = useSearchParams();
  const router = useRouter();

  /* Read URL params on mount */
  const urlMethod = searchParams.get("metodo") as AnalysisMethod | null;
  const urlPrograma = searchParams.get("programa");

  /* Core state */
  const [code, setCode] = useState(DEFAULT_CODE);
  const [method, setMethod] = useState<AnalysisMethod>(
    urlMethod && ["lexico", "recursivo", "ll1"].includes(urlMethod) ? urlMethod : "lexico"
  );
  const [activeTab, setActiveTab] = useState<ResultTab>(METHOD_TAB[method] ?? "tokens");
  const [isLoading, setIsLoading] = useState(false);

  /* Programs */
  const [programas, setProgramas] = useState<Record<string, string>>({});
  const [selectedProgram, setSelectedProgram] = useState(urlPrograma ?? "");

  /* Results */
  const [lexico, setLexico] = useState<LexicoResponse | null>(null);
  const [recursivo, setRecursivo] = useState<RecursivoResponse | null>(null);
  const [ll1, setLL1] = useState<LL1Response | null>(null);
  const [traduccion, setTraduccion] = useState<TraducirResponse | null>(null);
  const [syntaxErrors, setSyntaxErrors] = useState<string[]>([]);
  const [errorLines, setErrorLines] = useState<number[]>([]);
  const analysisRunId = useRef(0);

  /* Gallery modal */
  const [showGallery, setShowGallery] = useState(false);

  /* Resizable panel */
  const [leftWidth, setLeftWidth] = useState(40);
  const isDragging = useRef(false);
  const containerRef = useRef<HTMLDivElement>(null);

  /* Sync state to URL (for sharing) */
  const updateURL = useCallback(
    (m: AnalysisMethod, prog: string) => {
      const params = new URLSearchParams();
      params.set("metodo", m);
      if (prog) params.set("programa", prog);
      router.replace(`?${params.toString()}`, { scroll: false });
    },
    [router]
  );

  /* Fetch available programs on mount + auto-load from URL */
  useEffect(() => {
    fetchProgramas()
      .then((res) => {
        setProgramas(res.programas);
        /* If URL has a programa param, load it */
        if (urlPrograma && res.programas[urlPrograma]) {
          setCode(res.programas[urlPrograma]);
          setSelectedProgram(urlPrograma);
        }
      })
      .catch(() => {
        /* Backend may not be running */
      });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  /* When program selection changes, update code */
  const handleProgramChange = useCallback(
    (name: string) => {
      setSelectedProgram(name);
      updateURL(method, name);
      if (programas[name]) {
        setCode(programas[name]);
      }
    },
    [method, programas, updateURL]
  );

  /* When method changes, switch default tab + update URL */
  const handleMethodChange = useCallback((m: AnalysisMethod) => {
    setMethod(m);
    setActiveTab(METHOD_TAB[m]);
    updateURL(m, selectedProgram);
  }, [updateURL, selectedProgram]);

  /* Run analysis */
  const handleAnalyze = useCallback(async () => {
    if (!code.trim() || isLoading) return;
    const runId = analysisRunId.current + 1;
    analysisRunId.current = runId;
    setIsLoading(true);
    setSyntaxErrors([]);
    setErrorLines([]);
    setLexico(null);
    setRecursivo(null);
    setLL1(null);
    setTraduccion(null);
    setActiveTab(METHOD_TAB[method]);

    try {
      switch (method) {
        case "lexico": {
          const res = await analizarLexico(code);
          if (analysisRunId.current !== runId) return;
          setLexico(res);
          setActiveTab("tokens");
          /* Also attempt translation */
          traducirSwift(code)
            .then((swift) => {
              if (analysisRunId.current === runId) {
                setTraduccion(swift);
              }
            })
            .catch(() => {});
          /* Highlight error lines */
          if (res.errores?.length) {
            setErrorLines(res.errores.map((e) => e.fila));
          }
          if (res.errores?.length) {
            setActiveTab("errores");
          }
          break;
        }
        case "recursivo": {
          const res = await analizarRecursivo(code);
          if (analysisRunId.current !== runId) return;
          setRecursivo(res);
          if (res.lexico) setLexico(res.lexico);
          setSyntaxErrors([]);
          setActiveTab("arbol");
          traducirSwift(code)
            .then((swift) => {
              if (analysisRunId.current === runId) {
                setTraduccion(swift);
              }
            })
            .catch(() => {});
          const lines = [
            ...(res.lexico?.errores?.map((e) => e.fila) ?? []),
            ...syntaxLines(res.errores_sintacticos),
          ];
          if (lines.length) {
            setErrorLines(lines);
          }
          if (res.lexico?.errores?.length || res.errores_sintacticos?.length) {
            setActiveTab("errores");
          }
          if (res.errores_sintacticos?.length) {
            generarSugerenciasIA(code, res.errores_sintacticos)
              .then((ia) => {
                if (analysisRunId.current !== runId) return;
                setRecursivo((prev) =>
                  prev
                    ? {
                        ...prev,
                        errores_sintacticos: attachAISuggestions(prev.errores_sintacticos, ia.sugerencias),
                      }
                    : prev
                );
              })
              .catch(() => {
                if (analysisRunId.current !== runId) return;
                setRecursivo((prev) =>
                  prev
                    ? {
                        ...prev,
                        errores_sintacticos: prev.errores_sintacticos.map((diag) => ({
                          ...diag,
                          estado_ia: "error",
                        })),
                      }
                    : prev
                );
              });
          }
          break;
        }
        case "ll1": {
          const res = await analizarLL1(code);
          if (analysisRunId.current !== runId) return;
          setLL1(res);
          if (res.lexico) setLexico(res.lexico);
          setActiveTab("traza");
          traducirSwift(code)
            .then((swift) => {
              if (analysisRunId.current === runId) {
                setTraduccion(swift);
              }
            })
            .catch(() => {});
          const lines = [
            ...(res.lexico?.errores?.map((e) => e.fila) ?? []),
            ...syntaxLines(res.errores_sintacticos),
          ];
          if (lines.length) {
            setErrorLines(lines);
          }
          if (res.lexico?.errores?.length || res.errores_sintacticos?.length) {
            setActiveTab("errores");
          }
          if (res.errores_sintacticos?.length) {
            generarSugerenciasIA(code, res.errores_sintacticos)
              .then((ia) => {
                if (analysisRunId.current !== runId) return;
                setLL1((prev) =>
                  prev
                    ? {
                        ...prev,
                        errores_sintacticos: attachAISuggestions(prev.errores_sintacticos, ia.sugerencias),
                      }
                    : prev
                );
              })
              .catch(() => {
                if (analysisRunId.current !== runId) return;
                setLL1((prev) =>
                  prev
                    ? {
                        ...prev,
                        errores_sintacticos: prev.errores_sintacticos.map((diag) => ({
                          ...diag,
                          estado_ia: "error",
                        })),
                      }
                    : prev
                );
              });
          }
          break;
        }
      }
    } catch (err) {
      if (analysisRunId.current !== runId) return;
      setSyntaxErrors([
        err instanceof Error ? err.message : "Error de conexion con el servidor",
      ]);
      setActiveTab("errores");
    } finally {
      if (analysisRunId.current === runId) {
        setIsLoading(false);
      }
    }
  }, [code, method, isLoading]);

  /* Error click -> jump to line in editor */
  const handleClickError = useCallback((fila: number, columna: number) => {
    window.dispatchEvent(
      new CustomEvent("claudio:jump-to-line", {
        detail: { fila, columna },
      })
    );
  }, []);

  /* Resize handlers */
  const handleMouseDown = useCallback(() => {
    isDragging.current = true;
    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";
  }, []);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging.current || !containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const pct = ((e.clientX - rect.left) / rect.width) * 100;
      setLeftWidth(Math.max(20, Math.min(80, pct)));
    };

    const handleMouseUp = () => {
      isDragging.current = false;
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    };

    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);
    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };
  }, []);

  return (
    <div className="flex h-dvh flex-col" id="main-content">
      <Toolbar
        method={method}
        onMethodChange={handleMethodChange}
        programas={programas}
        selectedProgram={selectedProgram}
        onProgramChange={handleProgramChange}
        onAnalyze={handleAnalyze}
        isLoading={isLoading}
        onOpenGallery={() => setShowGallery(true)}
      />

      {/* Pipeline + context bar */}
      <div
        className="flex shrink-0 items-center gap-2 px-3 py-1 overflow-x-auto"
        style={{
          backgroundColor: "var(--color-bg)",
          borderBottom: "1px solid var(--color-border)",
        }}
      >
        {/* Compiler pipeline indicator */}
        {["Codigo", "Lexico", "Sintactico", "Semantico", "Swift"].map((fase, i) => {
          const faseActiva = method === "lexico" ? 1 : 2;
          const completada = i <= faseActiva;
          const actual = i === faseActiva;
          return (
            <span key={fase} className="flex items-center gap-1">
              {i > 0 && <span style={{ color: "var(--color-border)", fontSize: ".6rem" }}>→</span>}
              <span
                className="text-[0.6rem] font-medium px-1.5 py-0.5 rounded"
                style={{
                  backgroundColor: actual
                    ? "rgba(137,180,250,.15)"
                    : "transparent",
                  color: completada
                    ? actual ? "var(--color-accent)" : "var(--color-success)"
                    : "var(--color-muted)",
                  border: actual ? "1px solid rgba(137,180,250,.3)" : "1px solid transparent",
                }}
              >
                {completada && i < faseActiva ? "✓ " : ""}{fase}
              </span>
            </span>
          );
        })}

        <span style={{ color: "var(--color-border)" }} className="mx-1">|</span>

        {/* Method description */}
        <span className="text-[0.65rem] shrink-0" style={{ color: "var(--color-muted)" }}>
          {METHOD_DESCRIPTIONS[method]}
        </span>

        {/* Results summary badge */}
        {(lexico || recursivo || ll1) && (
          <>
            <span style={{ color: "var(--color-border)" }} className="mx-1">|</span>
            <span className="text-[0.6rem] font-mono shrink-0 flex items-center gap-2" style={{ color: "var(--color-muted)" }}>
              {lexico && <span>{lexico.total_tokens} tokens</span>}
              {lexico && lexico.total_errores > 0 && (
                <span style={{ color: "var(--color-error)" }}>{lexico.total_errores} err</span>
              )}
              {recursivo?.valido !== undefined && (
                <span style={{ color: recursivo.valido ? "var(--color-success)" : "var(--color-error)" }}>
                  {recursivo.valido ? "✓ valida" : "✗ invalida"}
                </span>
              )}
              {recursivo?.total_nodos ? <span>{recursivo.total_nodos} nodos</span> : null}
              {ll1?.valido !== undefined && (
                <span style={{ color: ll1.valido ? "var(--color-success)" : "var(--color-error)" }}>
                  {ll1.valido ? "✓ valida" : "✗ invalida"}
                </span>
              )}
              {ll1?.total_pasos ? <span>{ll1.total_pasos} pasos</span> : null}
            </span>
          </>
        )}
      </div>

      {/* Main split panel */}
      <div ref={containerRef} className="flex flex-1 flex-col overflow-hidden md:flex-row">
        {/* Editor panel */}
        <div
          className="h-[45dvh] shrink-0 overflow-hidden md:h-auto"
          style={{ width: `var(--editor-width, 100%)` }}
        >
          <style>{`
            @media (min-width: 768px) {
              [style*="--editor-width"] {
                --editor-width: ${leftWidth}% !important;
              }
            }
          `}</style>
          <CodeEditor
            value={code}
            onChange={setCode}
            onAnalyze={handleAnalyze}
            errorLines={errorLines}
          />
        </div>

        {/* Resize handle */}
        <div
          className="hidden h-full w-1 shrink-0 cursor-col-resize items-center justify-center md:flex"
          style={{ backgroundColor: "var(--color-border)" }}
          onMouseDown={handleMouseDown}
          role="separator"
          aria-orientation="vertical"
          aria-label="Redimensionar paneles"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === "ArrowLeft") {
              setLeftWidth((w) => Math.max(20, w - 2));
            } else if (e.key === "ArrowRight") {
              setLeftWidth((w) => Math.min(80, w + 2));
            }
          }}
        >
          <div
            className="h-8 w-0.5 rounded-full"
            style={{ backgroundColor: "var(--color-muted)" }}
            aria-hidden="true"
          />
        </div>

        {/* Results panel */}
        <div className="flex-1 overflow-hidden" style={{ backgroundColor: "var(--color-surface)" }}>
          <ResultsPanel
            activeTab={activeTab}
            onTabChange={setActiveTab}
            method={method}
            lexico={lexico}
            recursivo={recursivo}
            ll1={ll1}
            traduccion={traduccion}
            claudioCode={code}
            syntaxErrors={syntaxErrors}
            onClickError={handleClickError}
          />
        </div>
      </div>

      {/* Floating grammar panel */}
      <GrammarPanel
        activeProduction={
          ll1?.traza?.[0]?.accion?.includes("→")
            ? ll1.traza[0].accion
            : undefined
        }
      />

      {/* Program gallery modal */}
      {showGallery && (
        <ProgramGallery
          programas={programas}
          onSelect={handleProgramChange}
          onClose={() => setShowGallery(false)}
        />
      )}
    </div>
  );
}
