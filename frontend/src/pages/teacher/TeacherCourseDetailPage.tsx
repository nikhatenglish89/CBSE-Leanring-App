import { type FormEvent, useState } from "react";
import { useParams } from "react-router-dom";

import { Badge, Button, Card, Input, Spinner, useToast } from "../../components/ui";
import { useCourse, useCourseSections, useCreateSection, useUpdateCourseStatus } from "../../hooks/useCourses";
import { TeacherSectionCard } from "./TeacherSectionCard";

export function TeacherCourseDetailPage() {
  const { courseId } = useParams<{ courseId: string }>();
  const { data: course, isLoading } = useCourse(courseId);
  const { data: sections } = useCourseSections(courseId);
  const createSection = useCreateSection();
  const updateStatus = useUpdateCourseStatus();
  const { showToast } = useToast();
  const [sectionTitle, setSectionTitle] = useState("");

  const onCreateSection = async (event: FormEvent) => {
    event.preventDefault();
    if (!courseId || !sectionTitle.trim()) return;
    try {
      await createSection.mutateAsync({ courseId, title: sectionTitle });
      setSectionTitle("");
    } catch {
      showToast("Could not create the section.", "error");
    }
  };

  const togglePublish = async () => {
    if (!course) return;
    try {
      await updateStatus.mutateAsync({
        courseId: course.id,
        status: course.status === "PUBLISHED" ? "DRAFT" : "PUBLISHED",
      });
      showToast(course.status === "PUBLISHED" ? "Course unpublished." : "Course published.", "success");
    } catch {
      showToast("Could not update the course.", "error");
    }
  };

  if (isLoading || !course) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-12">
        <Spinner label="Loading course" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-12">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">{course.title}</h1>
          <p className="mt-1 text-sm text-slate-600">{course.description}</p>
        </div>
        <div className="flex items-center gap-3">
          <Badge tone={course.status === "PUBLISHED" ? "success" : "warning"}>{course.status}</Badge>
          <Button variant="secondary" onClick={togglePublish} isLoading={updateStatus.isPending}>
            {course.status === "PUBLISHED" ? "Unpublish" : "Publish"}
          </Button>
        </div>
      </div>

      <Card className="mt-6">
        <h2 className="text-lg font-medium text-slate-900">Add a section</h2>
        <form className="mt-4 flex items-end gap-3" onSubmit={onCreateSection}>
          <div className="flex-1">
            <Input
              label="Section title"
              value={sectionTitle}
              onChange={(event) => setSectionTitle(event.target.value)}
            />
          </div>
          <Button type="submit" isLoading={createSection.isPending}>
            Add section
          </Button>
        </form>
      </Card>

      <div className="mt-8 flex flex-col gap-4">
        {sections?.map((section) => (
          <TeacherSectionCard key={section.id} section={section} />
        ))}
        {sections?.length === 0 && (
          <p className="text-sm text-slate-500">No sections yet — add one above to start building the course.</p>
        )}
      </div>
    </div>
  );
}
