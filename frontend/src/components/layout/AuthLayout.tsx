import type { ReactNode } from "react";

import { BRAND } from "../../config/brand";

const HIGHLIGHTS = [
  "Chapter-wise video lessons for CBSE VI–XII",
  "Live classes with real teachers",
  "Instant-scored practice tests",
];

export function AuthLayout({
  title,
  subtitle,
  children,
  footer,
}: {
  title: string;
  subtitle: string;
  children: ReactNode;
  footer: ReactNode;
}) {
  return (
    <div className="flex min-h-[calc(100vh-4rem)] items-stretch">
      <div className="relative hidden w-1/2 flex-col justify-between overflow-hidden bg-gradient-to-br from-brand-700 via-brand-600 to-brand-800 p-12 text-white lg:flex">
        <div
          className="bg-hero-grid absolute inset-0 opacity-30 [background-size:22px_22px]"
          aria-hidden="true"
        />
        <div className="relative">
          <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-white/15 text-lg font-extrabold">
            E
          </span>
          <h2 className="mt-8 max-w-sm text-3xl font-bold leading-tight">{BRAND.tagline}</h2>
        </div>
        <ul className="relative flex flex-col gap-3 text-sm text-brand-50/90">
          {HIGHLIGHTS.map((item) => (
            <li key={item} className="flex items-center gap-2">
              <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-white/15 text-xs">
                ✓
              </span>
              {item}
            </li>
          ))}
        </ul>
      </div>

      <div className="flex w-full flex-col items-center justify-center px-4 py-16 lg:w-1/2">
        <div className="w-full max-w-sm">
          <h1 className="text-2xl font-bold text-slate-900">{title}</h1>
          <p className="mt-1 text-sm text-slate-600">{subtitle}</p>
          <div className="mt-8">{children}</div>
          <div className="mt-6 text-center text-sm text-slate-600">{footer}</div>
        </div>
      </div>
    </div>
  );
}
