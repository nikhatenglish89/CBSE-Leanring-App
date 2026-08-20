import { QueryClientProvider } from "@tanstack/react-query";
import { Route, BrowserRouter as Router, Routes } from "react-router-dom";

import { ToastProvider } from "./components/ui";
import { queryClient } from "./lib/queryClient";
import { HomePage } from "./pages/HomePage";
import { LoginPage } from "./pages/LoginPage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { RegisterPage } from "./pages/RegisterPage";
import { RoleDashboardPlaceholder } from "./pages/RoleDashboardPlaceholder";
import { StudentDashboardPage } from "./pages/student/StudentDashboardPage";
import { ProtectedRoute } from "./routes/ProtectedRoute";

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        <Router basename={import.meta.env.BASE_URL}>
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
            {/* Full teacher/parent/admin dashboards land in later phases;
                these placeholders prove role-aware routing works end-to-end. */}
            <Route
              path="/teacher"
              element={
                <ProtectedRoute allow={["TEACHER"]}>
                  <RoleDashboardPlaceholder roleLabel="Teacher" />
                </ProtectedRoute>
              }
            />
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
                  <RoleDashboardPlaceholder roleLabel="Admin" />
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </Router>
      </ToastProvider>
    </QueryClientProvider>
  );
}
