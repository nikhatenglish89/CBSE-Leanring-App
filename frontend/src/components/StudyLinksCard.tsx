import { Link } from "react-router-dom";

import { Card } from "./ui";

export function StudyLinksCard() {
  return (
    <Card>
      <h2 className="text-lg font-semibold text-slate-900">Explore</h2>
      <p className="mt-1 text-sm text-slate-500">
        Browse everything teachers have published across the platform.
      </p>
      <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Link
          to="/study-materials"
          className="group flex items-center gap-3 rounded-xl border border-slate-200 p-4 transition-all hover:-translate-y-0.5 hover:border-brand-300 hover:shadow-card"
        >
          <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-accent-100 text-xl text-accent-600">
            📚
          </span>
          <div>
            <p className="font-medium text-slate-900 group-hover:text-brand-700">Study Materials</p>
            <p className="text-xs text-slate-500">Notes, PDFs, and documents</p>
          </div>
        </Link>
        <Link
          to="/study-videos"
          className="group flex items-center gap-3 rounded-xl border border-slate-200 p-4 transition-all hover:-translate-y-0.5 hover:border-brand-300 hover:shadow-card"
        >
          <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-50 text-xl text-brand-600">
            🎥
          </span>
          <div>
            <p className="font-medium text-slate-900 group-hover:text-brand-700">Study Videos</p>
            <p className="text-xs text-slate-500">Video lessons by class &amp; subject</p>
          </div>
        </Link>
        <Link
          to="/practice-tests"
          className="group flex items-center gap-3 rounded-xl border border-slate-200 p-4 transition-all hover:-translate-y-0.5 hover:border-brand-300 hover:shadow-card"
        >
          <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-violet-50 text-xl text-violet-600">
            📝
          </span>
          <div>
            <p className="font-medium text-slate-900 group-hover:text-brand-700">Practice Tests</p>
            <p className="text-xs text-slate-500">20-question sets, instant scoring</p>
          </div>
        </Link>
        <Link
          to="/teacher-interaction"
          className="group flex items-center gap-3 rounded-xl border border-slate-200 p-4 transition-all hover:-translate-y-0.5 hover:border-brand-300 hover:shadow-card"
        >
          <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-violet-50 text-xl text-violet-600">
            🧑‍🏫
          </span>
          <div>
            <p className="font-medium text-slate-900 group-hover:text-brand-700">Teacher Interaction</p>
            <p className="text-xs text-slate-500">Ask questions, join live classes</p>
          </div>
        </Link>
      </div>
    </Card>
  );
}
