"use client";

import { useEffect, useRef, useCallback } from "react";
import { EditorState } from "@codemirror/state";
import { EditorView, keymap, lineNumbers, highlightActiveLine, highlightActiveLineGutter } from "@codemirror/view";
import { defaultKeymap, history, historyKeymap } from "@codemirror/commands";
import { bracketMatching } from "@codemirror/language";
import { claudioLanguage, claudioHighlightStyle } from "@/lib/claudio-lang";

interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  onAnalyze?: () => void;
  errorLines?: number[];
}

export function CodeEditor({ value, onChange, onAnalyze, errorLines = [] }: CodeEditorProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const viewRef = useRef<EditorView | null>(null);
  const onChangeRef = useRef(onChange);
  const onAnalyzeRef = useRef(onAnalyze);

  onChangeRef.current = onChange;
  onAnalyzeRef.current = onAnalyze;

  /* Create the editor once */
  useEffect(() => {
    if (!containerRef.current) return;

    const analyzeKeymap = keymap.of([
      {
        key: "Ctrl-Enter",
        run: () => {
          onAnalyzeRef.current?.();
          return true;
        },
      },
      {
        key: "Cmd-Enter",
        run: () => {
          onAnalyzeRef.current?.();
          return true;
        },
      },
    ]);

    const updateListener = EditorView.updateListener.of((update) => {
      if (update.docChanged) {
        onChangeRef.current(update.state.doc.toString());
      }
    });

    const state = EditorState.create({
      doc: value,
      extensions: [
        lineNumbers(),
        highlightActiveLine(),
        highlightActiveLineGutter(),
        history(),
        bracketMatching(),
        claudioLanguage,
        claudioHighlightStyle,
        keymap.of([...defaultKeymap, ...historyKeymap]),
        analyzeKeymap,
        updateListener,
        EditorView.lineWrapping,
        EditorView.theme({
          "&": {
            height: "100%",
            fontSize: "clamp(0.75rem, 0.7rem + 0.2vw, 0.875rem)",
          },
          ".cm-scroller": {
            fontFamily: "var(--font-mono)",
            overflow: "auto",
          },
          ".cm-content": {
            caretColor: "var(--color-accent)",
            padding: "var(--space-8) 0",
          },
          ".cm-line": {
            padding: "0 var(--space-8)",
          },
        }),
      ],
    });

    const view = new EditorView({
      state,
      parent: containerRef.current,
    });

    viewRef.current = view;

    return () => {
      view.destroy();
      viewRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  /* Sync external value changes (e.g. program selection) */
  useEffect(() => {
    const view = viewRef.current;
    if (!view) return;
    const currentDoc = view.state.doc.toString();
    if (currentDoc !== value) {
      view.dispatch({
        changes: { from: 0, to: currentDoc.length, insert: value },
      });
    }
  }, [value]);

  /* Highlight error lines */
  const highlightErrors = useCallback(() => {
    const view = viewRef.current;
    if (!view) return;
    // Remove existing error decorations by resetting theme — we use CSS class approach
    const lineElements = view.dom.querySelectorAll(".cm-line");
    lineElements.forEach((el) => el.classList.remove("cm-error-line"));

    errorLines.forEach((lineNum) => {
      try {
        const line = view.state.doc.line(lineNum);
        const domLine = view.domAtPos(line.from);
        const lineEl = domLine.node.parentElement;
        if (lineEl?.classList.contains("cm-line")) {
          lineEl.classList.add("cm-error-line");
        }
      } catch {
        /* Line may not exist */
      }
    });
  }, [errorLines]);

  useEffect(() => {
    highlightErrors();
  }, [highlightErrors]);

  /* External navigation from diagnostics panel */
  useEffect(() => {
    const handler = (event: Event) => {
      const detail = (event as CustomEvent<{ fila?: number; columna?: number }>).detail;
      const view = viewRef.current;
      if (!view || !detail?.fila) return;
      try {
        const lineInfo = view.state.doc.line(detail.fila);
        const columnOffset = Math.max(0, (detail.columna ?? 1) - 1);
        const pos = Math.min(lineInfo.to, lineInfo.from + columnOffset);
        view.dispatch({
          selection: { anchor: pos },
          scrollIntoView: true,
        });
        view.focus();
      } catch {
        /* Line may not exist */
      }
    };

    window.addEventListener("claudio:jump-to-line", handler);
    return () => window.removeEventListener("claudio:jump-to-line", handler);
  }, []);

  return (
    <div
      ref={containerRef}
      className="h-full w-full overflow-hidden"
      style={{ backgroundColor: "var(--color-surface-2)" }}
      role="textbox"
      aria-label="Editor de codigo Claudio"
      aria-multiline="true"
    />
  );
}

/* Jump to a specific line */
export function jumpToLine(view: EditorView | null, line: number) {
  if (!view) return;
  try {
    const lineInfo = view.state.doc.line(line);
    view.dispatch({
      selection: { anchor: lineInfo.from },
      scrollIntoView: true,
    });
    view.focus();
  } catch {
    /* Line may not exist */
  }
}
