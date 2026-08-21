import { useState } from "react";
import { Link } from "react-router-dom";

import { PageHeader } from "../components/layout/PageHeader";
import { Badge, Card, CardSkeleton, EmptyState, Select } from "../components/ui";
import { useBrowseVideos } from "../hooks/useMaterials";
import { useClasses, useSubjects } from "../hooks/useCurriculum";

export function StudyVideosPage() {
  const { data: classes } = useClasses();
  const [classId, setClassId] = useState("");
  const { data: subjects } = useSubjects(classId || undefined);
  const [subjectId, setSubjectId] = useState("");
  const { data: videos, isLoading } = useBrowseVideos({
    classId: classId || undefined,
    subjectId: subjectId || undefined,
  });

  return (
    <div className="page-shell flex flex-col gap-8 py-10">
      <PageHeader
        eyebrow="Study Videos"
        title="Video lessons from your teachers"
        subtitle="Every video attached across the platform — filter by class or subject, then watch it on its lesson page. Teachers and staff also see drafts still in progress, marked below."
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

      {!isLoading && videos && videos.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {videos.map((video) => (
            <Link
              key={video.id}
              to={`/lessons/${video.lesson_id}`}
              className="group flex flex-col gap-3 rounded-xl border border-slate-200 bg-white p-5 shadow-card transition-all hover:-translate-y-0.5 hover:border-brand-300 hover:shadow-lift"
            >
              <div className="flex aspect-video items-center justify-center rounded-lg bg-slate-900">
                <span className="flex h-10 w-10 items-center justify-center rounded-full bg-white/90 text-lg text-brand-700">
                  &#9654;
                </span>
              </div>
              <div>
                <p className="truncate font-medium text-slate-900 group-hover:text-brand-700">
                  {video.title || video.lesson_title}
                </p>
                <p className="truncate text-xs text-slate-500">
                  {video.course_title} &middot; {video.lesson_title}
                </p>
              </div>
              <div className="flex flex-wrap items-center gap-2">
                <Badge tone="neutral" className="w-fit">
                  {video.provider}
                </Badge>
                {video.course_status === "DRAFT" && <Badge tone="warning">Draft</Badge>}
              </div>
            </Link>
          ))}
        </div>
      )}

      {!isLoading && videos?.length === 0 && (
        <EmptyState
          icon="🎥"
          title="No study videos match these filters"
          description="Try a different class or subject, or check back soon — teachers are adding new videos regularly."
        />
      )}
    </div>
  );
}
