import { ComingSoonPage } from "./ComingSoonPage";

export function PracticeTestsPage() {
  return (
    <ComingSoonPage
      icon="📝"
      eyebrow="Practice Tests"
      title="Chapter and full-syllabus tests with instant scoring"
      description="The test engine isn't built yet — this is on the roadmap for a later phase of EduSphere."
      highlights={[
        "Chapter-wise and full-syllabus tests mapped to your class",
        "Instant scoring the moment you submit",
        "A topic-by-topic breakdown so you know what to revise",
      ]}
    />
  );
}
