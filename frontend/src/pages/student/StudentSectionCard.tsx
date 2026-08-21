import { Badge } from "../../components/ui";
import { useSectionLessons } from "../../hooks/useCourses";
import type { CourseSectionOut, LessonContentType } from "../../types/curriculum";

const CONTENT_ICON: Record<LessonContentType, string> = {
  TEXT: "📄",
  VIDEO: "🎥",
  PDF: "📎",
};

export function StudentSectionCard({ section, index }: { section: CourseSectionOut; index: number }) {
  const { data: lessons } = useSectionLessons(section.id);

  return (
    <details className="group rounded-xl border border-slate-200 bg-white shadow-card open:shadow-soft" open={index === 0}>
      <summary className="flex cursor-pointer list-none items-center justify-between gap-3 px-5 py-4 marker:content-none">
        <div className="flex items-center gap-3">
          <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-brand-50 text-xs font-semibold text-brand-700">
            {index + 1}
          </span>
          <h3 className="font-semibold text-slate-900">{section.title}</h3>
        </div>
        <span className="flex items-center gap-2 text-sm text-slate-500">
          {lessons?.length ?? 0} lesson{lessons?.length === 1 ? "" : "s"}
          <svg
            viewBox="0 0 24 24"
            className="h-4 w-4 shrink-0 transition-transform group-open:rotate-180"
            fill="none"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 9l6 6 6-6" />
          </svg>
        </span>
      </summary>
      <div className="border-t border-slate-100 px-5 pb-4 pt-2">
        <ul className="flex flex-col divide-y divide-slate-100">
          {lessons?.map((lesson) => (
            <li key={lesson.id} className="flex items-center gap-3 py-2.5 text-sm">
              <span className="text-base">{CONTENT_ICON[lesson.content_type]}</span>
              <span className="flex-1 text-slate-800">{lesson.title}</span>
              <Badge tone="neutral">{lesson.content_type}</Badge>
            </li>
          ))}
          {lessons?.length === 0 && <li className="py-2.5 text-sm text-slate-500">No lessons yet.</li>}
        </ul>
      </div>
    </details>
  );
}
