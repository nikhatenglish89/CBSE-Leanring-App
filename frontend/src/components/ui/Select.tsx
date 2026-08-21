import { type SelectHTMLAttributes, forwardRef, useId } from "react";

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label: string;
  error?: string;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, error, id, className = "", children, ...props }, ref) => {
    const generatedId = useId();
    const selectId = id ?? generatedId;
    const errorId = `${selectId}-error`;

    return (
      <div className="flex flex-col gap-1">
        <label htmlFor={selectId} className="text-sm font-medium text-slate-700">
          {label}
        </label>
        <select
          ref={ref}
          id={selectId}
          aria-invalid={Boolean(error)}
          aria-describedby={error ? errorId : undefined}
          className={`rounded-lg border px-3 py-2 text-sm text-slate-900 outline-none transition-colors
            focus:border-brand-600 focus:ring-2 focus:ring-brand-100 disabled:cursor-not-allowed disabled:opacity-60
            ${error ? "border-red-400" : "border-slate-300"} ${className}`}
          {...props}
        >
          {children}
        </select>
        {error && (
          <p id={errorId} className="text-sm text-red-600">
            {error}
          </p>
        )}
      </div>
    );
  }
);
Select.displayName = "Select";
