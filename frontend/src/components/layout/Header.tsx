import { useState } from "react";
import { Link, useLocation } from "react-router-dom";

import logoMark from "../../assets/edusphere-mark.png";
import { BRAND } from "../../config/brand";
import { useAuth } from "../../hooks/useAuth";
import { roleHomePath } from "../../lib/roleRoutes";
import type { UserRole } from "../../types/auth";
import { Button } from "../ui";

const ROLE_LABEL: Record<UserRole, string> = {
  STUDENT: "Student",
  TEACHER: "Teacher",
  PARENT: "Parent",
  ADMIN: "Admin",
  SUPER_ADMIN: "Super Admin",
  CONTENT_MANAGER: "Content Manager",
  SUPPORT_AGENT: "Support Agent",
};

const PUBLIC_NAV_LINKS = [
  { label: "Study Materials", to: "/#study-materials" },
  { label: "Study Videos", to: "/#study-videos" },
  { label: "Teacher Interaction", to: "/#teacher-interaction" },
  { label: "Practice Tests", to: "/#practice-tests" },
];

function initials(name: string): string {
  const parts = name.trim().split(/\s+/);
  const first = parts[0]?.[0] ?? "";
  const last = parts.length > 1 ? parts[parts.length - 1]?.[0] ?? "" : "";
  return (first + last).toUpperCase();
}

function Logo() {
  return (
    <span className="flex items-center gap-2 font-display text-lg font-bold tracking-tight text-slate-900">
      <img src={logoMark} alt="" className="h-9 w-9 shrink-0 rounded-lg object-contain" />
      {BRAND.shortName}
    </span>
  );
}

export function Header() {
  const { user, isAuthenticated, logout } = useAuth();
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);

  const homePath = isAuthenticated && user ? roleHomePath(user.role) : "/";
  const isActiveHome = location.pathname === homePath;

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/85 backdrop-blur">
      <div className="page-shell flex h-16 items-center justify-between">
        <Link to={homePath} className="shrink-0" onClick={() => setMenuOpen(false)}>
          <Logo />
        </Link>

        {isAuthenticated && user ? (
          <>
            <nav className="hidden items-center gap-1 md:flex">
              <Link
                to={homePath}
                className={`rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  isActiveHome ? "bg-brand-50 text-brand-700" : "text-slate-600 hover:bg-slate-100"
                }`}
              >
                Dashboard
              </Link>
            </nav>

            <div className="hidden items-center gap-3 md:flex">
              <Link
                to="/profile"
                title="Edit profile"
                className="flex items-center gap-2 rounded-full border border-slate-200 py-1 pl-1 pr-3 transition-colors hover:bg-slate-50"
              >
                <span className="flex h-7 w-7 items-center justify-center rounded-full bg-brand-100 text-xs font-semibold text-brand-700">
                  {initials(user.full_name)}
                </span>
                <span className="text-sm">
                  <span className="font-medium text-slate-900">{user.full_name}</span>{" "}
                  <span className="text-slate-400">&middot;</span>{" "}
                  <span className="text-slate-500">{ROLE_LABEL[user.role]}</span>
                </span>
              </Link>
              <Button variant="ghost" onClick={logout}>
                Log out
              </Button>
            </div>

            <button
              type="button"
              className="inline-flex h-9 w-9 items-center justify-center rounded-lg text-slate-600 hover:bg-slate-100 md:hidden"
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
            <nav className="hidden items-center gap-1 lg:flex">
              {PUBLIC_NAV_LINKS.map((link) => (
                <Link
                  key={link.to}
                  to={link.to}
                  className="rounded-lg px-3 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900"
                >
                  {link.label}
                </Link>
              ))}
            </nav>
            <div className="flex items-center gap-2">
              <Link to="/login">
                <Button variant="ghost">Log in</Button>
              </Link>
              <Link to="/register">
                <Button>Sign up free</Button>
              </Link>
            </div>
          </>
        )}
      </div>

      {isAuthenticated && user && menuOpen && (
        <div className="border-t border-slate-200 bg-white px-4 py-4 md:hidden">
          <div className="mb-3 flex items-center gap-2">
            <span className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-100 text-xs font-semibold text-brand-700">
              {initials(user.full_name)}
            </span>
            <span className="text-sm">
              <span className="block font-medium text-slate-900">{user.full_name}</span>
              <span className="text-slate-500">{ROLE_LABEL[user.role]}</span>
            </span>
          </div>
          <Link
            to={homePath}
            className="block rounded-lg px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100"
            onClick={() => setMenuOpen(false)}
          >
            Dashboard
          </Link>
          <Link
            to="/profile"
            className="block rounded-lg px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100"
            onClick={() => setMenuOpen(false)}
          >
            Edit profile
          </Link>
          <button
            type="button"
            className="mt-1 block w-full rounded-lg px-3 py-2 text-left text-sm font-medium text-red-600 hover:bg-red-50"
            onClick={() => {
              setMenuOpen(false);
              logout();
            }}
          >
            Log out
          </button>
        </div>
      )}
    </header>
  );
}
