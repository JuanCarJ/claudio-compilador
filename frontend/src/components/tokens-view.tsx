"use client";

import type { Token, SimboloEntry } from "@/lib/api";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";

/* Badge abbreviation + color map by token category */
const CATEGORY_CONFIG: Record<string, { label: string; bg: string; fg: string }> = {
  "PALABRA_RESERVADA": { label: "KW", bg: "var(--token-keyword)", fg: "var(--color-bg)" },
  "PALABRA RESERVADA": { label: "KW", bg: "var(--token-keyword)", fg: "var(--color-bg)" },
  "KEYWORD": { label: "KW", bg: "var(--token-keyword)", fg: "var(--color-bg)" },
  "IDENTIFICADOR": { label: "ID", bg: "var(--token-identifier)", fg: "var(--color-bg)" },
  "IDENTIFIER": { label: "ID", bg: "var(--token-identifier)", fg: "var(--color-bg)" },
  "OPERADOR": { label: "OP", bg: "var(--token-operator)", fg: "var(--color-bg)" },
  "OPERATOR": { label: "OP", bg: "var(--token-operator)", fg: "var(--color-bg)" },
  "NUMERO": { label: "LIT", bg: "var(--token-number)", fg: "var(--color-bg)" },
  "LITERAL": { label: "LIT", bg: "var(--token-number)", fg: "var(--color-bg)" },
  "NUMBER": { label: "LIT", bg: "var(--token-number)", fg: "var(--color-bg)" },
  "ENTERO": { label: "LIT", bg: "var(--token-number)", fg: "var(--color-bg)" },
  "REAL": { label: "LIT", bg: "var(--token-number)", fg: "var(--color-bg)" },
  "CADENA": { label: "STR", bg: "var(--token-string)", fg: "var(--color-bg)" },
  "STRING": { label: "STR", bg: "var(--token-string)", fg: "var(--color-bg)" },
  "DELIMITADOR": { label: "DLM", bg: "var(--token-delimiter)", fg: "var(--color-bg)" },
  "DELIMITER": { label: "DLM", bg: "var(--token-delimiter)", fg: "var(--color-bg)" },
  "PUNTUACION": { label: "DLM", bg: "var(--token-delimiter)", fg: "var(--color-bg)" },
  "COMENTARIO": { label: "CMT", bg: "var(--token-comment)", fg: "var(--color-text)" },
  "COMMENT": { label: "CMT", bg: "var(--token-comment)", fg: "var(--color-text)" },
  "ERROR": { label: "ERR", bg: "var(--color-error)", fg: "var(--color-bg)" },
  "TIPO": { label: "TYP", bg: "var(--token-type)", fg: "var(--color-bg)" },
  "BOOLEANO": { label: "LIT", bg: "var(--token-number)", fg: "var(--color-bg)" },
  "ASIGNACION": { label: "OP", bg: "var(--token-operator)", fg: "var(--color-bg)" },
};

function getConfig(categoria: string) {
  const upper = categoria.toUpperCase();
  return CATEGORY_CONFIG[upper] ?? { label: upper.slice(0, 3), bg: "var(--color-muted)", fg: "var(--color-text)" };
}

interface TokensViewProps {
  tokens: Token[];
  tablaSimbolos: SimboloEntry[];
}

export function TokensView({ tokens, tablaSimbolos }: TokensViewProps) {
  if (tokens.length === 0) {
    return (
      <div className="flex h-full items-center justify-center" style={{ color: "var(--color-muted)" }}>
        <p className="text-sm">Ejecuta el analisis lexico para ver los tokens.</p>
      </div>
    );
  }

  return (
    <ScrollArea className="h-full">
      <div className="p-3">
        {/* Token chips */}
        <section aria-label="Tokens encontrados">
          <h3
            className="mb-2 text-xs font-semibold uppercase tracking-wider"
            style={{ color: "var(--color-muted)" }}
          >
            Tokens ({tokens.length})
          </h3>
          <div className="flex flex-wrap gap-1.5">
            {tokens.map((tok, i) => {
              const cfg = getConfig(tok.categoria || tok.tipo);
              return (
                <span
                  key={`${tok.lexema}-${tok.fila}-${tok.columna}-${i}`}
                  className="inline-flex items-center gap-1 rounded-md px-1.5 py-0.5 text-xs font-mono transition-opacity duration-150 ease-out hover:opacity-80"
                  style={{ backgroundColor: cfg.bg, color: cfg.fg }}
                  title={`${tok.tipo} — Fila ${tok.fila}, Col ${tok.columna}`}
                >
                  <span
                    className="rounded px-1 py-px text-[0.6rem] font-semibold uppercase opacity-70"
                    aria-label={`Categoria: ${cfg.label}`}
                  >
                    {cfg.label}
                  </span>
                  <span>{tok.lexema}</span>
                </span>
              );
            })}
          </div>
        </section>

        {/* Symbol table */}
        {tablaSimbolos.length > 0 && (
          <>
            <Separator className="my-4" style={{ backgroundColor: "var(--color-border)" }} />
            <section aria-label="Tabla de simbolos">
              <h3
                className="mb-2 text-xs font-semibold uppercase tracking-wider"
                style={{ color: "var(--color-muted)" }}
              >
                Tabla de Simbolos ({tablaSimbolos.length})
              </h3>
              <div className="overflow-x-auto rounded-md" style={{ border: "1px solid var(--color-border)" }}>
                <table className="w-full text-xs" style={{ color: "var(--color-text)" }}>
                  <thead>
                    <tr style={{ backgroundColor: "var(--color-surface)" }}>
                      {tablaSimbolos[0] &&
                        Object.keys(tablaSimbolos[0]).map((key) => (
                          <th
                            key={key}
                            className="px-2 py-1.5 text-left font-semibold uppercase tracking-wider whitespace-nowrap"
                            style={{ color: "var(--color-muted)", borderBottom: "1px solid var(--color-border)" }}
                          >
                            {key}
                          </th>
                        ))}
                    </tr>
                  </thead>
                  <tbody>
                    {tablaSimbolos.map((row, idx) => (
                      <tr
                        key={idx}
                        className="transition-colors duration-150 ease-out hover:opacity-80"
                        style={{
                          backgroundColor: idx % 2 === 0 ? "var(--color-surface-2)" : "var(--color-surface)",
                        }}
                      >
                        {Object.values(row).map((val, ci) => (
                          <td
                            key={ci}
                            className="px-2 py-1 whitespace-nowrap font-mono"
                            style={{ borderBottom: "1px solid var(--color-border)" }}
                          >
                            {String(val ?? "")}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          </>
        )}
      </div>
    </ScrollArea>
  );
}
