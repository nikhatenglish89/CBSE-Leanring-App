import { BRAND } from "../../config/brand";

export function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-white">
      <div className="page-shell flex flex-col items-center justify-between gap-3 py-8 text-sm text-slate-500 sm:flex-row">
        <p>
          &copy; {new Date().getFullYear()} {BRAND.name}. Built for CBSE classes VI&ndash;XII.
        </p>
        <p className="text-slate-400">Made in India, for Indian students.</p>
      </div>
    </footer>
  );
}
