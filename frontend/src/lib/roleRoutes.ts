import type { UserRole } from "../types/auth";

/**
 * Where each role lands after login/register, and which roles may view
 * each role-scoped route group. ADMIN-family roles share the /admin
 * placeholder for now — dedicated CONTENT_MANAGER/SUPPORT_AGENT views
 * land with the admin dashboard in a later phase.
 */
export const ROLE_HOME: Record<UserRole, string> = {
  STUDENT: "/student",
  TEACHER: "/teacher",
  PARENT: "/parent",
  ADMIN: "/admin",
  SUPER_ADMIN: "/admin",
  CONTENT_MANAGER: "/admin",
  SUPPORT_AGENT: "/admin",
};

export function roleHomePath(role: UserRole): string {
  return ROLE_HOME[role];
}
