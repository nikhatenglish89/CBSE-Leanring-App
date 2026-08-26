import { useEffect } from "react";
import { Link, useLocation } from "react-router-dom";

import { HomeBannerSection } from "../components/home/HomeBannerSection";
import { Badge, Button } from "../components/ui";
import { BRAND } from "../config/brand";

type Tone = "brand" | "accent" | "violet" | "rose";

const TONE_ICON_CLASSES: Record<Tone, string> = {
  brand: "bg-brand-50 text-brand-600",
  accent: "bg-accent-100 text-accent-600",
  violet: "bg-violet-100 text-violet-600",
  rose: "bg-rose-100 text-rose-600",
};

export const HOME_FEATURES: {
  id: string;
  to: string;
  icon: string;
  title: string;
  description: string;
  tone: Tone;
  comingSoon: boolean;
}[] = [
  {
    id: "study-materials",
    to: "/study-materials",
    icon: "📚",
    title: "Study Materials",
    description: "Notes, PDFs, and documents your teachers upload — browse by class and subject.",
    tone: "accent",
    comingSoon: false,
  },
  {
    id: "study-videos",
    to: "/study-videos",
    icon: "🎥",
    title: "Study Videos",
    description: "Video lessons attached to published courses, mapped to the CBSE syllabus VI–XII.",
    tone: "brand",
    comingSoon: false,
  },
  {
    id: "teacher-interaction",
    to: "/teacher-interaction",
    icon: "🧑‍🏫",
    title: "Teacher Interaction",
    description: "Ask questions, join live classes, and get doubts cleared directly by real teachers.",
    tone: "violet",
    comingSoon: false,
  },
  {
    id: "practice-tests",
    to: "/practice-tests",
    icon: "📝",
    title: "Practice Tests",
    description: "Chapter and full-syllabus tests with instant scoring to track real progress.",
    tone: "rose",
    comingSoon: false,
  },
];

const HOW_IT_WORKS = [
  { step: "1", title: "Create your free account", description: "Sign up as a student, teacher, or parent in under a minute." },
  { step: "2", title: "Pick your class & subjects", description: "Tell us your CBSE class so we can tailor what you see." },
  { step: "3", title: "Start learning", description: "Browse courses your teachers publish, chapter by chapter." },
];

const CLASS_RANGE = ["VI", "VII", "VIII", "IX", "X", "XI", "XII"];

/** Small abstract illustration: a stack of course/lesson cards, kept as
 * inline SVG so the hero has real visual weight without an image asset. */
function HeroIllustration() {
  return (
    <svg viewBox="0 0 420 380" className="w-full max-w-md" aria-hidden="true">
      <defs>
        <linearGradient id="cardA" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#ffffff" stopOpacity="0.95" />
          <stop offset="100%" stopColor="#eef7ff" stopOpacity="0.9" />
        </linearGradient>
      </defs>

      <rect x="18" y="150" width="220" height="150" rx="20" fill="#ffffff" opacity="0.16" transform="rotate(-8 128 225)" />
      <rect x="60" y="40" width="240" height="160" rx="20" fill="#ffffff" opacity="0.22" transform="rotate(6 180 120)" />

      <rect x="60" y="90" width="300" height="210" rx="22" fill="url(#cardA)" />
      <rect x="60" y="90" width="300" height="72" rx="22" fill="#1a6ff5" />
      <circle cx="96" cy="126" r="18" fill="#ffffff" />
      <path d="M91 118l14 8-14 8z" fill="#1558e0" />
      <rect x="128" y="114" width="150" height="10" rx="5" fill="#ffffff" opacity="0.9" />
      <rect x="128" y="132" width="100" height="8" rx="4" fill="#ffffff" opacity="0.6" />

      <rect x="84" y="182" width="252" height="12" rx="6" fill="#dce8fb" />
      <rect x="84" y="206" width="200" height="12" rx="6" fill="#dce8fb" />
      <rect x="84" y="230" width="220" height="12" rx="6" fill="#dce8fb" />

      <rect x="84" y="258" width="90" height="26" rx="13" fill="#f97316" />
      <text x="129" y="275" textAnchor="middle" fontSize="12" fontWeight="700" fill="#ffffff" fontFamily="Inter, sans-serif">
        Chapter 4
      </text>

      <g transform="translate(300 40)">
        <circle cx="30" cy="30" r="30" fill="#22c55e" />
        <path d="M18 30l8 8 16-16" stroke="#ffffff" strokeWidth="4" fill="none" strokeLinecap="round" strokeLinejoin="round" />
      </g>

      <g transform="translate(10 300)">
        <rect width="120" height="46" rx="23" fill="#ffffff" />
        <circle cx="26" cy="23" r="12" fill="#8b5cf6" />
        <rect x="46" y="14" width="60" height="8" rx="4" fill="#cbd5f5" />
        <rect x="46" y="26" width="40" height="7" rx="3.5" fill="#e2e8f0" />
      </g>
    </svg>
  );
}

