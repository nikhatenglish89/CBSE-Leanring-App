import { Link } from "react-router-dom";

import { BRAND } from "../../config/brand";

const FOOTER_LINKS = [
  { label: "Study Materials", to: "/#study-materials" },
  { label: "Study Videos", to: "/#study-videos" },
  { label: "Teacher Interaction", to: "/#teacher-interaction" },
  { label: "Practice Tests", to: "/#practice-tests" },
];

export function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-white">
      <div className="h-1 bg-gradient-to-r from-brand-600 via-violet-600 to-accent-500" />
      <div className="page-shell flex flex-col gap-10 py-12 sm:flex-row sm:justify-between">
        <div className="max-w-xs">
          <span className="flex items-center gap-2 font-display text-base font-bold tracking-tight text-slate-900">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-gradient-to-br from-brand-500 to-brand-700 text-xs font-extrabold text-white">
              E
            </span>
            {BRAND.shortName}
          </span>
          <p className="mt-3 text-sm text-slate-500">
            A CBSE-focused learning platform for classes VI&ndash;XII &mdash; built for Indian students,
            teachers, and parents.
          </p>
        </div>

        <div className="flex flex-wrap gap-x-12 gap-y-6">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Explore</p>
            <ul className="mt-3 flex flex-col gap-2">
              {FOOTER_LINKS.map((link) => (
                <li key={link.to}>
                  <Link to={link.to} className="text-sm text-slate-600 hover:text-brand-600">
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Account</p>
            <ul className="mt-3 flex flex-col gap-2">
              <li>
                <Link to="/login" className="text-sm text-slate-600 hover:text-brand-600">
                  Log in
                </Link>
              </li>
              <li>
                <Link to="/register" className="text-sm text-slate-600 hover:text-brand-600">
                  Sign up free
                </Link>
              </li>
            </ul>
          </div>
        </div>
      </div>
      <div className="border-t border-slate-100">
        <div className="page-shell flex flex-col items-center justify-between gap-2 py-5 text-xs text-slate-400 sm:flex-row">
          <p>
            &copy; {new Date().getFullYear()} {BRAND.name}. Built for CBSE classes VI&ndash;XII.
          </p>
          <p>Made in India, for Indian students.</p>
        </div>
      </div>
    </footer>
  );
}
