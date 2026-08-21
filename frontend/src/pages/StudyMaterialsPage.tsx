import { useState } from "react";
import { Link } from "react-router-dom";

import { PageHeader } from "../components/layout/PageHeader";
import { Badge, Card, CardSkeleton, EmptyState, Select } from "../components/ui";
import { useBrowseMaterials } from "../hooks/useMaterials";
import { useClasses, useSubjects } from "../hooks/useCurriculum";
import { formatFileSize } from "../lib/format";
import type { MaterialType } from "../types/curriculum";

const MATERIAL_ICON: Record<MaterialType, string> = {
  PDF: "📕",
  DOCUMENT: "📄",
  PRESENTATION: "📊",
  IMAGE: "🖼️",
  TEXT: "📝",
  OTHER: "📎",
};

export function StudyMaterialsPage() {
  const { data: classes } = useClasses();
  const [classId, setClassId] = useState("");
  const { data: subjects } = useSubjects(classId || undefined);
  const [subjectId, setSubjectId] = useState("");
  const { data: materials, isLoading } = useBrowseMaterials({
    classId: classId || undefined,
    subjectId: subjectId || undefined,
  });

  return (
    <div className="page-shell flex flex-col gap-8 py-10">
      <PageHeader
        eyebrow="Study Materials"
        title="Notes, PDFs, and documents from your teachers"
        subtitle="Everything uploaded across the platform — filter by class or subject, then open a file straight from its lesson. Teachers and staff also see drafts still in progress, marked below."
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
        <div className="flex flex-col gap-3">
          {[1, 2, 3].map((i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      )}

      {!isLoading && materials && materials.length > 0 && (
        <ul className="flex flex-col divide-y divide-slate-100 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-card">
          {materials.map((material) => (
            <li key={material.id}>
              <Link
                to={`/lessons/${material.lesson_id}`}
                className="flex flex-wrap items-center gap-3 px-5 py-4 transition-colors hover:bg-slate-50"
              >
                <span className="text-xl">{MATERIAL_ICON[material.material_type]}</span>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-slate-800">{material.file_name}</p>
                  <p className="truncate text-xs text-slate-500">
                    {material.course_title} &middot; {material.lesson_title}
                  </p>
                </div>
                {material.course_status === "DRAFT" && <Badge tone="warning">Draft</Badge>}
                <Badge tone="neutral">{formatFileSize(material.file_size)}</Badge>
              </Link>
            </li>
          ))}
        </ul>
      )}

      {!isLoading && materials?.length === 0 && (
        <EmptyState
          icon="📚"
          title="No study materials match these filters"
          description="Try a different class or subject, or check back soon — teachers are adding new materials regularly."
        />
      )}
    </div>
  );
}
