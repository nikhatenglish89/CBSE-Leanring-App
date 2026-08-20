interface SpinnerProps {
  label?: string;
  className?: string;
}

export function Spinner({ label = "Loading", className = "" }: SpinnerProps) {
  return (
    <span role="status" className={`inline-flex items-center gap-2 text-sm text-slate-600 ${className}`}>
      <span
        className="h-4 w-4 animate-spin rounded-full border-2 border-slate-300 border-t-brand-600"
        aria-hidden="true"
      />
      <span className="sr-only">{label}</span>
    </span>
  );
}
