import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";

import { useAuthStore } from "../store/authStore";

/**
 * UX convenience only, per docs/ARCHITECTURE.md §7 — the backend's
 * require_permission() dependency is the real authorization boundary, not
 * this guard.
 */
export function ProtectedRoute({ children }: { children: ReactNode }) {
  const isAuthenticated = useAuthStore((s) => Boolean(s.user && s.accessToken));

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}
