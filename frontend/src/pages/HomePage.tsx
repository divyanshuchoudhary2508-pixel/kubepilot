import { useCallback } from "react";
import {
  Navbar,
  UploadBox,
  MonacoEditor,
  ValidateButton,
  ValidationResults,
  LoadingSpinner,
} from "@/components";
import { useManifestValidation } from "@/hooks";
import { PLACEHOLDER_MANIFEST } from "@/utils";

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

  const handleFileLoaded = useCallback(
    (fileContent: string) => {
      setContent(fileContent);
    },
    [setContent],
  );

  return (
    <div className="min-h-full bg-surface-950">
      <Navbar />

      <main className="mx-auto max-w-4xl px-6 py-10">
        <div className="mb-8">
          <h2 className="text-lg font-semibold text-neutral-100">Validate a Kubernetes manifest</h2>
          <p className="mt-1 text-sm text-neutral-500">
            Paste YAML below, or upload a file. Nothing leaves your machine except the manifest text sent to the
            validator.
          </p>
        </div>

        <div className="space-y-5">
          <UploadBox onFileLoaded={handleFileLoaded} />

          <MonacoEditor value={content} onChange={setContent} />

          <div className="flex items-center gap-3">
            <ValidateButton
              onClick={runValidation}
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
            <ValidationResults
              result={validationResult}
              onFix={runFix}
              fixStatus={fixStatus}
              fixResult={fixResult}
              fixError={fixError}
            />
          ) : null}
        </div>
      </main>
    </div>
  );
}
