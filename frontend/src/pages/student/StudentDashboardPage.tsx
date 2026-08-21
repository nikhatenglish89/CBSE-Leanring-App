import { useState } from "react";

import { CourseCard } from "../../components/courses/CourseCard";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card, CardSkeleton, EmptyState, Select } from "../../components/ui";
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
    <div className="page-shell flex flex-col gap-8 py-10">
      <PageHeader
        eyebrow="Student"
        title={`Welcome back, ${user?.full_name?.split(" ")[0] ?? "there"}`}
        subtitle="Browse published courses and pick up where you left off."
      />

      <Card className="grid gap-4 sm:grid-cols-2">
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

      <div>
        <h2 className="mb-4 text-lg font-semibold text-slate-900">Courses for you</h2>
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
              <CourseCard key={course.id} course={course} to={`/student/courses/${course.id}`} />
            ))}
          </div>
        )}
        {!isLoading && courses?.length === 0 && (
          <EmptyState
            icon="📚"
            title="No courses match these filters"
            description="Try a different class or subject, or check back soon — teachers are adding new courses regularly."
          />
        )}
      </div>
    </div>
  );
}
