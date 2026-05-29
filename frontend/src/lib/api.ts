/* ------------------------------------------------------------------ */
/*  API client for the Claudio compiler backend                       */
/* ------------------------------------------------------------------ */

export interface Token {
  lexema: string;
  tipo: string;
  categoria: string;
  fila: number;
  columna: number;
}

export interface LexicoError {
  lexema: string;
  fila: number;
  columna: number;
  mensaje: string;
  esperado?: string;
  simbolo_probable?: string;
  sugerencia_deterministica?: string;
}

export interface SimboloEntry {
  [key: string]: unknown;
}

export interface LexicoResponse {
  tokens: Token[];
  errores: LexicoError[];
  tabla_simbolos: SimboloEntry[];
  total_tokens: number;
  total_errores: number;
}

export interface AISuggestion {
  indice: number;
  explicacion_usuario: string;
  correccion_sugerida: string;
  mini_ejemplo: string;
  confianza: number;
  estado_ia: "pendiente" | "generando" | "lista" | "no_disponible" | "error" | string;
}

export interface SyntaxDiagnostic {
  indice: number;
  fila: number;
  columna: number;
  lexema_encontrado: string;
  tipo_encontrado: string;
  esperados: string[];
  contexto: string;
  sugerencia_deterministica: string;
  sugerencia_ia: AISuggestion | null;
  estado_ia: "pendiente" | "generando" | "lista" | "no_disponible" | "error" | string;
  recuperacion: string;
}

export interface TreeNode {
  simbolo: string;
  lexema: string;
  es_terminal: boolean;
  es_epsilon: boolean;
  fila?: number;
  columna?: number;
  hijos: TreeNode[];
}

export interface RecursivoResponse {
  valido: boolean;
  arbol: TreeNode | null;
  arbol_parcial: TreeNode | null;
  total_nodos: number;
  profundidad: number;
  errores: string[];
  errores_sintacticos: SyntaxDiagnostic[];
  total_errores_sintacticos: number;
  lexico: LexicoResponse;
}

export interface TrazaPaso {
  paso: number;
  pila: string;
  entrada: string;
  accion: string;
}

export interface LL1Response {
  valido: boolean;
  arbol: TreeNode | null;
  arbol_parcial: TreeNode | null;
  errores: string[];
  total_nodos: number;
  profundidad: number;
  traza: TrazaPaso[];
  total_pasos: number;
  tabla_ll1: Record<string, Record<string, string>>;
  primero: Record<string, string[]>;
  siguiente: Record<string, string[]>;
  terminales: string[];
  no_terminales: string[];
  es_ll1: boolean;
  conflictos: string[];
  errores_sintacticos: SyntaxDiagnostic[];
  total_errores_sintacticos: number;
  lexico: LexicoResponse;
}

export interface AISuggestionsResponse {
  estado: string;
  sugerencias: AISuggestion[];
}

export interface MapeoLinea {
  claudio: string;
  swift: string;
}

export interface TraducirResponse {
  swift: string;
  mapeo: MapeoLinea[];
}

export interface ProgramasResponse {
  programas: Record<string, string>;
}

export interface SemanticDiagnostic {
  indice: number;
  fila: number;
  columna: number;
  lexema: string;
  regla: string;
  mensaje: string;
  sugerencia: string;
  sugerencia_ia: AISuggestion | null;
  estado_ia: "pendiente" | "generando" | "lista" | "no_disponible" | "error" | string;
}

export interface SemanticSimboloEntry {
  nombre: string;
  tipo: string;
  inmutable: boolean;
  inicializado: boolean;
  ambito: number;
  fila: number;
  columna: number;
}

export interface SemanticoResponse {
  valido: boolean;
  errores_semanticos: SemanticDiagnostic[];
  total_errores_semanticos: number;
  tabla_simbolos: SemanticSimboloEntry[];
  arbol_parcial: TreeNode | null;
  lexico: LexicoResponse;
}

const BASE = "/api";

async function post<T>(endpoint: string, codigo: string): Promise<T> {
  const res = await fetch(`${BASE}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ codigo }),
  });
  if (!res.ok) {
    throw new Error(`Error ${res.status}: ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export function fetchProgramas(): Promise<ProgramasResponse> {
  return fetch(`${BASE}/programas`).then((r) => {
    if (!r.ok) throw new Error(`Error ${r.status}`);
    return r.json() as Promise<ProgramasResponse>;
  });
}

export function analizarLexico(codigo: string) {
  return post<LexicoResponse>("/lexico", codigo);
}

export function analizarRecursivo(codigo: string) {
  return post<RecursivoResponse>("/recursivo", codigo);
}

export function analizarLL1(codigo: string) {
  return post<LL1Response>("/ll1", codigo);
}

export function analizarSemantico(codigo: string) {
  return post<SemanticoResponse>("/semantico", codigo);
}

export function traducirSwift(codigo: string) {
  return post<TraducirResponse>("/traducir", codigo);
}

export function generarSugerenciasIA(codigo: string, diagnosticos: SyntaxDiagnostic[]) {
  return fetch(`${BASE}/sugerencias-ia`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ codigo, diagnosticos }),
  }).then((r) => {
    if (!r.ok) throw new Error(`Error ${r.status}`);
    return r.json() as Promise<AISuggestionsResponse>;
  });
}

export function generarSugerenciasIASemantico(
  codigo: string,
  diagnosticos: SemanticDiagnostic[],
) {
  return fetch(`${BASE}/sugerencias-ia-semantico`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ codigo, diagnosticos }),
  }).then((r) => {
    if (!r.ok) throw new Error(`Error ${r.status}`);
    return r.json() as Promise<AISuggestionsResponse>;
  });
}
