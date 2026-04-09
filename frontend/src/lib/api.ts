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

export interface TreeNode {
  simbolo: string;
  lexema: string;
  es_terminal: boolean;
  es_epsilon: boolean;
  hijos: TreeNode[];
}

export interface RecursivoResponse {
  valido: boolean;
  arbol: TreeNode;
  total_nodos: number;
  profundidad: number;
  errores: string[];
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
  arbol: TreeNode;
  traza: TrazaPaso[];
  total_pasos: number;
  tabla_ll1: Record<string, Record<string, string>>;
  primero: Record<string, string[]>;
  siguiente: Record<string, string[]>;
  terminales: string[];
  no_terminales: string[];
  es_ll1: boolean;
  conflictos: string[];
  lexico: LexicoResponse;
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

export function traducirSwift(codigo: string) {
  return post<TraducirResponse>("/traducir", codigo);
}
