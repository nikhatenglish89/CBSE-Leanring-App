import { type FormEvent, useState } from "react";
import { Link } from "react-router-dom";

import { Badge, Button, Card, Input, Select, useToast } from "../../components/ui";
import { useCreateLesson, useSectionLessons } from "../../hooks/useCourses";
import type { CourseSectionOut, LessonContentType } from "../../types/curriculum";

const CONTENT_ICON: Record<LessonContentType, string> = {
  TEXT: "📄",
  VIDEO: "🎥",
  PDF: "📎",
};

export function TeacherSectionCard({ section, index }: { section: CourseSectionOut; index: number }) {
  const { data: lessons } = useSectionLessons(section.id);
  const createLesson = useCreateLesson();
  const { showToast } = useToast();
  const [title, setTitle] = useState("");
  const [contentType, setContentType] = useState<LessonContentType>("TEXT");

  const onCreate = async (event: FormEvent) => {
    event.preventDefault();
    if (!title.trim()) return;
    try {
      await createLesson.mutateAsync({ sectionId: section.id, title, content_type: contentType });
      setTitle("");
    } catch {
      showToast("Could not create the lesson.", "error");
    }
  };

  return (
    <Card>
      <div className="flex items-center gap-3">
        <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-brand-50 text-xs font-semibold text-brand-700">
          {index + 1}
        </span>
        <h3 className="font-semibold text-slate-900">{section.title}</h3>
      </div>

      <ul className="mt-4 flex flex-col divide-y divide-slate-100 border-t border-slate-100">
        {lessons?.map((lesson) => (
          <li key={lesson.id}>
            <Link
              to={`/lessons/${lesson.id}`}
              className="flex items-center gap-3 py-2.5 text-sm transition-colors hover:text-brand-700"
            >
              <span className="text-base">{CONTENT_ICON[lesson.content_type]}</span>
              <span className="flex-1 text-slate-800 hover:underline">{lesson.title}</span>
              <Badge tone="neutral">{lesson.content_type}</Badge>
            </Link>
          </li>
        ))}
        {lessons?.length === 0 && <li className="py-2.5 text-sm text-slate-500">No lessons yet.</li>}
      </ul>

      <form className="mt-4 flex flex-col gap-3 border-t border-slate-100 pt-4 sm:flex-row sm:items-end" onSubmit={onCreate}>
        <div className="flex-1">
          <Input
            label="Lesson title"
            placeholder="e.g. Introduction to Irrational Numbers"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
          />
        </div>
        <Select
          label="Type"
          value={contentType}
          onChange={(event) => setContentType(event.target.value as LessonContentType)}
          className="sm:w-32"
        >
          <option value="TEXT">Text</option>
          <option value="VIDEO">Video</option>
          <option value="PDF">PDF</option>
        </Select>
        <Button type="submit" isLoading={createLesson.isPending}>
          Add lesson
        </Button>
      </form>
    </Card>
  );
}