export function HomePage() {
  const { hash } = useLocation();

  useEffect(() => {
    if (!hash) return;
    const target = document.querySelector(hash);
    target?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, [hash]);

  return (
    <div>
      <section className="relative overflow-hidden bg-gradient-to-br from-brand-700 via-brand-600 to-violet-700">
        <div
          className="bg-hero-grid absolute inset-0 opacity-40 [background-size:22px_22px]"
          aria-hidden="true"
        />
        <div
          className="pointer-events-none absolute -right-24 -top-24 h-96 w-96 rounded-full bg-accent-400/30 blur-3xl"
          aria-hidden="true"
        />
        <div
          className="pointer-events-none absolute -left-24 bottom-0 h-80 w-80 rounded-full bg-violet-500/30 blur-3xl"
          aria-hidden="true"
        />

        <div className="page-shell relative grid gap-12 py-20 sm:py-28 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
          <div className="flex flex-col items-center gap-6 text-center lg:items-start lg:text-left">
            <span className="rounded-full bg-white/10 px-4 py-1.5 text-sm font-medium text-brand-50 ring-1 ring-inset ring-white/20">
              CBSE &middot; Classes VI&ndash;XII
            </span>
            <h1 className="max-w-xl text-4xl font-extrabold tracking-tight text-white sm:text-5xl">
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
            <div className="mt-4 flex flex-wrap items-center justify-center gap-2 lg:justify-start">
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

          <div className="hidden justify-self-center lg:flex">
            <HeroIllustration />
          </div>
        </div>
      </section>

      <HomeBannerSection />

      <section className="page-shell py-16 sm:py-24">
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-xs font-semibold uppercase tracking-wide text-brand-600">What&rsquo;s on EduSphere</p>
          <h2 className="mt-1 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
            Everything you need to excel at CBSE
          </h2>
          <p className="mt-3 text-slate-600">
            One platform for students, teachers, and parents &mdash; built around the real CBSE
            curriculum.
          </p>
        </div>
        <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {HOME_FEATURES.map((feature) => (
            <Link
              key={feature.id}
              id={feature.id}
              to={feature.to}
              className="hover-lift scroll-mt-24 rounded-2xl border border-slate-200 bg-white p-6 text-center shadow-card"
            >
              <span
                className={`mx-auto flex h-12 w-12 items-center justify-center rounded-2xl text-2xl ${TONE_ICON_CLASSES[feature.tone]}`}
              >
                {feature.icon}
              </span>
              <h3 className="mt-4 font-semibold text-slate-900">{feature.title}</h3>
              <p className="mt-2 text-sm text-slate-600">{feature.description}</p>
              {feature.comingSoon ? (
                <Badge tone="warning" className="mt-4 gap-1">
                  <span className="h-1.5 w-1.5 rounded-full bg-amber-500" /> Coming soon
                </Badge>
              ) : (
                <span className="mt-4 inline-block text-sm font-medium text-brand-600">
                  Browse now &rarr;
                </span>
              )}
            </Link>
          ))}
        </div>
      </section>

      <section className="border-t border-slate-200 bg-white py-16 sm:py-24">
        <div className="page-shell">
          <div className="mx-auto max-w-2xl text-center">
            <p className="text-xs font-semibold uppercase tracking-wide text-brand-600">Getting started</p>
            <h2 className="mt-1 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
              Up and running in three steps
            </h2>
          </div>
          <div className="relative mt-12 grid gap-10 sm:grid-cols-3">
            <div
              className="pointer-events-none absolute left-0 right-0 top-6 hidden h-px bg-slate-200 sm:block"
              aria-hidden="true"
            />
            {HOW_IT_WORKS.map((item) => (
              <div key={item.step} className="relative flex flex-col items-center gap-3 text-center">
                <span className="flex h-12 w-12 items-center justify-center rounded-full bg-brand-600 font-display text-lg font-bold text-white shadow-soft">
                  {item.step}
                </span>
                <h3 className="font-semibold text-slate-900">{item.title}</h3>
                <p className="max-w-xs text-sm text-slate-600">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="relative overflow-hidden bg-gradient-to-br from-brand-700 via-brand-600 to-violet-700">
        <div
          className="bg-hero-grid absolute inset-0 opacity-30 [background-size:22px_22px]"
          aria-hidden="true"
        />
        <div className="page-shell relative flex flex-col items-center gap-4 py-16 text-center">
          <h2 className="text-2xl font-bold text-white sm:text-3xl">Ready to get started?</h2>
          <p className="max-w-md text-brand-50/90">
            Create a free account as a student, teacher, or parent &mdash; it only takes a minute.
          </p>
          <Link to="/register">
            <Button className="!bg-white !text-brand-700 hover:!bg-brand-50">Create your account</Button>
          </Link>
        </div>
      </section>
    </div>
  );
}
