import { AlertTriangle, Lightbulb } from "lucide-react";
import type { Issue } from "@/types";
import { getSeverityStyle } from "@/utils";

interface IssueCardProps {
  issue: Issue;
}

/**
 * Renders a single Issue. ErrorCard and WarningCard are thin, semantically
 * distinct wrappers around this — the visual language (severity dot, line
 * number, suggestion) is identical, so the rendering logic lives here once.
 */
export function IssueCard({ issue }: IssueCardProps) {
  const style = getSeverityStyle(issue.severity);

  return (
    <div className={`rounded-xl border ${style.borderClass} ${style.bgClass} p-4`}>
      <div className="flex items-start gap-3">
        <AlertTriangle size={16} className={`mt-0.5 shrink-0 ${style.textClass}`} />
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h4 className="text-sm font-medium text-neutral-100">{issue.title}</h4>
            <span
              className={`inline-flex items-center gap-1 rounded-full border ${style.borderClass} px-2 py-0.5 text-[11px] font-medium ${style.textClass}`}
            >
              <span className={`h-1.5 w-1.5 rounded-full ${style.dotClass}`} />
              {style.label}
            </span>
            {issue.line !== null ? (
              <span className="rounded-full bg-surface-700 px-2 py-0.5 text-[11px] font-mono text-neutral-400">
                line {issue.line}
              </span>
            ) : null}
          </div>
          <p className="mt-1.5 text-sm text-neutral-400">{issue.message}</p>
          {issue.suggestion ? (
            <div className="mt-2 flex items-start gap-1.5 text-xs text-neutral-500">
              <Lightbulb size={13} className="mt-0.5 shrink-0" />
              <span>{issue.suggestion}</span>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
