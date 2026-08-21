import { ComingSoonPage } from "./ComingSoonPage";

export function TeacherInteractionPage() {
  return (
    <ComingSoonPage
      icon="🧑‍🏫"
      eyebrow="Teacher Interaction"
      title="Ask questions and join live classes"
      description="Direct Q&A with teachers and scheduled live classes aren't built yet — this is on the roadmap for a later phase of EduSphere."
      highlights={[
        "Post a question on any lesson and get an answer from your teacher",
        "Join scheduled live classes for real-time doubt clearing",
        "See a history of your questions and answers per subject",
      ]}
    />
  );
}
