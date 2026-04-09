"use client";

import { useState } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ChevronDown, ChevronRight, BookOpen } from "lucide-react";

interface GrammarPanelProps {
  activeProduction?: string;
}

interface Section {
  title: string;
  rules: string[];
}

const GRAMMAR_SECTIONS: Section[] = [
  {
    title: "Programa y declaraciones",
    rules: [
      "programa → declaracion programa | ε",
      "declaracion → def_funcion | def_clase | sentencia | importacion",
      "importacion → importar ID",
    ],
  },
  {
    title: "Variables",
    rules: [
      "decl_variable → var tipo ID = expresion",
      "decl_variable → sea tipo ID = expresion",
    ],
  },
  {
    title: "Funciones",
    rules: [
      "def_funcion → funcion tipo_ret ID ( parametros ) hacer bloque fin_funcion",
      "tipo_ret → tipo_basico | ε",
      "parametros → param_lista | ε",
      "param_lista → tipo ID param_resto",
      "param_resto → , tipo ID param_resto | ε",
    ],
  },
  {
    title: "Clases",
    rules: [
      "def_clase → clase ID herencia_opt hacer cuerpo_clase fin_clase",
      "herencia_opt → hereda ID | ε",
      "cuerpo_clase → miembro_clase cuerpo_clase | ε",
      "miembro_clase → def_atributo | def_metodo",
      "def_atributo → atributo tipo ID",
      "def_metodo → metodo ID ( parametros ) hacer bloque fin_funcion",
    ],
  },
  {
    title: "Bloque y sentencias",
    rules: [
      "bloque → sentencia bloque_rest",
      "bloque_rest → sentencia bloque_rest | ε",
      "sentencia → sent_si | sent_para | sent_mientras | sent_retornar | sent_imprimir | sent_romper | sent_continuar | decl_variable | sent_id",
      "sent_id → ID resto_id",
      "resto_id → = expresion | . ID resto_id | ( argumentos ) | ε",
    ],
  },
  {
    title: "Condicional",
    rules: [
      "sent_si → si expresion entonces bloque rama_sino fin_si",
      "rama_sino → sino bloque | ε",
    ],
  },
  {
    title: "Ciclos",
    rules: [
      "sent_para → para ID desde expresion hasta expresion paso_opt hacer bloque fin_para",
      "paso_opt → paso expresion | ε",
      "sent_mientras → mientras expresion hacer bloque fin_mientras",
    ],
  },
  {
    title: "Sentencias simples",
    rules: [
      "sent_retornar → retornar expresion",
      "sent_imprimir → imprimir ( expresion )",
      "sent_romper → romper",
      "sent_continuar → continuar",
    ],
  },
  {
    title: "Expresiones (precedencia ↓)",
    rules: [
      "expresion → expr_or",
      "expr_or → expr_and expr_or_p",
      "expr_or_p → o expr_and expr_or_p | ε",
      "expr_and → expr_rel expr_and_p",
      "expr_and_p → y expr_rel expr_and_p | ε",
      "expr_rel → expr_add expr_rel_p",
      "expr_rel_p → op_rel expr_add | ε",
      "op_rel → == | != | < | > | <= | >=",
      "expr_add → expr_mul expr_add_p",
      "expr_add_p → + expr_mul expr_add_p | - expr_mul expr_add_p | ε",
      "expr_mul → expr_pot expr_mul_p",
      "expr_mul_p → * expr_pot expr_mul_p | / expr_pot expr_mul_p | % expr_pot expr_mul_p | ε",
      "expr_pot → expr_unaria expr_pot_p",
      "expr_pot_p → ** expr_unaria expr_pot_p | ε",
      "expr_unaria → no expr_unaria | - expr_unaria | expr_primaria",
    ],
  },
  {
    title: "Primarias y tipos",
    rules: [
      "expr_primaria → NUM_ENTERO | NUM_REAL | CADENA_LIT | verdadero | falso | nulo | instanciacion | este sufijo_id | ID sufijo_id | ( expresion )",
      "instanciacion → nuevo ID ( argumentos )",
      "sufijo_id → ( argumentos ) | . ID sufijo_id | ε",
      "argumentos → arg_lista | ε",
      "arg_lista → expresion arg_resto",
      "arg_resto → , expresion arg_resto | ε",
      "tipo → entero | real | cadena | booleano | ID",
      "tipo_basico → entero | real | cadena | booleano",
    ],
  },
];

