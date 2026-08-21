import { type FormEvent, useState } from "react";

import { CourseCard } from "../../components/courses/CourseCard";
import { PageHeader } from "../../components/layout/PageHeader";
import { Button, Card, CardSkeleton, EmptyState, Input, Select, useToast } from "../../components/ui";
import { useAuth } from "../../hooks/useAuth";
import { useCreateCourse, useCourses } from "../../hooks/useCourses";
import { useClasses, useSubjects } from "../../hooks/useCurriculum";

export function TeacherDashboardPage() {
  const { user } = useAuth();
  const { showToast } = useToast();
  const { data: courses, isLoading } = useCourses({ mine: true });
  const { data: classes } = useClasses();
  const [classId, setClassId] = useState("");
  const { data: subjects } = useSubjects(classId || undefined);
  const [subjectId, setSubjectId] = useState("");
  const [title, setTitle] = useState("");
  const createCourse = useCreateCourse();

  const publishedCount = courses?.filter((c) => c.status === "PUBLISHED").length ?? 0;
  const draftCount = courses?.filter((c) => c.status === "DRAFT").length ?? 0;

  const onCreate = async (event: FormEvent) => {
    event.preventDefault();
    if (!classId || !subjectId || !title.trim()) {
      showToast("Pick a class, subject, and title.", "error");
      return;
    }
    try {
      await createCourse.mutateAsync({ class_id: classId, subject_id: subjectId, title });
      setTitle("");
      showToast("Course created as a draft.", "success");
    } catch {
      showToast("Could not create the course.", "error");
    }
  };

  return (
    <div className="page-shell flex flex-col gap-8 py-10">
      <PageHeader
        eyebrow="Teacher"
        title={`Welcome back, ${user?.full_name?.split(" ")[0] ?? "there"}`}
        subtitle="Create and manage the courses you teach."
      />

      <div className="grid gap-4 sm:grid-cols-3">
        <Card className="!p-4">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Total courses</p>
          <p className="mt-1 text-2xl font-bold text-slate-900">{courses?.length ?? "–"}</p>
        </Card>
        <Card className="!p-4">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Published</p>
          <p className="mt-1 text-2xl font-bold text-emerald-600">{publishedCount}</p>
        </Card>
        <Card className="!p-4">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Drafts</p>
          <p className="mt-1 text-2xl font-bold text-amber-600">{draftCount}</p>
        </Card>
      </div>

      <Card>
        <h2 className="text-lg font-semibold text-slate-900">Create a course</h2>
        <p className="mt-1 text-sm text-slate-500">New courses start as a draft — publish when ready.</p>
        <form className="mt-4 grid gap-4 sm:grid-cols-2" onSubmit={onCreate}>
          <Select
            label="Class"
            value={classId}
            onChange={(event) => {
              setClassId(event.target.value);
              setSubjectId("");
            }}
          >
            <option value="">Select a class</option>
            {classes?.map((klass) => (
              <option key={klass.id} value={klass.id}>
                {klass.name}
              </option>
            ))}
          </Select>
          <Select
            label="Subject"
            value={subjectId}
            onChange={(event) => setSubjectId(event.target.value)}
            disabled={!classId}
          >
            <option value="">Select a subject</option>
            {subjects?.map((subject) => (
              <option key={subject.id} value={subject.id}>
                {subject.name}
              </option>
            ))}
          </Select>
          <div className="sm:col-span-2">
            <Input label="Title" value={title} onChange={(event) => setTitle(event.target.value)} />
          </div>
          <div className="sm:col-span-2">
            <Button type="submit" isLoading={createCourse.isPending}>
              Create course
            </Button>
          </div>
        </form>
      </Card>

      <div>
        <h2 className="mb-4 text-lg font-semibold text-slate-900">Your courses</h2>
        {isLoading && (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <CardSkeleton key={i} />
            ))}
          </div>
        )}
        {!isLoading && courses && courses.length > 0 && (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {courses.map((course) => (
              <CourseCard key={course.id} course={course} to={`/teacher/courses/${course.id}`} />
            ))}
          </div>
        )}
        {!isLoading && courses?.length === 0 && (
          <EmptyState icon="✏️" title="No courses yet" description="Create your first course above to get started." />
        )}
      </div>
    </div>
  );
}
