import { QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { Route, BrowserRouter as Router, Routes } from "react-router-dom";

import { Layout } from "./components/layout/Layout";
import { Spinner, ToastProvider } from "./components/ui";
import { useAuthBootstrap } from "./hooks/useAuthBootstrap";
import { queryClient } from "./lib/queryClient";
import { AdminBannersPage } from "./pages/admin/AdminBannersPage";
import { AdminDashboardPage } from "./pages/admin/AdminDashboardPage";
import { AdminFeedbackPage } from "./pages/admin/AdminFeedbackPage";
import { AdminUserDetailPage } from "./pages/admin/AdminUserDetailPage";
import { AdminUsersPage } from "./pages/admin/AdminUsersPage";
import { FeedbackPage } from "./pages/FeedbackPage";
import { ForcePasswordResetPage } from "./pages/ForcePasswordResetPage";
import { ForgotPasswordPage } from "./pages/ForgotPasswordPage";
import { GroupDetailPage } from "./pages/GroupDetailPage";
import { GroupsPage } from "./pages/GroupsPage";
import { HomePage } from "./pages/HomePage";
import { LessonDetailPage } from "./pages/LessonDetailPage";
import { LoginPage } from "./pages/LoginPage";
import { MessagesPage } from "./pages/MessagesPage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { PracticeSetPage } from "./pages/PracticeSetPage";
import { PracticeTestsPage } from "./pages/PracticeTestsPage";
import { ProfilePage } from "./pages/ProfilePage";
import { RegisterPage } from "./pages/RegisterPage";
import { ResetPasswordPage } from "./pages/ResetPasswordPage";
import { RoleDashboardPlaceholder } from "./pages/RoleDashboardPlaceholder";
import { StudentCourseDetailPage } from "./pages/student/StudentCourseDetailPage";
import { StudentDashboardPage } from "./pages/student/StudentDashboardPage";
import { StudyMaterialsPage } from "./pages/StudyMaterialsPage";
import { StudyVideosPage } from "./pages/StudyVideosPage";
import { TeacherCourseDetailPage } from "./pages/teacher/TeacherCourseDetailPage";
import { TeacherDashboardPage } from "./pages/teacher/TeacherDashboardPage";
import { TeacherInteractionPage } from "./pages/TeacherInteractionPage";
import { VerifyEmailPage } from "./pages/VerifyEmailPage";
import { ProtectedRoute } from "./routes/ProtectedRoute";

function AuthGate({ children }: { children: ReactNode }) {
  const isReady = useAuthBootstrap();
  if (!isReady) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50">
        <Spinner label="Loading EduSphere" className="text-base" />
      </div>
    );
  }
  return <>{children}</>;
}

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        <AuthGate>
        <Router basename={import.meta.env.BASE_URL}>
          <Layout>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
            <Route path="/reset-password" element={<ResetPasswordPage />} />
            <Route path="/verify-email" element={<VerifyEmailPage />} />
            <Route
              path="/force-password-reset"
              element={
                <ProtectedRoute skipPasswordResetCheck>
                  <ForcePasswordResetPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <ProfilePage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/lessons/:lessonId"
              element={
                <ProtectedRoute>
                  <LessonDetailPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/study-materials"
              element={
                <ProtectedRoute>
                  <StudyMaterialsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/study-videos"
              element={
                <ProtectedRoute>
                  <StudyVideosPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/teacher-interaction"
              element={
                <ProtectedRoute>
                  <TeacherInteractionPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/messages"
              element={
                <ProtectedRoute allow={["STUDENT", "TEACHER"]}>
                  <MessagesPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/groups"
              element={
                <ProtectedRoute allow={["STUDENT", "TEACHER"]}>
                  <GroupsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/groups/:groupId"
              element={
                <ProtectedRoute allow={["STUDENT", "TEACHER"]}>
                  <GroupDetailPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/feedback"
              element={
                <ProtectedRoute>
                  <FeedbackPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/practice-tests"
              element={
                <ProtectedRoute>
                  <PracticeTestsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/practice-tests/:practiceSetId"
              element={
                <ProtectedRoute>
                  <PracticeSetPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/student"
              element={
                <ProtectedRoute allow={["STUDENT"]}>
                  <StudentDashboardPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/student/courses/:courseId"
              element={
                <ProtectedRoute allow={["STUDENT"]}>
                  <StudentCourseDetailPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/teacher"
              element={
                <ProtectedRoute allow={["TEACHER"]}>
                  <TeacherDashboardPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/teacher/courses/:courseId"
              element={
                <ProtectedRoute allow={["TEACHER"]}>
                  <TeacherCourseDetailPage />
                </ProtectedRoute>
              }
            />
            {/* Parent dashboard lands in a later phase; this placeholder
                proves role-aware routing works end-to-end. */}
            <Route
              path="/parent"
              element={
                <ProtectedRoute allow={["PARENT"]}>
                  <RoleDashboardPlaceholder roleLabel="Parent" />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin"
              element={
                <ProtectedRoute allow={["ADMIN", "SUPER_ADMIN", "CONTENT_MANAGER", "SUPPORT_AGENT"]}>
                  <AdminDashboardPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/banners"
              element={
                <ProtectedRoute allow={["ADMIN", "SUPER_ADMIN", "CONTENT_MANAGER"]}>
                  <AdminBannersPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/feedback"
              element={
                <ProtectedRoute allow={["ADMIN", "SUPER_ADMIN", "SUPPORT_AGENT"]}>
                  <AdminFeedbackPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/users"
              element={
                <ProtectedRoute allow={["ADMIN", "SUPER_ADMIN", "SUPPORT_AGENT"]}>
                  <AdminUsersPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/users/:userId"
              element={
                <ProtectedRoute allow={["ADMIN", "SUPER_ADMIN", "SUPPORT_AGENT"]}>
                  <AdminUserDetailPage />
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
          </Layout>
        </Router>
        </AuthGate>
      </ToastProvider>
    </QueryClientProvider>
  );
}
