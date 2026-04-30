"use client";

import { useState } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
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
  "8. Ciclo para (for)": { tags: ["para", "desde", "hasta", "paso"], complexity: "simple" },
  "9. Ciclo mientras (while)": { tags: ["mientras", "hacer"], complexity: "simple" },
  "10. Romper y continuar": { tags: ["romper", "continuar", "mientras"], complexity: "medio" },
  "11. Funciones": { tags: ["funcion", "retornar", "parametros"], complexity: "medio" },
  "12. Factorial recursivo": { tags: ["funcion", "recursion", "si", "retornar"], complexity: "medio" },
  "13. Clases y objetos": { tags: ["clase", "metodo", "atributo", "nuevo", "este"], complexity: "complejo" },
  "14. Herencia": { tags: ["clase", "hereda", "metodo", "nuevo"], complexity: "complejo" },
  "15. Programa completo": { tags: ["todo", "clase", "funcion", "si", "para", "mientras"], complexity: "complejo" },
  "Quiz 3. Error: falta entonces": { tags: ["quiz3", "error", "si", "entonces"], complexity: "medio" },
  "Quiz 3. Error: parentesis sin cerrar": { tags: ["quiz3", "error", "imprimir", ")"], complexity: "medio" },
  "Quiz 3. Error: multiples fallos": { tags: ["quiz3", "error", "recuperacion", "ia"], complexity: "complejo" },
};

const COMPLEXITY_COLORS = {
  simple: "var(--color-success)",
  medio: "var(--color-warning)",
  complejo: "var(--color-error)",
};

export function ProgramGallery({ programas, onSelect, onClose }: ProgramGalleryProps) {
  const [search, setSearch] = useState("");

  const entries = Object.entries(programas).filter(([name]) => {
    if (!search.trim()) return true;
    const q = search.toLowerCase();
    const meta = PROGRAM_TAGS[name];
    return (
      name.toLowerCase().includes(q) ||
      meta?.tags.some((t) => t.includes(q))
    );
  });

  return (
    <div
      className="fixed inset-0 z-[200] flex items-center justify-center"
      style={{ backgroundColor: "rgba(0,0,0,.6)" }}
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div
        className="w-full max-w-2xl max-h-[80vh] rounded-lg overflow-hidden flex flex-col"
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
              15 programas validos y casos Quiz 3 para recuperacion de errores
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
              placeholder="Buscar por nombre o constructo (si, para, clase...)"
              className="flex-1 bg-transparent text-xs outline-none"
              style={{ color: "var(--color-text)" }}
              autoFocus
            />
          </div>
        </div>

        {/* Programs grid */}
        <ScrollArea className="flex-1">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 p-4">
            {entries.map(([name, code]) => {
              const meta = PROGRAM_TAGS[name] ?? { tags: [], complexity: "simple" as const };
              const lineCount = code.split("\n").length;
              const isInvalidDemo = name.startsWith("Quiz 3.");
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
                      {isInvalidDemo ? "quiz3" : meta.complexity}
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
        </ScrollArea>
      </div>
    </div>
  );
}
