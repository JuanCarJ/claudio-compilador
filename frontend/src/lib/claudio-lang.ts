/* ------------------------------------------------------------------ */
/*  CodeMirror 6 language support for Claudio                         */
/*  Simple StreamLanguage-based highlighting for Spanish keywords      */
/* ------------------------------------------------------------------ */

import { StreamLanguage, type StreamParser } from "@codemirror/language";
import { tags as t } from "@lezer/highlight";
import { HighlightStyle, syntaxHighlighting } from "@codemirror/language";

const KEYWORDS = new Set([
  "si", "entonces", "sino", "fin_si",
  "para", "desde", "hasta", "paso", "hacer", "fin_para",
  "mientras", "fin_mientras",
  "funcion", "fin_funcion", "retornar",
  "clase", "fin_clase", "hereda", "nuevo", "este", "metodo", "atributo",
  "var", "sea",
  "imprimir",
  "y", "o", "no",
  "importar", "romper", "continuar",
]);

const TYPES = new Set([
  "entero", "real", "cadena", "booleano",
]);

const LITERALS = new Set([
  "verdadero", "falso", "nulo",
]);

interface ClaudioState {
  inString: false | '"' | "'";
  inComment: boolean;
}

const claudioParser: StreamParser<ClaudioState> = {
  name: "claudio",

  startState(): ClaudioState {
    return { inString: false, inComment: false };
  },

  token(stream, state): string | null {
    /* Multi-line comment continuation */
    if (state.inComment) {
      if (stream.match("*/")) {
        state.inComment = false;
      } else {
        stream.next();
      }
      return "comment";
    }

    /* String continuation */
    if (state.inString) {
      const quote = state.inString;
      while (!stream.eol()) {
        const ch = stream.next();
        if (ch === "\\") {
          stream.next(); // skip escaped char
        } else if (ch === quote) {
          state.inString = false;
          return "string";
        }
      }
      return "string";
    }

    /* Skip whitespace */
    if (stream.eatSpace()) return null;

    /* Single-line comment */
    if (stream.match("//")) {
      stream.skipToEnd();
      return "comment";
    }

    /* Multi-line comment start */
    if (stream.match("/*")) {
      state.inComment = true;
      return "comment";
    }

    /* Strings */
    const ch = stream.peek();
    if (ch === '"' || ch === "'") {
      state.inString = ch as '"' | "'";
      stream.next();
      return "string";
    }

    /* Numbers */
    if (stream.match(/^[0-9]+(\.[0-9]+)?/)) {
      return "number";
    }

    /* Operators */
    if (stream.match(/^[+\-*/%=<>!&|^~]+/)) {
      return "operator";
    }

    /* Delimiters */
    if (stream.match(/^[(){}[\],;:.]/)) {
      return "punctuation";
    }

    /* Words: keywords, types, literals, identifiers */
    if (stream.match(/^[a-zA-Z_\u00C0-\u024F][a-zA-Z0-9_\u00C0-\u024F]*/)) {
      const word = stream.current();
      if (KEYWORDS.has(word)) return "keyword";
      if (TYPES.has(word)) return "typeName";
      if (LITERALS.has(word)) return "bool";
      return "variableName";
    }

    /* Fallback */
    stream.next();
    return null;
  },
};

export const claudioLanguage = StreamLanguage.define(claudioParser);

/* Syntax highlight colors matching the Claudio palette */
export const claudioHighlightStyle = syntaxHighlighting(
  HighlightStyle.define([
    { tag: t.keyword, color: "var(--token-keyword)", fontWeight: "500" },
    { tag: t.variableName, color: "var(--token-identifier)" },
    { tag: t.number, color: "var(--token-number)" },
    { tag: t.string, color: "var(--token-string)" },
    { tag: t.bool, color: "var(--token-number)" },
    { tag: t.operator, color: "var(--token-operator)" },
    { tag: t.punctuation, color: "var(--token-delimiter)" },
    { tag: t.comment, color: "var(--token-comment)", fontStyle: "italic" },
    { tag: t.typeName, color: "var(--token-type)" },
  ])
);
