import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { Badge, Button, Card, CardSkeleton, Textarea, useToast } from "../components/ui";
import { useAuth } from "../hooks/useAuth";
import { useLesson, useUpdateLesson } from "../hooks/useCourses";
import type { LessonContentType } from "../types/curriculum";

const CONTENT_ICON: Record<LessonContentType, string> = {
  TEXT: "📄",
  VIDEO: "🎥",
  PDF: "📎",
};

const CAN_EDIT_ROLES = ["TEACHER", "ADMIN", "SUPER_ADMIN", "CONTENT_MANAGER"];

export function LessonDetailPage() {
  const { lessonId } = useParams<{ lessonId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { data: lesson, isLoading } = useLesson(lessonId);
  const updateLesson = useUpdateLesson();
  const { showToast } = useToast();

  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState("");

  useEffect(() => {
    if (lesson) setDraft(lesson.content);
  }, [lesson]);

  const canEdit = Boolean(user && CAN_EDIT_ROLES.includes(user.role));

  const onSave = async () => {
    if (!lessonId) return;
    try {
      await updateLesson.mutateAsync({ lessonId, content: draft });
      setEditing(false);
      showToast("Lesson content saved.", "success");
    } catch {
      showToast("Could not save — you may not own this course.", "error");
    }
  };

  if (isLoading || !lesson) {
    return (
      <div className="page-shell flex flex-col gap-4 py-10">
        <CardSkeleton />
      </div>
    );
  }

  return (
    <div className="page-shell mx-auto flex max-w-3xl flex-col gap-6 py-10">
      <button
        type="button"
        onClick={() => navigate(-1)}
        className="self-start text-sm font-medium text-brand-600 hover:underline"
      >
        &larr; Back
      </button>

      <Card>
        <div className="flex flex-wrap items-center gap-2">
          <Badge tone="neutral" className="gap-1">
            <span>{CONTENT_ICON[lesson.content_type]}</span> {lesson.content_type}
          </Badge>
          {lesson.description && <Badge tone="brand">{lesson.description}</Badge>}
        </div>
        <h1 className="mt-3 font-display text-2xl font-bold text-slate-900 sm:text-3xl">{lesson.title}</h1>

        <div className="mt-6 border-t border-slate-100 pt-6">
          {editing ? (
            <div className="flex flex-col gap-3">
              <Textarea
                label="Lesson content"
                rows={16}
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
              />
              <div className="flex gap-2">
                <Button onClick={onSave} isLoading={updateLesson.isPending}>
                  Save
                </Button>
                <Button variant="secondary" onClick={() => { setEditing(false); setDraft(lesson.content); }}>
                  Cancel
                </Button>
              </div>
            </div>
          ) : lesson.content.trim() ? (
            <p className="whitespace-pre-line font-serif text-base leading-8 text-slate-800">
              {lesson.content}
            </p>
          ) : (
            <p className="text-sm italic text-slate-500">
              No content has been added for this lesson yet.
            </p>
          )}

          {canEdit && !editing && (
            <Button variant="secondary" className="mt-6" onClick={() => setEditing(true)}>
              {lesson.content.trim() ? "Edit content" : "Add content"}
            </Button>
          )}
        </div>
      </Card>
    </div>
  );
}
