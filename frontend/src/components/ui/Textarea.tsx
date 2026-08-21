import { type TextareaHTMLAttributes, forwardRef, useId } from "react";

interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label: string;
  error?: string;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ label, error, id, className = "", ...props }, ref) => {
    const generatedId = useId();
    const textareaId = id ?? generatedId;
    const errorId = `${textareaId}-error`;

    return (
      <div className="flex flex-col gap-1">
        <label htmlFor={textareaId} className="text-sm font-medium text-slate-700">
          {label}
        </label>
        <textarea
          ref={ref}
          id={textareaId}
          aria-invalid={Boolean(error)}
          aria-describedby={error ? errorId : undefined}
          className={`rounded-lg border px-3 py-2 text-sm text-slate-900 outline-none transition-colors
            focus:border-brand-600 focus:ring-2 focus:ring-brand-100
            ${error ? "border-red-400" : "border-slate-300"} ${className}`}
          {...props}
        />
        {error && (
          <p id={errorId} className="text-sm text-red-600">
            {error}
          </p>
        )}
      </div>
    );
  }
);
Textarea.displayName = "Textarea";