function RuleLine({ rule, isActive }: { rule: string; isActive: boolean }) {
  const arrowIdx = rule.indexOf("→");
  if (arrowIdx === -1) return <span>{rule}</span>;

  const lhs = rule.substring(0, arrowIdx).trim();
  const rhs = rule.substring(arrowIdx + 1).trim();

  /* Colorize RHS: terminals vs non-terminals vs operators */
  const parts = rhs.split(/(\s+)/);
  const TERMINALS = new Set([
    "si","entonces","sino","fin_si","para","desde","hasta","paso","hacer",
    "fin_para","mientras","fin_mientras","funcion","fin_funcion","retornar",
    "clase","fin_clase","hereda","nuevo","este","metodo","atributo","var","sea",
    "entero","real","cadena","booleano","verdadero","falso","nulo","imprimir",
    "y","o","no","importar","romper","continuar","ID","NUM_ENTERO","NUM_REAL",
    "CADENA_LIT","(",")","=",",",".","+","-","*","/","%","**",
    "==","!=","<",">","<=",">=","$",
  ]);

  return (
    <div
      className="py-0.5 px-2 rounded text-[0.7rem] font-mono leading-relaxed transition-colors duration-150"
      style={{
        backgroundColor: isActive ? "rgba(137,180,250,.12)" : "transparent",
        borderLeft: isActive ? "2px solid var(--color-accent)" : "2px solid transparent",
      }}
    >
      <span style={{ color: "var(--color-accent)", fontWeight: 600 }}>{lhs}</span>
      <span style={{ color: "var(--color-muted)" }}> → </span>
      {parts.map((p, i) => {
        if (p.trim() === "") return <span key={i}>{p}</span>;
        if (p === "|") return <span key={i} style={{ color: "var(--color-muted)" }}> | </span>;
        if (p === "ε") return <span key={i} style={{ color: "var(--color-muted)", fontStyle: "italic" }}>ε</span>;
        if (TERMINALS.has(p)) {
          return <span key={i} style={{ color: "var(--color-success)" }}>{p}</span>;
        }
        return <span key={i} style={{ color: "var(--color-accent)" }}>{p}</span>;
      })}
    </div>
  );
}

export function GrammarPanel({ activeProduction }: GrammarPanelProps) {
  const [openSections, setOpenSections] = useState<Set<number>>(new Set([0, 1, 2, 4, 5]));
  const [isOpen, setIsOpen] = useState(false);

  const toggleSection = (idx: number) => {
    setOpenSections((prev) => {
      const next = new Set(prev);
      if (next.has(idx)) next.delete(idx);
      else next.add(idx);
      return next;
    });
  };

  /* Match active production to a rule */
  const normalizedActive = activeProduction?.split("→")[0]?.trim().toLowerCase() ?? "";

  return (
    <>
      {/* Toggle button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-14 right-3 z-50 flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium shadow-lg transition-all duration-150 cursor-pointer"
        style={{
          backgroundColor: isOpen ? "var(--color-accent)" : "var(--color-surface)",
          color: isOpen ? "var(--color-bg)" : "var(--color-text)",
          border: "1px solid var(--color-border)",
        }}
      >
        <BookOpen className="size-3.5" />
        BNF
      </button>

      {/* Panel */}
      {isOpen && (
        <div
          className="fixed bottom-24 right-3 z-50 w-[380px] max-h-[70vh] rounded-lg shadow-2xl overflow-hidden flex flex-col"
          style={{
            backgroundColor: "var(--color-surface)",
            border: "1px solid var(--color-border)",
          }}
        >
          <div
            className="flex items-center justify-between px-3 py-2 shrink-0"
            style={{ borderBottom: "1px solid var(--color-border)" }}
          >
            <span className="text-xs font-semibold" style={{ color: "var(--color-accent)" }}>
              Gramatica BNF — Claudio
            </span>
            <span className="text-[0.6rem]" style={{ color: "var(--color-muted)" }}>
              52 no-terminales · 59 terminales
            </span>
          </div>
          <ScrollArea className="flex-1">
            <div className="p-2 space-y-1">
              {GRAMMAR_SECTIONS.map((section, sIdx) => (
                <div key={sIdx}>
                  <button
                    onClick={() => toggleSection(sIdx)}
                    className="flex w-full items-center gap-1 py-1 text-[0.65rem] font-semibold uppercase tracking-wider cursor-pointer"
                    style={{ color: "var(--color-muted)" }}
                  >
                    {openSections.has(sIdx) ? (
                      <ChevronDown className="size-3" />
                    ) : (
                      <ChevronRight className="size-3" />
                    )}
                    {section.title}
                  </button>
                  {openSections.has(sIdx) && (
                    <div className="ml-1 mb-2">
                      {section.rules.map((rule, rIdx) => {
                        const ruleLhs = rule.split("→")[0]?.trim().toLowerCase() ?? "";
                        const isActive = normalizedActive !== "" && ruleLhs === normalizedActive;
                        return <RuleLine key={rIdx} rule={rule} isActive={isActive} />;
                      })}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </ScrollArea>
        </div>
      )}
    </>
  );
}
