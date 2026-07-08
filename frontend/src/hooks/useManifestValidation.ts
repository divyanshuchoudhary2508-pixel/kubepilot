import { useCallback, useState } from "react";
import { validateManifest, fixManifest, ManifestApiError } from "@/services";
import type { ValidationResponse, FixResponse } from "@/types";

export type AsyncStatus = "idle" | "loading" | "success" | "error";

interface UseManifestValidationResult {
  content: string;
  setContent: (value: string) => void;

  validationResult: ValidationResponse | null;
  validationStatus: AsyncStatus;
  validationError: string | null;
  runValidation: () => Promise<void>;

  fixResult: FixResponse | null;
  fixStatus: AsyncStatus;
  fixError: string | null;
  runFix: () => Promise<void>;

  reset: () => void;
}

export function useManifestValidation(initialContent = ""): UseManifestValidationResult {
  const [content, setContentState] = useState(initialContent);

  const [validationResult, setValidationResult] = useState<ValidationResponse | null>(null);
  const [validationStatus, setValidationStatus] = useState<AsyncStatus>("idle");
  const [validationError, setValidationError] = useState<string | null>(null);

  const [fixResult, setFixResult] = useState<FixResponse | null>(null);
  const [fixStatus, setFixStatus] = useState<AsyncStatus>("idle");
  const [fixError, setFixError] = useState<string | null>(null);

  const setContent = useCallback((value: string) => {
    setContentState(value);
    // Editing invalidates any previous report/fix — avoids showing stale results.
    setValidationResult(null);
    setValidationStatus("idle");
    setValidationError(null);
    setFixResult(null);
    setFixStatus("idle");
    setFixError(null);
  }, []);

  const runValidation = useCallback(async () => {
    if (!content.trim()) {
      setValidationError("Paste or upload a manifest first.");
      setValidationStatus("error");
      return;
    }
    setValidationStatus("loading");
    setValidationError(null);
    setFixResult(null);
    setFixStatus("idle");
    try {
      const result = await validateManifest(content);
      setValidationResult(result);
      setValidationStatus("success");
    } catch (error) {
      const message = error instanceof ManifestApiError ? error.message : "Something went wrong.";
      setValidationError(message);
      setValidationStatus("error");
    }
  }, [content]);

  const runFix = useCallback(async () => {
    if (!content.trim()) return;
    setFixStatus("loading");
    setFixError(null);
    try {
      const result = await fixManifest(content);
      setFixResult(result);
      setFixStatus("success");
    } catch (error) {
      const message = error instanceof ManifestApiError ? error.message : "Something went wrong.";
      setFixError(message);
      setFixStatus("error");
    }
  }, [content]);

  const reset = useCallback(() => {
    setContent("");
  }, [setContent]);

  return {
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
    reset,
  };
}
