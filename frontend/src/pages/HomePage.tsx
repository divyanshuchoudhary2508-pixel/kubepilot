import { useCallback, useRef, useState } from "react";
import { ChevronDown, FlaskConical } from "lucide-react";
import {
  Navbar,
  UploadBox,
  MonacoEditor,
  ValidateButton,
  ValidationResults,
  LoadingSpinner,
} from "@/components";
import type { MonacoEditor as MonacoEditorInstance, MonacoInstance } from "@/components/MonacoEditor";
import { useManifestValidation } from "@/hooks";
import { PLACEHOLDER_MANIFEST, EXAMPLE_MANIFESTS } from "@/utils";
import type { Issue } from "@/types";

/**
 * Convert a KubePilot Issue into a Monaco editor marker.
 * Monaco severity: 1=hint, 2=info, 4=warning, 8=error
 */
function toMonacoSeverity(severity: Issue["severity"], monacoSeverity: MonacoInstance["MarkerSeverity"]) {
  if (severity === "high") return monacoSeverity.Error;
  if (severity === "medium") return monacoSeverity.Warning;
  return monacoSeverity.Hint;
}

export function HomePage() {
  const {
    content,
    setContent,
    validationResult,
    validationStatus,
    validationError,
    runValidation,
    fixResult,
    fixStatus,
    fixError,
    runFix,
  } = useManifestValidation(PLACEHOLDER_MANIFEST);

  // Refs to the Monaco editor + monaco instance so we can set markers and jump lines.
  const editorRef = useRef<MonacoEditorInstance | null>(null);
  const monacoRef = useRef<MonacoInstance | null>(null);
  // Decoration ID refs for the click-to-jump highlight (cleared after 1 s).
  const decorationsRef = useRef<string[]>([]);

  const [showExamples, setShowExamples] = useState(false);

  // ------------------------------------------------------------------ //
  // Monaco mount
  // ------------------------------------------------------------------ //
  const handleEditorMount = useCallback(
    (editor: MonacoEditorInstance, monaco: MonacoInstance) => {
      editorRef.current = editor;
      monacoRef.current = monaco;
    },
    [],
  );

  // ------------------------------------------------------------------ //
  // Set Monaco inline markers after validation
  // ------------------------------------------------------------------ //
  const setMonacoMarkers = useCallback(
    (issues: Issue[]) => {
      const editor = editorRef.current;
      const monaco = monacoRef.current;
      if (!editor || !monaco) return;

      const model = editor.getModel();
      if (!model) return;

      const markers = issues
        .filter((issue) => issue.line !== null)
        .map((issue) => ({
          startLineNumber: issue.line!,
          endLineNumber: issue.line!,
          startColumn: 1,
          endColumn: model.getLineMaxColumn(issue.line!),
          message: `[${issue.severity.toUpperCase()}] ${issue.title}: ${issue.message}`,
          severity: toMonacoSeverity(issue.severity, monaco.MarkerSeverity),
          source: "KubePilot",
        }));

      monaco.editor.setModelMarkers(model, "kubepilot", markers);
    },
    [],
  );

  const clearMonacoMarkers = useCallback(() => {
    const editor = editorRef.current;
    const monaco = monacoRef.current;
    if (!editor || !monaco) return;
    const model = editor.getModel();
    if (model) monaco.editor.setModelMarkers(model, "kubepilot", []);
  }, []);

  // ------------------------------------------------------------------ //
  // Validate: set markers when done
  // ------------------------------------------------------------------ //
  const handleValidate = useCallback(async () => {
    clearMonacoMarkers();
    await runValidation();
  }, [runValidation, clearMonacoMarkers]);

  // Whenever validationResult updates (after a run), push markers.
  // We do this via a useEffect-like pattern inside the component.
  // Actually, because runValidation is awaited in handleValidate, we can
  // just set markers right after — but validationResult is stale in the
  // callback. Instead we use a ref-based approach in the ValidationResults
  // render path: the parent just re-renders and calls setMonacoMarkers via
  // a useEffect triggered by validationResult change.
  // Simpler: set markers inline after runValidation resolves.
  // The hook already updates validationResult state; we watch it via a
  // separate effect declared inline. Since hooks can't be called inside
  // callbacks, we handle this with a small helper below.

  // ------------------------------------------------------------------ //
  // Click-to-jump
  // ------------------------------------------------------------------ //
  const handleLineClick = useCallback((line: number) => {
    const editor = editorRef.current;
    const monaco = monacoRef.current;
    if (!editor || !monaco) return;

    editor.revealLineInCenter(line);

    // Brief yellow highlight on the target line.
    if (decorationsRef.current.length > 0) {
      decorationsRef.current = editor.deltaDecorations(decorationsRef.current, []);
    }
    decorationsRef.current = editor.deltaDecorations([], [
      {
        range: new monaco.Range(line, 1, line, 1),
        options: {
          isWholeLine: true,
          className: "monaco-jump-highlight",
          linesDecorationsClassName: "monaco-jump-highlight-gutter",
        },
      },
    ]);

    // Clear after 1.2 s.
    setTimeout(() => {
      if (editorRef.current && decorationsRef.current.length > 0) {
        decorationsRef.current = editorRef.current.deltaDecorations(decorationsRef.current, []);
      }
    }, 1200);
  }, []);

  // ------------------------------------------------------------------ //
  // Content change: clear markers
  // ------------------------------------------------------------------ //
  const handleContentChange = useCallback(
    (value: string) => {
      setContent(value);
      clearMonacoMarkers();
    },
    [setContent, clearMonacoMarkers],
  );

  const handleFileLoaded = useCallback(
    (fileContent: string) => {
      handleContentChange(fileContent);
    },
    [handleContentChange],
  );

  return (
    <div className="min-h-full bg-surface-950">
      {/* Monaco jump highlight style — injected once */}
      <style>{`
        .monaco-jump-highlight { background: rgba(232, 163, 61, 0.18) !important; }
        .monaco-jump-highlight-gutter { background: #e8a33d; width: 3px !important; }
      `}</style>

      <Navbar />

      <main className="mx-auto max-w-4xl px-6 py-10">
        <div className="mb-8">
          <h2 className="text-lg font-semibold text-neutral-100">Validate a Kubernetes manifest</h2>
          <p className="mt-1 text-sm text-neutral-500">
            Paste YAML below, or upload a file. Nothing leaves your machine except the manifest text
            sent to the validator.
          </p>
        </div>

        <div className="space-y-5">
          <UploadBox onFileLoaded={handleFileLoaded} />

          {/* Examples picker */}
          <div className="relative">
            <button
              type="button"
              id="examples-toggle"
              onClick={() => setShowExamples((v) => !v)}
              className="inline-flex items-center gap-1.5 rounded-lg border border-surface-border bg-surface-800 px-3 py-1.5 text-xs font-medium text-neutral-400 transition-colors hover:border-accent/40 hover:text-neutral-200"
            >
              <FlaskConical size={13} />
              Load an example
              <ChevronDown
                size={13}
                className={`transition-transform ${showExamples ? "rotate-180" : ""}`}
              />
            </button>

            {showExamples ? (
              <div className="absolute left-0 top-9 z-20 w-80 overflow-hidden rounded-xl border border-surface-border bg-surface-850 shadow-panel">
                {EXAMPLE_MANIFESTS.map((ex) => (
                  <button
                    key={ex.label}
                    type="button"
                    onClick={() => {
                      handleContentChange(ex.content);
                      setShowExamples(false);
                    }}
                    className="flex w-full flex-col items-start gap-0.5 px-4 py-3 text-left transition-colors hover:bg-surface-800"
                  >
                    <span className="text-sm font-medium text-neutral-200">{ex.label}</span>
                    <span className="text-xs text-neutral-500">{ex.description}</span>
                  </button>
                ))}
              </div>
            ) : null}
          </div>

          <MonacoEditor
            value={content}
            onChange={handleContentChange}
            onEditorMount={handleEditorMount}
          />

          <div className="flex items-center gap-3">
            <ValidateButton
              onClick={async () => {
                clearMonacoMarkers();
                await runValidation();
                // After validation resolves, validationResult is still the
                // old value in this closure — we let the render effect handle markers.
              }}
              isLoading={validationStatus === "loading"}
              disabled={!content.trim()}
            />
            {validationStatus === "error" && validationError ? (
              <p className="text-sm text-danger">{validationError}</p>
            ) : null}
          </div>

          {validationStatus === "loading" ? (
            <div className="flex justify-center py-6">
              <LoadingSpinner size={18} label="Running validation checks…" />
            </div>
          ) : null}

          {validationResult ? (
            <>
              {/* Set markers whenever validationResult changes — rendered synchronously */}
              <MarkerSetter
                issues={[...validationResult.errors, ...validationResult.warnings]}
                setMarkers={setMonacoMarkers}
              />
              <ValidationResults
                result={validationResult}
                onFix={runFix}
                fixStatus={fixStatus}
                fixResult={fixResult}
                fixError={fixError}
                onLineClick={handleLineClick}
              />
            </>
          ) : null}
        </div>
      </main>
    </div>
  );
}

/**
 * Tiny render-effect component: calls setMarkers whenever its `issues` prop
 * changes. This sidesteps having to put a useEffect in the parent's callback.
 */
function MarkerSetter({
  issues,
  setMarkers,
}: {
  issues: Issue[];
  setMarkers: (issues: Issue[]) => void;
}) {
  // Call setMarkers on every render where issues changes.
  // We use a ref to avoid calling on the very first render with stale data.
  const prevIssues = useRef<Issue[] | null>(null);
  if (prevIssues.current !== issues) {
    prevIssues.current = issues;
    setMarkers(issues);
  }
  return null;
}
