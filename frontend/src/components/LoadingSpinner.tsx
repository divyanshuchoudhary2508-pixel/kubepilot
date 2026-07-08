import { Loader2 } from "lucide-react";

interface LoadingSpinnerProps {
  size?: number;
  label?: string;
  className?: string;
}

export function LoadingSpinner({ size = 16, label, className = "" }: LoadingSpinnerProps) {
  return (
    <span className={`inline-flex items-center gap-2 ${className}`}>
      <Loader2 size={size} className="animate-spin" aria-hidden="true" />
      {label ? <span className="text-sm text-neutral-400">{label}</span> : null}
    </span>
  );
}
