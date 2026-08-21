import { useParams } from "react-router-dom";

import { Card, Spinner } from "../../components/ui";
import { useCourse, useCourseSections } from "../../hooks/useCourses";
import { StudentSectionCard } from "./StudentSectionCard";

export function StudentCourseDetailPage() {
  const { courseId } = useParams<{ courseId: string }>();
  const { data: course, isLoading } = useCourse(courseId);
  const { data: sections } = useCourseSections(courseId);

  if (isLoading || !course) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-12">
        <Spinner label="Loading course" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-12">
      <h1 className="text-2xl font-semibold text-slate-900">{course.title}</h1>
      <p className="mt-1 text-sm text-slate-600">{course.description}</p>

      <div className="mt-8 flex flex-col gap-4">
        {sections?.map((section) => (
          <StudentSectionCard key={section.id} section={section} />
        ))}
        {sections?.length === 0 && (
          <Card>
            <p className="text-sm text-slate-500">No sections yet.</p>
          </Card>
        )}
      </div>
    </div>
  );
}
