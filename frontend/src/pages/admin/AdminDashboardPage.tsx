import { type FormEvent, useState } from "react";

import { Button, Card, Input, Select, useToast } from "../../components/ui";
import { useAuth } from "../../hooks/useAuth";
import { useClasses, useCreateClass, useCreateSubject, useSubjects } from "../../hooks/useCurriculum";

export function AdminDashboardPage() {
  const { user } = useAuth();
  const { showToast } = useToast();
  const { data: classes } = useClasses();
  const createClass = useCreateClass();
  const [className, setClassName] = useState("");

  const [subjectClassId, setSubjectClassId] = useState("");
  const { data: subjects } = useSubjects(subjectClassId || undefined);
  const createSubject = useCreateSubject();
  const [subjectName, setSubjectName] = useState("");

  const onCreateClass = async (event: FormEvent) => {
    event.preventDefault();
    if (!className.trim()) return;
    try {
      await createClass.mutateAsync({ name: className });
      setClassName("");
      showToast("Class created.", "success");
    } catch {
      showToast("Could not create class — the name may already exist.", "error");
    }
  };

  const onCreateSubject = async (event: FormEvent) => {
    event.preventDefault();
    if (!subjectClassId || !subjectName.trim()) return;
    try {
      await createSubject.mutateAsync({ class_id: subjectClassId, name: subjectName });
      setSubjectName("");
      showToast("Subject created.", "success");
    } catch {
      showToast("Could not create subject — it may already exist for this class.", "error");
    }
  };

  return (
    <div className="mx-auto max-w-4xl px-4 py-12">
      <h1 className="text-2xl font-semibold text-slate-900">Welcome, {user?.full_name}</h1>
      <p className="mt-1 text-sm text-slate-600">Manage the curriculum taxonomy — classes and subjects.</p>

      <div className="mt-6 grid gap-6 sm:grid-cols-2">
        <Card>
          <h2 className="text-lg font-medium text-slate-900">Classes</h2>
          <ul className="mt-3 flex flex-col gap-1 text-sm text-slate-700">
            {classes?.map((klass) => (
              <li key={klass.id}>{klass.name}</li>
            ))}
          </ul>
          <form className="mt-4 flex items-end gap-3" onSubmit={onCreateClass}>
            <div className="flex-1">
              <Input label="New class name" value={className} onChange={(event) => setClassName(event.target.value)} />
            </div>
            <Button type="submit" isLoading={createClass.isPending}>
              Add
            </Button>
          </form>
        </Card>

        <Card>
          <h2 className="text-lg font-medium text-slate-900">Subjects</h2>
          <Select
            label="Class"
            value={subjectClassId}
            onChange={(event) => setSubjectClassId(event.target.value)}
            className="mt-3"
          >
            <option value="">Select a class</option>
            {classes?.map((klass) => (
              <option key={klass.id} value={klass.id}>
                {klass.name}
              </option>
            ))}
          </Select>
          <ul className="mt-3 flex flex-col gap-1 text-sm text-slate-700">
            {subjects?.map((subject) => (
              <li key={subject.id}>{subject.name}</li>
            ))}
          </ul>
          <form className="mt-4 flex items-end gap-3" onSubmit={onCreateSubject}>
            <div className="flex-1">
              <Input
                label="New subject name"
                value={subjectName}
                onChange={(event) => setSubjectName(event.target.value)}
                disabled={!subjectClassId}
              />
            </div>
            <Button type="submit" isLoading={createSubject.isPending} disabled={!subjectClassId}>
              Add
            </Button>
          </form>
        </Card>
      </div>
    </div>
  );
}
