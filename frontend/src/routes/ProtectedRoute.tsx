import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";

import { roleHomePath } from "../lib/roleRoutes";
import { useAuthStore } from "../store/authStore";
import type { UserRole } from "../types/auth";

/**
 * UX convenience only, per docs/ARCHITECTURE.md §7 — the backend's
 * require_permission() dependency is the real authorization boundary, not
 * this guard. `allow` just steers a signed-in user with the wrong role to
 * their own dashboard instead of showing them someone else's.
 */
export function ProtectedRoute({
  children,
  allow,
  skipPasswordResetCheck,
}: {
  children: ReactNode;
  allow?: UserRole[];
  /** Only the reset page itself sets this — every other protected route
   * must redirect there until an admin-created account's temporary
   * password has been changed. */
  skipPasswordResetCheck?: boolean;
}) {
  const user = useAuthStore((s) => s.user);
  const isAuthenticated = useAuthStore((s) => Boolean(s.user && s.accessToken));

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  if (user.must_reset_password && !skipPasswordResetCheck) {
    return <Navigate to="/force-password-reset" replace />;
  }

  if (allow && !allow.includes(user.role)) {
    return <Navigate to={roleHomePath(user.role)} replace />;
  }

  return <>{children}</>;
}
