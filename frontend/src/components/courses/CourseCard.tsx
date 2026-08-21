import { Link } from "react-router-dom";

import { Badge } from "../ui";
import type { CourseOut } from "../../types/curriculum";

export function CourseCard({ course, to }: { course: CourseOut; to: string }) {
  return (
    <Link
      to={to}
      className="group flex flex-col gap-3 rounded-xl border border-slate-200 bg-white p-5 shadow-card transition-all hover:-translate-y-0.5 hover:border-brand-300 hover:shadow-soft"
    >
      <div className="flex items-start justify-between gap-3">
        <h3 className="font-semibold text-slate-900 group-hover:text-brand-700">{course.title}</h3>
        <Badge tone={course.access_type === "FREE" ? "success" : "brand"}>{course.access_type}</Badge>
      </div>
      <p className="line-clamp-2 text-sm text-slate-500">
        {course.description || "No description yet."}
      </p>
      <div className="mt-auto flex items-center justify-between pt-2">
        {course.status && (
          <Badge tone={course.status === "PUBLISHED" ? "success" : "warning"}>{course.status}</Badge>
        )}
        <span className="text-sm font-medium text-brand-600 group-hover:underline">View course &rarr;</span>
      </div>
    </Link>
  );
}
