import { ShieldCheck } from "lucide-react";
import { LoadingSpinner } from "./LoadingSpinner";

interface ValidateButtonProps {
  onClick: () => void;
  isLoading: boolean;
  disabled?: boolean;
}

export function ValidateButton({ onClick, isLoading, disabled = false }: ValidateButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled || isLoading}
      className="inline-flex items-center gap-2 rounded-xl bg-accent px-5 py-2.5 text-sm font-medium text-white transition-colors hover:bg-accent-hover disabled:cursor-not-allowed disabled:opacity-50"
    >
      {isLoading ? (
        <LoadingSpinner size={15} label="Validating…" />
      ) : (
        <>
          <ShieldCheck size={16} />
          Validate
        </>
      )}
    </button>
  );
}
