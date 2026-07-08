import { useCallback, useRef, useState } from "react";
import { UploadCloud, FileText } from "lucide-react";

interface UploadBoxProps {
  onFileLoaded: (content: string, filename: string) => void;
}

const ACCEPTED_EXTENSIONS = [".yaml", ".yml"];

function isYamlFile(file: File): boolean {
  const name = file.name.toLowerCase();
  return ACCEPTED_EXTENSIONS.some((ext) => name.endsWith(ext));
}

export function UploadBox({ onFileLoaded }: UploadBoxProps) {
  const [isDragActive, setIsDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastFilename, setLastFilename] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const readFile = useCallback(
    (file: File) => {
      if (!isYamlFile(file)) {
        setError("Only .yaml or .yml files are supported.");
        return;
      }
      setError(null);
      const reader = new FileReader();
      reader.onload = () => {
        if (typeof reader.result === "string") {
          onFileLoaded(reader.result, file.name);
          setLastFilename(file.name);
        }
      };
      reader.onerror = () => setError("Could not read that file.");
      reader.readAsText(file);
    },
    [onFileLoaded],
  );

  const handleDrop = useCallback(
    (event: React.DragEvent<HTMLDivElement>) => {
      event.preventDefault();
      setIsDragActive(false);
      const file = event.dataTransfer.files[0];
      if (file) readFile(file);
    },
    [readFile],
  );

  const handleInputChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0];
      if (file) readFile(file);
      // Allow re-uploading the same filename twice in a row.
      event.target.value = "";
    },
    [readFile],
  );

  return (
    <div>
      <div
        role="button"
        tabIndex={0}
        onClick={() => inputRef.current?.click()}
        onKeyDown={(event) => {
          if (event.key === "Enter" || event.key === " ") inputRef.current?.click();
        }}
        onDragOver={(event) => {
          event.preventDefault();
          setIsDragActive(true);
        }}
        onDragLeave={() => setIsDragActive(false)}
        onDrop={handleDrop}
        className={`flex cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border border-dashed px-6 py-8 text-center transition-colors ${
          isDragActive
            ? "border-accent bg-accent-muted"
            : "border-surface-border bg-surface-850 hover:border-surface-600 hover:bg-surface-800"
        }`}
      >
        {lastFilename ? (
          <FileText size={22} className="text-accent" />
        ) : (
          <UploadCloud size={22} className="text-neutral-500" />
        )}
        <p className="text-sm text-neutral-300">
          {lastFilename ? (
            <span className="font-medium text-neutral-100">{lastFilename}</span>
          ) : (
            <>
              <span className="font-medium text-neutral-100">Drop a manifest</span> or click to upload
            </>
          )}
        </p>
        <p className="text-xs text-neutral-500">.yaml or .yml — or just paste directly into the editor below</p>
        <input
          ref={inputRef}
          type="file"
          accept=".yaml,.yml"
          onChange={handleInputChange}
          className="hidden"
          aria-label="Upload a YAML manifest"
        />
      </div>
      {error ? <p className="mt-2 text-xs text-danger">{error}</p> : null}
    </div>
  );
}
