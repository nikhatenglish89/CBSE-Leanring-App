import axios from "axios";
import { type FormEvent, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { Badge, Button, Card, CardSkeleton, EmptyState, Input, useToast } from "../../components/ui";
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
    } catch (error) {
      // Surfaces the server's specific reason when it has one (e.g. "Your
      // account must be verified by an admin before you can publish
      // courses.") instead of a generic message that would leave the
      // teacher guessing why.
      const message = axios.isAxiosError(error) ? error.response?.data?.error?.message : undefined;
      showToast(message ?? "Could not update the course.", "error");
    }
  };

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
      <Link to="/teacher" className="text-sm font-medium text-brand-600 hover:underline">
        &larr; Back to your courses
      </Link>

      <div className="flex flex-col gap-4 rounded-2xl border border-slate-200 bg-gradient-to-br from-brand-50 to-white p-6 sm:flex-row sm:items-start sm:justify-between sm:p-8">
        <div>
          <Badge tone={course.status === "PUBLISHED" ? "success" : "warning"}>{course.status}</Badge>
          <h1 className="mt-3 text-2xl font-bold text-slate-900 sm:text-3xl">{course.title}</h1>
          <p className="mt-2 max-w-2xl text-slate-600">
            {course.description || "No description provided yet."}
          </p>
        </div>
        <Button
          variant={course.status === "PUBLISHED" ? "secondary" : "primary"}
          onClick={togglePublish}
          isLoading={updateStatus.isPending}
          className="shrink-0"
        >
          {course.status === "PUBLISHED" ? "Unpublish" : "Publish course"}
        </Button>
      </div>

      <Card>
        <h2 className="text-lg font-semibold text-slate-900">Add a section</h2>
        <p className="mt-1 text-sm text-slate-500">Sections organize lessons into a syllabus students can follow.</p>
        <form className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-end" onSubmit={onCreateSection}>
          <div className="flex-1">
            <Input
              label="Section title"
              placeholder="e.g. Chapter 1 — Real Numbers"
              value={sectionTitle}
              onChange={(event) => setSectionTitle(event.target.value)}
            />
          </div>
          <Button type="submit" isLoading={createSection.isPending}>
            Add section
          </Button>
        </form>
      </Card>

      <div>
        <h2 className="mb-4 text-lg font-semibold text-slate-900">Course content</h2>
        <div className="flex flex-col gap-4">
          {sections?.map((section, index) => (
            <TeacherSectionCard key={section.id} section={section} index={index} />
          ))}
          {sections?.length === 0 && (
            <EmptyState icon="🗂️" title="No sections yet" description="Add one above to start building the course." />
          )}
        </div>
      </div>
    </div>
  );
}
