import { type FormEvent, useState } from "react";

import { Badge, Button, Card, Input, Select, useToast } from "../../components/ui";
import { useCreateLesson, useSectionLessons } from "../../hooks/useCourses";
import type { CourseSectionOut, LessonContentType } from "../../types/curriculum";

export function TeacherSectionCard({ section }: { section: CourseSectionOut }) {
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

      <form className="mt-4 flex items-end gap-3" onSubmit={onCreate}>
        <div className="flex-1">
          <Input label="Lesson title" value={title} onChange={(event) => setTitle(event.target.value)} />
        </div>
        <Select
          label="Type"
          value={contentType}
          onChange={(event) => setContentType(event.target.value as LessonContentType)}
          className="w-32"
        >
          <option value="TEXT">Text</option>
          <option value="VIDEO">Video</option>
          <option value="PDF">PDF</option>
        </Select>
        <Button type="submit" isLoading={createLesson.isPending}>
          Add
        </Button>
      </form>
    </Card>
  );
}
