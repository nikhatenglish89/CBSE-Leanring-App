import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { Badge, Button, Card, CardSkeleton, useToast } from "../components/ui";
import { usePracticeSet, useSubmitPracticeSet } from "../hooks/usePractice";
import type { PracticeSubmitResult } from "../types/curriculum";

export function PracticeSetPage() {
  const { practiceSetId } = useParams<{ practiceSetId: string }>();
  const navigate = useNavigate();
  const { data: practiceSet, isLoading } = usePracticeSet(practiceSetId);
  const submitPracticeSet = useSubmitPracticeSet(practiceSetId);
  const { showToast } = useToast();

  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [result, setResult] = useState<PracticeSubmitResult | null>(null);

  if (isLoading || !practiceSet) {
    return (
      <div className="page-shell flex flex-col gap-4 py-10">
        <CardSkeleton />
      </div>
    );
  }

  const answeredCount = Object.keys(answers).length;

  const onSubmit = async () => {
    try {
      const payload = Object.entries(answers).map(([question_id, selected_index]) => ({
        question_id,
        selected_index,
      }));
      const data = await submitPracticeSet.mutateAsync(payload);
      setResult(data);
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch {
      showToast("Could not submit your answers. Please try again.", "error");
    }
  };

  const onRetake = () => {
    setAnswers({});
    setResult(null);
  };

  return (
    <div className="page-shell mx-auto flex max-w-3xl flex-col gap-6 py-10">
      <button
        type="button"
        onClick={() => navigate(-1)}
        className="self-start text-sm font-medium text-brand-600 hover:underline"
      >
        &larr; Back
      </button>

      <div>
        <div className="mb-2 flex items-center gap-2">
          <Badge tone="brand">{practiceSet.class_name}</Badge>
          <Badge tone="neutral">{practiceSet.subject_name}</Badge>
        </div>
        <h1 className="text-2xl font-semibold text-slate-900">{practiceSet.title}</h1>
      </div>

      {result && (
        <Card className="flex flex-col items-center gap-2 border-brand-200 bg-brand-50 py-6 text-center">
          <p className="text-sm font-medium text-brand-700">Your score</p>
          <p className="text-4xl font-bold text-brand-800">
            {result.score} / {result.total}
          </p>
          <Button variant="secondary" onClick={onRetake} className="mt-2">
            Retake this test
          </Button>
        </Card>
      )}

      <div className="flex flex-col gap-4">
        {practiceSet.questions.map((question, index) => {
          const questionResult = result?.results.find((r) => r.question_id === question.id);
          return (
            <Card key={question.id} className="flex flex-col gap-3">
              <p className="font-medium text-slate-900">
                {index + 1}. {question.question_text}
              </p>
              <div className="flex flex-col gap-2">
                {question.options.map((option, optionIndex) => {
                  const isSelected = answers[question.id] === optionIndex;
                  let optionClasses =
                    "flex items-center gap-3 rounded-lg border px-3 py-2 text-sm transition-colors";
                  if (questionResult) {
                    if (optionIndex === questionResult.correct_index) {
                      optionClasses += " border-emerald-300 bg-emerald-50 text-emerald-800";
                    } else if (optionIndex === questionResult.selected_index) {
                      optionClasses += " border-rose-300 bg-rose-50 text-rose-800";
                    } else {
                      optionClasses += " border-slate-200 text-slate-500";
                    }
                  } else {
                    optionClasses += isSelected
                      ? " border-brand-400 bg-brand-50 text-brand-800"
                      : " border-slate-200 text-slate-700 hover:border-brand-200 hover:bg-slate-50";
                  }
                  return (
                    <label key={optionIndex} className={optionClasses}>
                      <input
                        type="radio"
                        name={question.id}
                        checked={isSelected}
                        disabled={Boolean(result)}
                        onChange={() =>
                          setAnswers((prev) => ({ ...prev, [question.id]: optionIndex }))
                        }
                        className="h-4 w-4"
                      />
                      {option}
                    </label>
                  );
                })}
              </div>
              {questionResult && (
                <p className="text-xs text-slate-500">
                  {questionResult.is_correct ? "Correct. " : "Not quite. "}
                  {questionResult.explanation}
                </p>
              )}
            </Card>
          );
        })}
      </div>

      {!result && (
        <div className="flex flex-col items-center gap-2 pb-6">
          <p className="text-xs text-slate-500">
            {answeredCount} of {practiceSet.questions.length} answered
          </p>
          <Button onClick={onSubmit} isLoading={submitPracticeSet.isPending} disabled={answeredCount === 0}>
            Submit test
          </Button>
        </div>
      )}
    </div>
  );
}
