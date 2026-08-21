import { Link } from "react-router-dom";

import { Button } from "../components/ui";
import { BRAND } from "../config/brand";

const FEATURES = [
  {
    icon: "🎥",
    title: "Video Lessons",
    description: "Structured, chapter-wise video lessons mapped to the CBSE syllabus for classes VI–XII.",
  },
  {
    icon: "🧑‍🏫",
    title: "Live Classes",
    description: "Join real-time classes with teachers, ask questions, and never fall behind.",
  },
  {
    icon: "📝",
    title: "Practice Tests",
    description: "Chapter and full-syllabus tests with instant scoring to track real progress.",
  },
];

const CLASS_RANGE = ["VI", "VII", "VIII", "IX", "X", "XI", "XII"];

export function HomePage() {
  return (
    <div>
      <section className="relative overflow-hidden bg-gradient-to-br from-brand-700 via-brand-600 to-brand-800">
        <div
          className="bg-hero-grid absolute inset-0 opacity-40 [background-size:22px_22px]"
          aria-hidden="true"
        />
        <div className="page-shell relative flex flex-col items-center gap-6 py-24 text-center sm:py-32">
          <span className="rounded-full bg-white/10 px-4 py-1.5 text-sm font-medium text-brand-50 ring-1 ring-inset ring-white/20">
            CBSE &middot; Classes VI&ndash;XII
          </span>
          <h1 className="max-w-3xl text-4xl font-extrabold tracking-tight text-white sm:text-5xl">
            {BRAND.tagline}
          </h1>
          <p className="max-w-xl text-lg text-brand-50/90">
            {BRAND.name} is a CBSE-focused learning platform &mdash; video lessons, study material,
            live classes, and practice tests, all in one place.
          </p>
          <div className="mt-2 flex flex-col gap-3 sm:flex-row">
            <Link to="/register">
              <Button className="w-full !bg-white !text-brand-700 hover:!bg-brand-50 sm:w-auto">
                Start learning free
              </Button>
            </Link>
            <Link to="/login">
              <Button
                variant="ghost"
                className="w-full !text-white ring-1 ring-inset ring-white/30 hover:!bg-white/10 sm:w-auto"
              >
                I already have an account
              </Button>
            </Link>
          </div>
          <div className="mt-4 flex flex-wrap items-center justify-center gap-2">
            {CLASS_RANGE.map((label) => (
              <span
                key={label}
                className="flex h-9 w-9 items-center justify-center rounded-full bg-white/10 text-sm font-semibold text-white ring-1 ring-inset ring-white/20"
              >
                {label}
              </span>
            ))}
          </div>
        </div>
      </section>

      <section className="page-shell py-16 sm:py-24">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
            Everything you need to excel at CBSE
          </h2>
          <p className="mt-3 text-slate-600">
            One platform for students, teachers, and parents &mdash; built around the real CBSE
            curriculum.
          </p>
        </div>
        <div className="mt-12 grid gap-6 sm:grid-cols-3">
          {FEATURES.map((feature) => (
            <div
              key={feature.title}
              className="rounded-xl border border-slate-200 bg-white p-6 text-center shadow-card"
            >
              <span className="flex h-12 w-12 items-center justify-center rounded-full bg-brand-50 text-2xl">
                {feature.icon}
              </span>
              <h3 className="mt-4 font-semibold text-slate-900">{feature.title}</h3>
              <p className="mt-2 text-sm text-slate-600">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="border-t border-slate-200 bg-white">
        <div className="page-shell flex flex-col items-center gap-4 py-16 text-center">
          <h2 className="text-2xl font-bold text-slate-900">Ready to get started?</h2>
          <p className="max-w-md text-slate-600">
            Create a free account as a student, teacher, or parent &mdash; it only takes a minute.
          </p>
          <Link to="/register">
            <Button>Create your account</Button>
          </Link>
        </div>
      </section>
    </div>
  );
}
