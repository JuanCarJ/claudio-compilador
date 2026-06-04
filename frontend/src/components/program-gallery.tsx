"use client";

import { useState } from "react";
import { X, Search } from "lucide-react";

interface ProgramGalleryProps {
  programas: Record<string, string>;
  onSelect: (name: string) => void;
  onClose: () => void;
}

/* Tags describing what constructs each program demonstrates */
const PROGRAM_TAGS: Record<string, { tags: string[]; complexity: "simple" | "medio" | "complejo" }> = {
  "1. Hola Mundo": { tags: ["imprimir"], complexity: "simple" },
  "2. Tipos y variables": { tags: ["var", "sea", "entero", "real", "cadena", "booleano"], complexity: "simple" },
  "3. Calculadora aritmetica": { tags: ["+", "-", "*", "/", "%", "**"], complexity: "simple" },
  "4. Comparaciones": { tags: ["==", "!=", "<", ">", "<=", ">="], complexity: "simple" },
  "5. Logica booleana": { tags: ["y", "o", "no"], complexity: "simple" },
  "6. Condicional simple": { tags: ["si", "entonces", "sino", "fin_si"], complexity: "simple" },
  "7. Condicional anidado": { tags: ["si", "sino", "anidado"], complexity: "medio" },
  "8. Ciclo para": { tags: ["para", "desde", "hasta", "paso"], complexity: "simple" },
  "9. Ciclo mientras": { tags: ["mientras", "hacer"], complexity: "simple" },
  "10. Romper y continuar": { tags: ["romper", "continuar", "mientras"], complexity: "medio" },
  "11. Funciones": { tags: ["funcion", "retornar", "parametros"], complexity: "medio" },
  "12. Factorial recursivo": { tags: ["funcion", "recursion", "si", "retornar"], complexity: "medio" },
  "Quiz 4. Caso semantico valido": { tags: ["quiz4", "valido", "funcion", "tabla"], complexity: "medio" },
  "Final. Valido con Swift": { tags: ["final", "valido", "swift", "sdt"], complexity: "medio" },
  "Final. Error semantico sin Swift": { tags: ["final", "error", "semantico", "sin swift"], complexity: "medio" },
  "Final. Error lexico/sintactico sin Swift": { tags: ["final", "error", "lexico", "sintactico"], complexity: "medio" },
};

const COMPLEXITY_COLORS = {
  simple: "var(--color-success)",
  medio: "var(--color-warning)",
  complejo: "var(--color-error)",
};

const VALID_QUICK_CASES = [
  { name: "Final. Valido con Swift", label: "Final", detail: "Genera Swift" },
  { name: "Quiz 4. Caso semantico valido", label: "Quiz 4", detail: "Semantico valido" },
  { name: "12. Factorial recursivo", label: "Recursion", detail: "Funcion valida" },
  { name: "11. Funciones", label: "Funciones", detail: "Retorno y parametros" },
];

function isInvalidProgram(name: string) {
  return name.startsWith("Final. Error");
}

function numberedProgramIndex(name: string) {
  const match = name.match(/^(\d+)\./);
  return match ? Number(match[1]) : null;
}

function programSortKey(name: string) {
  if (isInvalidProgram(name)) return 1000;

  const quickIndex = VALID_QUICK_CASES.findIndex((item) => item.name === name);
  if (quickIndex >= 0) return quickIndex;

  const numberedIndex = numberedProgramIndex(name);
  if (numberedIndex !== null) return 20 + numberedIndex;

  if (name.startsWith("Quiz 4.")) return 100;
  if (name.startsWith("Final.")) return 110;
  return 200;
}

