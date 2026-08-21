import { Link, useParams } from "react-router-dom";

import { Badge, CardSkeleton, EmptyState } from "../../components/ui";
import { useCourse, useCourseSections } from "../../hooks/useCourses";
import { StudentSectionCard } from "./StudentSectionCard";

export function StudentCourseDetailPage() {
  const { courseId } = useParams<{ courseId: string }>();
  const { data: course, isLoading } = useCourse(courseId);
  const { data: sections } = useCourseSections(courseId);

  if (isLoading || !course) {
    return (
      <div className="page-shell flex flex-col gap-4 py-10">
        <CardSkeleton />
        <CardSkeleton />
      </div>
    );
  }

  return (
    <div className="page-shell flex flex-col gap-8 py-10">
      <Link to="/student" className="text-sm font-medium text-brand-600 hover:underline">
        &larr; Back to courses
      </Link>

      <div className="rounded-2xl border border-slate-200 bg-gradient-to-br from-brand-50 to-white p-6 sm:p-8">
        <div className="flex flex-wrap items-center gap-2">
          <Badge tone={course.access_type === "FREE" ? "success" : "brand"}>{course.access_type}</Badge>
        </div>
        <h1 className="mt-3 text-2xl font-bold text-slate-900 sm:text-3xl">{course.title}</h1>
        <p className="mt-2 max-w-2xl text-slate-600">
          {course.description || "No description provided yet."}
        </p>
      </div>

      <div>
        <h2 className="mb-4 text-lg font-semibold text-slate-900">Syllabus</h2>
        <div className="flex flex-col gap-3">
          {sections?.map((section, index) => (
            <StudentSectionCard key={section.id} section={section} index={index} />
          ))}
          {sections?.length === 0 && (
            <EmptyState icon="🗂️" title="No sections yet" description="The teacher hasn't added content to this course yet." />
          )}
        </div>
      </div>
    </div>
  );
}
