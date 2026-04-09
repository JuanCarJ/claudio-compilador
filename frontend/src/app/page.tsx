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
  type LexicoResponse,
  type RecursivoResponse,
  type LL1Response,
  type TraducirResponse,
} from "@/lib/api";

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
    [programas]
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
    setIsLoading(true);
    setSyntaxErrors([]);
    setErrorLines([]);

    try {
      switch (method) {
        case "lexico": {
          const res = await analizarLexico(code);
          setLexico(res);
          setActiveTab("tokens");
          /* Also attempt translation */
          traducirSwift(code)
            .then(setTraduccion)
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
          setRecursivo(res);
          if (res.lexico) setLexico(res.lexico);
          setSyntaxErrors(res.errores ?? []);
          setActiveTab("arbol");
          traducirSwift(code)
            .then(setTraduccion)
            .catch(() => {});
          if (res.lexico?.errores?.length) {
            setErrorLines(res.lexico.errores.map((e) => e.fila));
          }
          if (res.errores?.length) {
            setActiveTab("errores");
          }
          break;
        }
        case "ll1": {
          const res = await analizarLL1(code);
          setLL1(res);
          if (res.lexico) setLexico(res.lexico);
          setActiveTab("traza");
          traducirSwift(code)
            .then(setTraduccion)
            .catch(() => {});
          if (res.lexico?.errores?.length) {
            setErrorLines(res.lexico.errores.map((e) => e.fila));
          }
          break;
        }
      }
    } catch (err) {
      setSyntaxErrors([
        err instanceof Error ? err.message : "Error de conexion con el servidor",
      ]);
      setActiveTab("errores");
    } finally {
      setIsLoading(false);
    }
  }, [code, method, isLoading]);

  /* Error click -> jump to line in editor */
  const handleClickError = useCallback((_fila: number, _columna: number) => {
    /* The CodeEditor exposes jumpToLine as a static function,
       but since we don't hold a ref to the EditorView here,
       we dispatch a custom event that the editor could listen to.
       For simplicity, we just scroll to the error tab feedback. */
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
      />

      {/* Method context bar */}
      <div
        className="flex shrink-0 items-center gap-3 px-3 py-1"
        style={{
          backgroundColor: "var(--color-bg)",
          borderBottom: "1px solid var(--color-border)",
        }}
      >
        <span className="text-[0.7rem] font-medium" style={{ color: "var(--color-accent)" }}>
          {method === "lexico" ? "Analisis Lexico" : method === "recursivo" ? "Desc. Recursivo" : "Predictivo LL(1)"}
        </span>
        <span className="text-[0.65rem]" style={{ color: "var(--color-muted)" }}>
          {METHOD_DESCRIPTIONS[method]}
        </span>
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
    </div>
  );
}
