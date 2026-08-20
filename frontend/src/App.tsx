import { QueryClientProvider } from "@tanstack/react-query";
import { Navigate, Route, BrowserRouter as Router, Routes } from "react-router-dom";

import { ToastProvider } from "./components/ui";
import { queryClient } from "./lib/queryClient";
import { HomePage } from "./pages/HomePage";
import { LoginPage } from "./pages/LoginPage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { RegisterPage } from "./pages/RegisterPage";
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
                <ProtectedRoute>
                  <StudentDashboardPage />
                </ProtectedRoute>
              }
            />
            {/* /teacher/*, /parent/*, /admin/* route groups land in later phases */}
            <Route path="/teacher" element={<Navigate to="/" replace />} />
            <Route path="/parent" element={<Navigate to="/" replace />} />
            <Route path="/admin" element={<Navigate to="/" replace />} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </Router>
      </ToastProvider>
    </QueryClientProvider>
  );
}
