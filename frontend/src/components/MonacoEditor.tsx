import Editor, { type OnChange } from "@monaco-editor/react";

interface MonacoEditorProps {
  value: string;
  onChange: (value: string) => void;
  height?: string;
}

export function MonacoEditor({ value, onChange, height = "420px" }: MonacoEditorProps) {
  const handleChange: OnChange = (newValue) => {
    onChange(newValue ?? "");
  };

  return (
    <div className="overflow-hidden rounded-xl border border-surface-border bg-surface-850 shadow-panel">
      <div className="flex items-center justify-between border-b border-surface-border px-4 py-2">
        <span className="text-xs font-medium text-neutral-500">manifest.yaml</span>
        <span className="text-xs text-neutral-600">YAML</span>
      </div>
      <Editor
        height={height}
        defaultLanguage="yaml"
        language="yaml"
        theme="vs-dark"
        value={value}
        onChange={handleChange}
        options={{
          fontSize: 13,
          fontFamily: "'JetBrains Mono', Menlo, monospace",
          lineNumbers: "on",
          wordWrap: "on",
          minimap: { enabled: false },
          scrollBeyondLastLine: false,
          automaticLayout: true,
          padding: { top: 12, bottom: 12 },
          renderLineHighlight: "gutter",
          tabSize: 2,
        }}
      />
    </div>
  );
}
