import { Link } from "react-router-dom";

import { Button } from "../components/ui";

export function NotFoundPage() {
  return (
    <div className="page-shell flex min-h-[calc(100vh-16rem)] flex-col items-center justify-center gap-4 py-24 text-center">
      <span className="flex h-16 w-16 items-center justify-center rounded-full bg-brand-50 text-3xl">
        🧭
      </span>
      <p className="text-sm font-semibold uppercase tracking-wide text-brand-600">404</p>
      <h1 className="text-3xl font-bold text-slate-900">Page not found</h1>
      <p className="max-w-sm text-slate-600">
        The page you're looking for doesn't exist or may have moved.
      </p>
      <Link to="/">
        <Button variant="secondary">Back to home</Button>
      </Link>
    </div>
  );
}
