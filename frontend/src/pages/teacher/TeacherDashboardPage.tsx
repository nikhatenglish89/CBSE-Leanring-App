import { type FormEvent, useState } from "react";
import { Link } from "react-router-dom";

import { Badge, Button, Card, Input, Select, Spinner, useToast } from "../../components/ui";
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
    <div className="mx-auto max-w-4xl px-4 py-12">
      <h1 className="text-2xl font-semibold text-slate-900">Welcome, {user?.full_name}</h1>
      <p className="mt-1 text-sm text-slate-600">Manage the courses you teach.</p>

      <Card className="mt-6">
        <h2 className="text-lg font-medium text-slate-900">Create a course</h2>
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

      <div className="mt-8">
        <h2 className="text-lg font-medium text-slate-900">Your courses</h2>
        {isLoading && <Spinner className="mt-4" label="Loading courses" />}
        <div className="mt-4 flex flex-col gap-3">
          {courses?.map((course) => (
            <Link key={course.id} to={`/teacher/courses/${course.id}`}>
              <Card className="flex items-center justify-between hover:border-brand-300">
                <div>
                  <p className="font-medium text-slate-900">{course.title}</p>
                  <p className="text-sm text-slate-500">{course.description || "No description yet."}</p>
                </div>
                <Badge tone={course.status === "PUBLISHED" ? "success" : "warning"}>{course.status}</Badge>
              </Card>
            </Link>
          ))}
          {courses?.length === 0 && (
            <p className="text-sm text-slate-500">No courses yet — create your first one above.</p>
          )}
        </div>
      </div>
    </div>
  );
}
