import { useState } from "react";
import { Link, useLocation } from "react-router-dom";

import logoMark from "../../assets/edusphere-mark.png";
import { useAuth } from "../../hooks/useAuth";
import { roleHomePath } from "../../lib/roleRoutes";
import type { UserRole } from "../../types/auth";

const ROLE_LABEL: Record<UserRole, string> = {
  STUDENT: "Student",
  TEACHER: "Teacher",
  PARENT: "Parent",
  ADMIN: "Admin",
  SUPER_ADMIN: "Super Admin",
  CONTENT_MANAGER: "Content Manager",
  SUPPORT_AGENT: "Support Agent",
};

const FEATURE_NAV_LINKS = [
  { label: "Study Materials", to: "/study-materials" },
  { label: "Study Videos", to: "/study-videos" },
  { label: "Teacher Interaction", to: "/teacher-interaction" },
  { label: "Practice Tests", to: "/practice-tests" },
  { label: "Feedback", to: "/feedback" },
];

// Only shown to signed-in Students/Teachers — messaging and groups always
// involve a student-teacher pairing, so both are meaningless for anyone else.
const STUDENT_TEACHER_ROLES = new Set<UserRole>(["STUDENT", "TEACHER"]);

function initials(name: string): string {
  const parts = name.trim().split(/\s+/);
  const first = parts[0]?.[0] ?? "";
  const last = parts.length > 1 ? parts[parts.length - 1]?.[0] ?? "" : "";
  return (first + last).toUpperCase();
}

// A link is "current" on an exact match or on any of its sub-routes (e.g.
// /groups/:id should still highlight the Groups link).
function isNavActive(pathname: string, to: string): boolean {
  return pathname === to || pathname.startsWith(`${to}/`);
}

// Active item gets the same solid-white pill treatment as the header's CTA
// capsule, so "where am I" reads at a glance against the dark bar.
function navLinkClass(active: boolean): string {
  return `rounded-full px-3 py-2 text-sm font-medium whitespace-nowrap transition-colors ${
    active ? "bg-white text-slate-900" : "text-slate-300 hover:bg-white/10 hover:text-white"
  }`;
}

function mobileNavLinkClass(active: boolean): string {
  return `block rounded-full px-4 py-2.5 text-sm font-medium transition-colors ${
    active ? "bg-white text-slate-900" : "text-slate-300 hover:bg-white/10 hover:text-white"
  }`;
}

function Logo({ homePath, onClick }: { homePath: string; onClick: () => void }) {
  return (
    <Link to={homePath} className="flex shrink-0 items-center" onClick={onClick}>
      <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-white">
        <img src={logoMark} alt="EduSphere" className="h-7 w-7 object-contain" />
      </span>
    </Link>
  );
}

export function Header() {
  const { user, isAuthenticated, logout } = useAuth();
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);

  const homePath = isAuthenticated && user ? roleHomePath(user.role) : "/";

  const authedNavLinks = user
    ? [
        { label: "Dashboard", to: homePath },
        ...FEATURE_NAV_LINKS,
        ...(STUDENT_TEACHER_ROLES.has(user.role)
          ? [
              { label: "Messages", to: "/messages" },
              { label: "Groups", to: "/groups" },
            ]
          : []),
      ]
    : [];

  return (
    <header className="sticky top-0 z-40 bg-slate-50/90 backdrop-blur">
      <div className="mx-auto w-full max-w-7xl px-4 py-3 sm:px-6 sm:py-4 lg:px-8">
        <div className="flex h-16 items-center justify-between gap-1 rounded-full bg-slate-900 pl-2 pr-2 shadow-lg shadow-slate-900/15 sm:pr-3">
          <Logo homePath={homePath} onClick={() => setMenuOpen(false)} />

          {isAuthenticated && user ? (
            <>
              <nav className="hidden items-center gap-0.5 xl:flex">
                {authedNavLinks.map((link) => (
                  <Link key={link.to} to={link.to} className={navLinkClass(isNavActive(location.pathname, link.to))}>
                    {link.label}
                  </Link>
                ))}
              </nav>

              <div className="hidden items-center gap-1 xl:flex">
                <Link
                  to="/profile"
                  title={`${user.full_name} · ${ROLE_LABEL[user.role]}`}
                  className="flex items-center gap-2 rounded-full bg-white py-1.5 pl-1.5 pr-3 transition-opacity hover:opacity-90"
                >
                  <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-brand-100 text-xs font-semibold text-brand-700">
                    {initials(user.full_name)}
                  </span>
                  <span className="whitespace-nowrap text-sm font-medium text-slate-900">
                    {user.full_name.split(" ")[0]}
                  </span>
                </Link>
                <button
                  type="button"
                  onClick={logout}
                  className="rounded-full px-3 py-2 text-sm font-medium text-slate-300 transition-colors hover:bg-white/10 hover:text-white"
                >
                  Log out
                </button>
              </div>

              <button
                type="button"
                className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-slate-300 transition-colors hover:bg-white/10 hover:text-white xl:hidden"
                aria-label="Toggle menu"
                onClick={() => setMenuOpen((open) => !open)}
              >
                <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth={2}>
                  {menuOpen ? (
                    <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                  ) : (
                    <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
                  )}
                </svg>
              </button>
            </>
          ) : (
            <>
              <nav className="hidden items-center gap-0.5 lg:flex">
                {FEATURE_NAV_LINKS.map((link) => (
                  <Link key={link.to} to={link.to} className={navLinkClass(isNavActive(location.pathname, link.to))}>
                    {link.label}
                  </Link>
                ))}
              </nav>
              <div className="flex shrink-0 items-center gap-1">
                <Link
                  to="/login"
                  className="rounded-full px-4 py-2 text-sm font-medium text-slate-300 transition-colors hover:bg-white/10 hover:text-white"
                >
                  Log in
                </Link>
                <Link
                  to="/register"
                  className="rounded-full bg-white px-5 py-2 text-sm font-semibold text-slate-900 transition-opacity hover:opacity-90"
                >
                  Sign up free
                </Link>
              </div>
            </>
          )}
        </div>
      </div>

      {isAuthenticated && user && menuOpen && (
        <div className="mx-auto -mt-1 w-full max-w-7xl px-4 pb-4 sm:px-6 lg:px-8 xl:hidden">
          <div className="flex flex-col gap-0.5 rounded-3xl bg-slate-900 p-3 shadow-lg shadow-slate-900/15">
            <div className="mb-2 flex items-center gap-2 px-2 pt-1">
              <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-brand-100 text-xs font-semibold text-brand-700">
                {initials(user.full_name)}
              </span>
              <span className="text-sm">
                <span className="block font-medium text-white">{user.full_name}</span>
                <span className="text-slate-400">{ROLE_LABEL[user.role]}</span>
              </span>
            </div>
            {authedNavLinks.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className={mobileNavLinkClass(isNavActive(location.pathname, link.to))}
                onClick={() => setMenuOpen(false)}
              >
                {link.label}
              </Link>
            ))}
            <Link
              to="/profile"
              className={mobileNavLinkClass(isNavActive(location.pathname, "/profile"))}
              onClick={() => setMenuOpen(false)}
            >
              Edit profile
            </Link>
            <button
              type="button"
              className="mt-1 block w-full rounded-full px-4 py-2.5 text-left text-sm font-medium text-rose-400 transition-colors hover:bg-white/10"
              onClick={() => {
                setMenuOpen(false);
                logout();
              }}
            >
              Log out
            </button>
          </div>
        </div>
      )}
    </header>
  );
}
