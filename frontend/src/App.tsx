import { QueryClientProvider } from "@tanstack/react-query";
import { Route, BrowserRouter as Router, Routes } from "react-router-dom";

import { Layout } from "./components/layout/Layout";
import { ToastProvider } from "./components/ui";
import { queryClient } from "./lib/queryClient";
import { AdminDashboardPage } from "./pages/admin/AdminDashboardPage";
import { HomePage } from "./pages/HomePage";
import { LoginPage } from "./pages/LoginPage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { RegisterPage } from "./pages/RegisterPage";
import { RoleDashboardPlaceholder } from "./pages/RoleDashboardPlaceholder";
import { StudentCourseDetailPage } from "./pages/student/StudentCourseDetailPage";
import { StudentDashboardPage } from "./pages/student/StudentDashboardPage";
import { TeacherCourseDetailPage } from "./pages/teacher/TeacherCourseDetailPage";
import { TeacherDashboardPage } from "./pages/teacher/TeacherDashboardPage";
import { ProtectedRoute } from "./routes/ProtectedRoute";

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        <Router basename={import.meta.env.BASE_URL}>
          <Layout>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
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
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
          </Layout>
        </Router>
      </ToastProvider>
    </QueryClientProvider>
  );
}
