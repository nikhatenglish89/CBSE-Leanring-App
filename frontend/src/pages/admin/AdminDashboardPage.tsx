import { type FormEvent, useState } from "react";

import { PageHeader } from "../../components/layout/PageHeader";
import { StudyLinksCard } from "../../components/StudyLinksCard";
import { Button, Card, EmptyState, Input, Select, useToast } from "../../components/ui";
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
    <div className="page-shell flex flex-col gap-8 py-10">
      <PageHeader
        eyebrow="Admin"
        title={`Welcome back, ${user?.full_name?.split(" ")[0] ?? "there"}`}
        subtitle="Manage the curriculum taxonomy — classes and subjects."
      />

      <StudyLinksCard />

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <h2 className="text-lg font-semibold text-slate-900">Classes</h2>
          <div className="mt-4 overflow-hidden rounded-lg border border-slate-200">
            {classes && classes.length > 0 ? (
              <table className="w-full text-sm">
                <thead className="bg-slate-50 text-left text-xs font-medium uppercase tracking-wide text-slate-500">
                  <tr>
                    <th className="px-4 py-2.5">Name</th>
                    <th className="px-4 py-2.5">Order</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {classes.map((klass) => (
                    <tr key={klass.id}>
                      <td className="px-4 py-2.5 font-medium text-slate-800">{klass.name}</td>
                      <td className="px-4 py-2.5 text-slate-500">{klass.display_order}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="p-4">
                <EmptyState icon="🏫" title="No classes yet" />
              </div>
            )}
          </div>
          <form className="mt-4 flex items-end gap-3" onSubmit={onCreateClass}>
            <div className="flex-1">
              <Input
                label="New class name"
                placeholder="e.g. Class XIII"
                value={className}
                onChange={(event) => setClassName(event.target.value)}
              />
            </div>
            <Button type="submit" isLoading={createClass.isPending}>
              Add
            </Button>
          </form>
        </Card>

        <Card>
          <h2 className="text-lg font-semibold text-slate-900">Subjects</h2>
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

          <div className="mt-4 overflow-hidden rounded-lg border border-slate-200">
            {subjectClassId && subjects && subjects.length > 0 ? (
              <table className="w-full text-sm">
                <thead className="bg-slate-50 text-left text-xs font-medium uppercase tracking-wide text-slate-500">
                  <tr>
                    <th className="px-4 py-2.5">Name</th>
                    <th className="px-4 py-2.5">Order</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {subjects.map((subject) => (
                    <tr key={subject.id}>
                      <td className="px-4 py-2.5 font-medium text-slate-800">{subject.name}</td>
                      <td className="px-4 py-2.5 text-slate-500">{subject.display_order}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="p-4">
                <EmptyState
                  icon="📖"
                  title={subjectClassId ? "No subjects yet for this class" : "Select a class to view its subjects"}
                />
              </div>
            )}
          </div>

          <form className="mt-4 flex items-end gap-3" onSubmit={onCreateSubject}>
            <div className="flex-1">
              <Input
                label="New subject name"
                placeholder="e.g. Computer Science"
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
