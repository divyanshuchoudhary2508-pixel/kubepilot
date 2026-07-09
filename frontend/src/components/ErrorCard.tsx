import type { Issue } from "@/types";
import { IssueCard } from "./IssueCard";

interface ErrorCardProps {
  issue: Issue;
  onLineClick?: (line: number) => void;
}

export function ErrorCard({ issue, onLineClick }: ErrorCardProps) {
  return <IssueCard issue={issue} onLineClick={onLineClick} />;
}