export function ProgramGallery({ programas, onSelect, onClose }: ProgramGalleryProps) {
  const [search, setSearch] = useState("");

  const validQuickCases = VALID_QUICK_CASES.filter((item) => programas[item.name]);
  const entries = Object.entries(programas)
    .filter(([name]) => {
      if (!search.trim()) return true;
      const q = search.toLowerCase();
      const meta = PROGRAM_TAGS[name];
      return (
        name.toLowerCase().includes(q) ||
        meta?.tags.some((t) => t.includes(q))
      );
    })
    .sort(([a], [b]) => programSortKey(a) - programSortKey(b) || a.localeCompare(b));

  return (
    <div
      className="fixed inset-0 z-[200] flex items-center justify-center"
      style={{ backgroundColor: "rgba(0,0,0,.6)" }}
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div
        className="w-full max-w-2xl max-h-[88dvh] min-h-0 rounded-lg overflow-hidden flex flex-col"
        style={{
          backgroundColor: "var(--color-surface)",
          border: "1px solid var(--color-border)",
          boxShadow: "0 25px 50px rgba(0,0,0,.5)",
        }}
      >
        {/* Header */}
        <div
          className="flex items-center justify-between px-4 py-3 shrink-0"
          style={{ borderBottom: "1px solid var(--color-border)" }}
        >
          <div>
            <h2 className="text-sm font-bold" style={{ color: "var(--color-text)" }}>
              Programas de Ejemplo
            </h2>
            <p className="text-[0.7rem]" style={{ color: "var(--color-muted)" }}>
              Programas correctos primero; fallas y recuperacion al final
            </p>
          </div>
          <button
            onClick={onClose}
            className="rounded-md p-1 cursor-pointer transition-colors"
            style={{ color: "var(--color-muted)" }}
          >
            <X className="size-4" />
          </button>
        </div>

        {validQuickCases.length > 0 && (
          <div className="shrink-0 px-4 py-3" style={{ borderBottom: "1px solid var(--color-border)" }}>
            <div className="mb-2 flex items-center justify-between gap-2">
              <span className="text-xs font-semibold" style={{ color: "var(--color-text)" }}>
                Casos correctos destacados
              </span>
              <span className="text-[0.6rem] uppercase tracking-wide" style={{ color: "var(--color-muted)" }}>
                empezar por aqui
              </span>
            </div>
            <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
              {validQuickCases.map((item) => (
                <button
                  key={item.name}
                  onClick={() => { onSelect(item.name); onClose(); }}
                  className="rounded-md px-2 py-2 text-left transition-colors"
                  style={{
                    backgroundColor: "rgba(166,227,161,.08)",
                    border: "1px solid rgba(166,227,161,.3)",
                  }}
                >
                  <span className="block text-xs font-bold" style={{ color: "var(--color-text)" }}>
                    {item.label}
                  </span>
                  <span className="block truncate text-[0.6rem]" style={{ color: "var(--color-muted)" }}>
                    {item.detail}
                  </span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Search */}
        <div className="px-4 py-2 shrink-0" style={{ borderBottom: "1px solid var(--color-border)" }}>
          <div
            className="flex items-center gap-2 rounded-md px-2.5 py-1.5"
            style={{ backgroundColor: "var(--color-surface-2)", border: "1px solid var(--color-border)" }}
          >
            <Search className="size-3.5" style={{ color: "var(--color-muted)" }} />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Buscar por regla o constructo (sem-1, si, para, clase...)"
              className="flex-1 bg-transparent text-xs outline-none"
              style={{ color: "var(--color-text)" }}
              autoFocus
            />
          </div>
        </div>

        {/* Programs grid */}
        <div
          className="min-h-0 flex-1 overflow-y-auto overscroll-contain"
          style={{ scrollbarWidth: "thin", scrollbarColor: "var(--color-border) transparent" }}
        >
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 p-4">
            {entries.map(([name, code]) => {
              const meta = PROGRAM_TAGS[name] ?? { tags: [], complexity: "simple" as const };
              const lineCount = code.split("\n").length;
              const isQuiz3Demo = name.startsWith("Quiz 3.");
              const isQuiz4Demo = name.startsWith("Quiz 4.");
              const isInvalidDemo = isInvalidProgram(name);
              return (
                <button
                  key={name}
                  onClick={() => { onSelect(name); onClose(); }}
                  className="text-left rounded-lg p-3 transition-all duration-100 cursor-pointer group"
                  style={{
                    backgroundColor: isInvalidDemo ? "rgba(243,139,168,.07)" : "var(--color-surface-2)",
                    border: isInvalidDemo ? "1px solid rgba(243,139,168,.28)" : "1px solid var(--color-border)",
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = "rgba(137,180,250,.4)";
                    e.currentTarget.style.backgroundColor = "rgba(137,180,250,.06)";
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = isInvalidDemo ? "rgba(243,139,168,.28)" : "var(--color-border)";
                    e.currentTarget.style.backgroundColor = isInvalidDemo ? "rgba(243,139,168,.07)" : "var(--color-surface-2)";
                  }}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-semibold" style={{ color: "var(--color-text)" }}>
                      {name}
                    </span>
                    <span
                      className="text-[0.6rem] font-medium px-1.5 py-0.5 rounded"
                      style={{
                        backgroundColor: `${COMPLEXITY_COLORS[meta.complexity]}15`,
                        color: COMPLEXITY_COLORS[meta.complexity],
                      }}
                    >
                      {isQuiz4Demo ? "quiz4" : isQuiz3Demo ? "quiz3" : meta.complexity}
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-1 mb-1.5">
                    {meta.tags.slice(0, 5).map((tag) => (
                      <span
                        key={tag}
                        className="text-[0.55rem] font-mono px-1.5 py-0.5 rounded"
                        style={{
                          backgroundColor: "rgba(137,180,250,.08)",
                          color: "var(--color-accent)",
                        }}
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                  <span className="text-[0.6rem]" style={{ color: "var(--color-muted)" }}>
                    {lineCount} lineas
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
