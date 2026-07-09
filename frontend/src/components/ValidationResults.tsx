import { CheckCircle2, Sparkles, XCircle } from "lucide-react";
import type { ValidationResponse, FixResponse } from "@/types";
import { getScoreColor } from "@/utils";
import { ErrorCard } from "./ErrorCard";
import { WarningCard } from "./WarningCard";
import { DownloadButton } from "./DownloadButton";
import { LoadingSpinner } from "./LoadingSpinner";

interface ValidationResultsProps {
  result: ValidationResponse;
  onFix: () => void;
  fixStatus: "idle" | "loading" | "success" | "error";
  fixResult: FixResponse | null;
  fixError: string | null;
  onLineClick?: (line: number) => void;
}

export function ValidationResults({
  result,
  onFix,
  fixStatus,
  fixResult,
  fixError,
  onLineClick,
}: ValidationResultsProps) {
  const hasIssues = result.errors.length > 0 || result.warnings.length > 0;

  return (
    <div className="space-y-5">
      {/* Summary */}
      <div className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-surface-border bg-surface-850 p-5">
        <div className="flex items-center gap-3">
          {result.valid ? (
            <CheckCircle2 size={22} className="text-success" />
          ) : (
            <XCircle size={22} className="text-danger" />
          )}
          <div>
            <p className="text-sm font-medium text-neutral-100">
              {result.valid ? "Manifest is valid" : "Manifest has blocking errors"}
            </p>
            <p className="text-xs text-neutral-500">
              {result.errors.length} error{result.errors.length === 1 ? "" : "s"} ·{" "}
              {result.warnings.length} warning{result.warnings.length === 1 ? "" : "s"} ·{" "}
              {result.passed_checks.length} passed
              {result.document_count > 1 ? (
                <span className="ml-2 rounded-full bg-surface-700 px-2 py-0.5 text-[11px] font-mono">
                  {result.document_count} docs
                </span>
              ) : null}
            </p>
          </div>
        </div>
        <div className="text-right">
          <p className={`text-2xl font-semibold leading-none ${getScoreColor(result.score)}`}>
            {result.score}
          </p>
          <p className="mt-1 text-[11px] uppercase tracking-wide text-neutral-500">Score</p>
        </div>
      </div>

      {/* Errors */}
      {result.errors.length > 0 ? (
        <div className="space-y-2.5">
          <h3 className="text-xs font-semibold uppercase tracking-wide text-neutral-500">
            Errors ({result.errors.length})
          </h3>
          {result.errors.map((issue, index) => (
            <ErrorCard key={`error-${index}`} issue={issue} onLineClick={onLineClick} />
          ))}
        </div>
      ) : null}

      {/* Warnings */}
      {result.warnings.length > 0 ? (
        <div className="space-y-2.5">
          <h3 className="text-xs font-semibold uppercase tracking-wide text-neutral-500">
            Warnings ({result.warnings.length})
          </h3>
          {result.warnings.map((issue, index) => (
            <WarningCard key={`warning-${index}`} issue={issue} onLineClick={onLineClick} />
          ))}
        </div>
      ) : null}

      {/* Passed checks */}
      {result.passed_checks.length > 0 ? (
        <details className="rounded-xl border border-surface-border bg-surface-850 p-4">
          <summary className="cursor-pointer text-xs font-semibold uppercase tracking-wide text-neutral-500">
            Passed checks ({result.passed_checks.length})
          </summary>
          <ul className="mt-3 space-y-1.5">
            {result.passed_checks.map((check, index) => (
              <li key={index} className="flex items-center gap-2 text-sm text-neutral-400">
                <CheckCircle2 size={14} className="shrink-0 text-success" />
                {check}
              </li>
            ))}
          </ul>
        </details>
      ) : null}

      {/* Fix / download */}
      {hasIssues ? (
        <div className="rounded-xl border border-surface-border bg-surface-850 p-5">
          {!fixResult ? (
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-sm font-medium text-neutral-100">Generate a fixed version</p>
                <p className="mt-0.5 text-xs text-neutral-500">
                  Applies deterministic fixes only — no AI, nothing invented.
                </p>
              </div>
              <button
                type="button"
                onClick={onFix}
                disabled={fixStatus === "loading"}
                className="inline-flex items-center gap-2 rounded-xl border border-accent/40 bg-accent-muted px-4 py-2 text-sm font-medium text-accent transition-colors hover:bg-accent/20 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {fixStatus === "loading" ? (
                  <LoadingSpinner size={14} label="Fixing…" />
                ) : (
                  <>
                    <Sparkles size={15} />
                    Fix manifest
                  </>
                )}
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <p className="text-sm font-medium text-neutral-100">
                  Applied {fixResult.applied_fixes.length} fix
                  {fixResult.applied_fixes.length === 1 ? "" : "es"}
                </p>
                <DownloadButton content={fixResult.fixed_content} />
              </div>
              {fixResult.applied_fixes.length > 0 ? (
                <ul className="space-y-1">
                  {fixResult.applied_fixes.map((fix, index) => (
                    <li key={index} className="flex items-center gap-2 text-sm text-neutral-400">
                      <Sparkles size={13} className="shrink-0 text-accent" />
                      {fix}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-neutral-500">
                  No mechanical fixes applied — remaining issues need a decision only you can make.
                </p>
              )}
            </div>
          )}
          {fixError ? <p className="mt-3 text-xs text-danger">{fixError}</p> : null}
        </div>
      ) : null}
    </div>
  );
}
