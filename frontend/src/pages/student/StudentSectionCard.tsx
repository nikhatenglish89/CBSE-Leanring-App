import { Badge, Card } from "../../components/ui";
import { useSectionLessons } from "../../hooks/useCourses";
import type { CourseSectionOut } from "../../types/curriculum";

export function StudentSectionCard({ section }: { section: CourseSectionOut }) {
  const { data: lessons } = useSectionLessons(section.id);

  return (
    <Card>
      <h3 className="font-medium text-slate-900">{section.title}</h3>
      <ul className="mt-3 flex flex-col gap-2">
        {lessons?.map((lesson) => (
          <li
            key={lesson.id}
            className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2 text-sm"
          >
            <span>{lesson.title}</span>
            <Badge tone="brand">{lesson.content_type}</Badge>
          </li>
        ))}
        {lessons?.length === 0 && <li className="text-sm text-slate-500">No lessons yet.</li>}
      </ul>
    </Card>
  );
}
