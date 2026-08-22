import { useState } from "react";

import { useAnswerQuestion, useAskQuestion, useLessonQuestions } from "../../hooks/useInteraction";
import { Button, Card, Skeleton, Textarea, useToast } from "../ui";

export function LessonQABlock({
  lessonId,
  canAsk,
  canAnswer,
}: {
  lessonId: string;
  canAsk: boolean;
  canAnswer: boolean;
}) {
  const { data: questions, isLoading } = useLessonQuestions(lessonId);
  const askQuestion = useAskQuestion(lessonId);
  const answerQuestion = useAnswerQuestion(lessonId);
  const { showToast } = useToast();

  const [draftQuestion, setDraftQuestion] = useState("");
  const [answeringId, setAnsweringId] = useState<string | null>(null);
  const [draftAnswer, setDraftAnswer] = useState("");

  if (isLoading) {
    return (
      <Card>
        <h2 className="text-lg font-semibold text-slate-900">Questions &amp; answers</h2>
        <div className="mt-4 flex flex-col gap-2">
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
        </div>
      </Card>
    );
  }

  if ((questions?.length ?? 0) === 0 && !canAsk) return null;

  const onAsk = async () => {
    if (!draftQuestion.trim()) return;
    try {
      await askQuestion.mutateAsync(draftQuestion.trim());
      setDraftQuestion("");
      showToast("Your question has been posted.", "success");
    } catch {
      showToast("Could not post your question. Please try again.", "error");
    }
  };

  const startAnswering = (questionId: string, existingBody?: string) => {
    setAnsweringId(questionId);
    setDraftAnswer(existingBody ?? "");
  };

  const onAnswer = async (questionId: string) => {
    if (!draftAnswer.trim()) return;
    try {
      await answerQuestion.mutateAsync({ questionId, body: draftAnswer.trim() });
      setAnsweringId(null);
      setDraftAnswer("");
      showToast("Your answer has been posted.", "success");
    } catch {
      showToast("Could not post your answer. Please try again.", "error");
    }
  };

  return (
    <Card>
      <h2 className="text-lg font-semibold text-slate-900">Questions &amp; answers</h2>

      {questions && questions.length > 0 ? (
        <ul className="mt-4 flex flex-col divide-y divide-slate-100 border-t border-slate-100">
          {questions.map((question) => (
            <li key={question.id} className="flex flex-col gap-2 py-4">
              <div>
                <p className="text-sm font-medium text-slate-800">{question.body}</p>
                <p className="mt-0.5 text-xs text-slate-500">
                  Asked by {question.student_name}
                </p>
              </div>

              {question.answer ? (
                <div className="ml-3 rounded-lg border border-brand-100 bg-brand-50/60 p-3">
                  <p className="text-sm text-slate-800">{question.answer.body}</p>
                  <p className="mt-1 text-xs text-slate-500">
                    &mdash; {question.answer.teacher_name}
                  </p>
                  {canAnswer && answeringId !== question.id && (
                    <Button
                      variant="ghost"
                      className="mt-2 !px-0"
                      onClick={() => startAnswering(question.id, question.answer?.body)}
                    >
                      Edit answer
                    </Button>
                  )}
                </div>
              ) : (
                canAnswer &&
                answeringId !== question.id && (
                  <Button variant="secondary" className="ml-3 w-fit" onClick={() => startAnswering(question.id)}>
                    Answer
                  </Button>
                )
              )}

              {canAnswer && answeringId === question.id && (
                <div className="ml-3 flex flex-col gap-2">
                  <Textarea
                    label="Your answer"
                    rows={3}
                    value={draftAnswer}
                    onChange={(event) => setDraftAnswer(event.target.value)}
                    placeholder="Write your answer..."
                  />
                  <div className="flex gap-2">
                    <Button onClick={() => onAnswer(question.id)} isLoading={answerQuestion.isPending}>
                      Post answer
                    </Button>
                    <Button variant="secondary" onClick={() => setAnsweringId(null)}>
                      Cancel
                    </Button>
                  </div>
                </div>
              )}
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-4 text-sm italic text-slate-500">No questions yet.</p>
      )}

      {canAsk && (
        <div className="mt-4 flex flex-col gap-2 border-t border-slate-100 pt-4">
          <Textarea
            label="Your question"
            rows={3}
            value={draftQuestion}
            onChange={(event) => setDraftQuestion(event.target.value)}
            placeholder="Ask your teacher a question about this lesson..."
          />
          <Button
            className="w-fit"
            onClick={onAsk}
            isLoading={askQuestion.isPending}
            disabled={!draftQuestion.trim()}
          >
            Post question
          </Button>
        </div>
      )}
    </Card>
  );
}
