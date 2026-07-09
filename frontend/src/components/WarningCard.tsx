import type { Issue } from "@/types";
import { IssueCard } from "./IssueCard";

interface WarningCardProps {
  issue: Issue;
  onLineClick?: (line: number) => void;
}

export function WarningCard({ issue, onLineClick }: WarningCardProps) {
  return <IssueCard issue={issue} onLineClick={onLineClick} />;
}
