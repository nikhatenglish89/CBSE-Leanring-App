import { useState } from "react";
import { Link } from "react-router-dom";

import { Badge, Card, Select, Spinner } from "../../components/ui";
import { useAuth } from "../../hooks/useAuth";
import { useCourses } from "../../hooks/useCourses";
import { useClasses, useSubjects } from "../../hooks/useCurriculum";

export function StudentDashboardPage() {
  const { user } = useAuth();
  const { data: classes } = useClasses();
  const [classId, setClassId] = useState("");
  const { data: subjects } = useSubjects(classId || undefined);
  const [subjectId, setSubjectId] = useState("");
  const { data: courses, isLoading } = useCourses({
    classId: classId || undefined,
    subjectId: subjectId || undefined,
  });

  return (
    <div className="mx-auto max-w-4xl px-4 py-12">
      <h1 className="text-2xl font-semibold text-slate-900">Welcome, {user?.full_name}</h1>
      <p className="mt-1 text-sm text-slate-600">Browse published courses below.</p>

      <Card className="mt-6 grid gap-4 sm:grid-cols-2">
        <Select
          label="Class"
          value={classId}
          onChange={(event) => {
            setClassId(event.target.value);
            setSubjectId("");
          }}
        >
          <option value="">All classes</option>
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
          <option value="">All subjects</option>
          {subjects?.map((subject) => (
            <option key={subject.id} value={subject.id}>
              {subject.name}
            </option>
          ))}
        </Select>
      </Card>

      <div className="mt-8">
        {isLoading && <Spinner label="Loading courses" />}
        <div className="flex flex-col gap-3">
          {courses?.map((course) => (
            <Link key={course.id} to={`/student/courses/${course.id}`}>
              <Card className="flex items-center justify-between hover:border-brand-300">
                <div>
                  <p className="font-medium text-slate-900">{course.title}</p>
                  <p className="text-sm text-slate-500">{course.description || "No description yet."}</p>
                </div>
                <Badge tone={course.access_type === "FREE" ? "success" : "brand"}>{course.access_type}</Badge>
              </Card>
            </Link>
          ))}
          {courses?.length === 0 && (
            <p className="text-sm text-slate-500">No published courses match these filters yet.</p>
          )}
        </div>
      </div>
    </div>
  );
}
