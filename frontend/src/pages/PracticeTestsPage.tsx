import { useState } from "react";
import { Link } from "react-router-dom";

import { PageHeader } from "../components/layout/PageHeader";
import { Badge, Card, CardSkeleton, EmptyState, Select } from "../components/ui";
import { useBrowsePracticeSets } from "../hooks/usePractice";
import { useClasses, useSubjects } from "../hooks/useCurriculum";

export function PracticeTestsPage() {
  const { data: classes } = useClasses();
  const [classId, setClassId] = useState("");
  const { data: subjects } = useSubjects(classId || undefined);
  const [subjectId, setSubjectId] = useState("");
  const { data: practiceSets, isLoading } = useBrowsePracticeSets({
    classId: classId || undefined,
    subjectId: subjectId || undefined,
  });

  return (
    <div className="page-shell flex flex-col gap-8 py-10">
      <PageHeader
        eyebrow="Practice Tests"
        title="Chapter and full-syllabus tests with instant scoring"
        subtitle="20-question sets for every class and subject. Pick one, answer at your own pace, and see your score with explanations the moment you submit."
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

      {isLoading && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      )}

      {!isLoading && practiceSets && practiceSets.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {practiceSets.map((set) => (
            <Link
              key={set.id}
              to={`/practice-tests/${set.id}`}
              className="group flex flex-col gap-3 rounded-xl border border-slate-200 bg-white p-5 shadow-card transition-all hover:-translate-y-0.5 hover:border-brand-300 hover:shadow-lift"
            >
              <div className="flex items-center justify-between">
                <Badge tone="brand">{set.class_name}</Badge>
                <Badge tone="neutral">{set.question_count} questions</Badge>
              </div>
              <div>
                <p className="font-medium text-slate-900 group-hover:text-brand-700">{set.title}</p>
                <p className="text-xs text-slate-500">{set.subject_name}</p>
              </div>
            </Link>
          ))}
        </div>
      )}

      {!isLoading && practiceSets?.length === 0 && (
        <EmptyState
          icon="📝"
          title="No practice sets match these filters"
          description="Try a different class or subject."
        />
      )}
    </div>
  );
}
