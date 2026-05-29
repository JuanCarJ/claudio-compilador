"use client";

import { ScrollArea } from "@/components/ui/scroll-area";
import type { SemanticSimboloEntry as SimboloEntry } from "@/lib/api";

interface SymbolTableViewProps {
  simbolos: SimboloEntry[];
  valido: boolean;
}

const TIPO_COLOR: Record<string, string> = {
  entero: "var(--token-number)",
  real: "var(--token-number)",
  cadena: "var(--token-string)",
  booleano: "var(--token-keyword)",
  funcion: "var(--color-accent)",
  clase: "var(--color-accent)",
};

export function SymbolTableView({ simbolos, valido }: SymbolTableViewProps) {
  if (simbolos.length === 0) {
    return (
      <div className="flex h-full items-center justify-center gap-2 text-sm" style={{ color: "var(--color-muted)" }}>
        {valido
          ? "No se declararon identificadores."
          : "Ejecuta el analisis semantico para ver la tabla de simbolos."}
      </div>
    );
  }

  return (
    <ScrollArea className="h-full">
      <div className="space-y-2 p-3">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-semibold uppercase" style={{ color: "var(--color-accent)" }}>
            Tabla de Simbolos
          </h3>
          <span className="text-[0.65rem] font-mono" style={{ color: "var(--color-muted)" }}>
            {simbolos.length} identificador{simbolos.length !== 1 ? "es" : ""}
          </span>
        </div>

        <div className="overflow-x-auto rounded-md" style={{ border: "1px solid var(--color-border)" }}>
          <table className="w-full text-xs" style={{ borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ backgroundColor: "var(--color-surface-2)", borderBottom: "1px solid var(--color-border)" }}>
                {["Nombre", "Tipo", "Declaracion", "Ambito", "Fila:Col"].map((h) => (
                  <th
                    key={h}
                    className="whitespace-nowrap px-3 py-2 text-left font-semibold"
                    style={{ color: "var(--color-muted)" }}
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {simbolos.map((s, i) => (
                <tr
                  key={`${s.nombre}-${s.fila}-${i}`}
                  style={{
                    backgroundColor: i % 2 === 0 ? "transparent" : "rgba(255,255,255,.02)",
                    borderBottom: "1px solid var(--color-border)",
                  }}
                >
                  <td className="px-3 py-1.5 font-mono font-semibold" style={{ color: "var(--color-text)" }}>
                    {s.nombre}
                  </td>
                  <td className="px-3 py-1.5 font-mono">
                    <span
                      className="rounded px-1.5 py-0.5 text-[0.65rem]"
                      style={{
                        color: TIPO_COLOR[s.tipo] ?? "var(--color-text)",
                        backgroundColor: "rgba(255,255,255,.05)",
                        border: "1px solid var(--color-border)",
                      }}
                    >
                      {s.tipo}
                    </span>
                  </td>
                  <td className="px-3 py-1.5">
                    <span
                      className="rounded px-1.5 py-0.5 text-[0.6rem] font-semibold"
                      style={{
                        backgroundColor: s.inmutable ? "rgba(203,166,247,.12)" : "rgba(166,227,161,.08)",
                        color: s.inmutable ? "var(--token-keyword)" : "var(--color-success)",
                        border: `1px solid ${s.inmutable ? "rgba(203,166,247,.25)" : "rgba(166,227,161,.2)"}`,
                      }}
                    >
                      {s.inmutable ? "sea (constante)" : "var (variable)"}
                    </span>
                  </td>
                  <td className="px-3 py-1.5 text-center font-mono" style={{ color: "var(--color-muted)" }}>
                    {s.ambito === 0 ? (
                      <span style={{ color: "var(--color-accent)" }}>global</span>
                    ) : (
                      <span>local ({s.ambito})</span>
                    )}
                  </td>
                  <td className="px-3 py-1.5 font-mono text-[0.65rem]" style={{ color: "var(--color-muted)" }}>
                    {s.fila}:{s.columna}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </ScrollArea>
  );
}
