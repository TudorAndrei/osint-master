import { Routes, Route } from "react-router-dom";
import { ThemeProvider } from "@/components/layout/ThemeProvider";
import RequireAuth from "@/components/auth/RequireAuth";
import RootLayout from "@/routes/root";
import HomePage from "@/routes/home";
import InvestigationPage from "@/routes/investigation";

export default function App() {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="osint-theme">
      <Routes>
        <Route
          path="/"
          element={(
            <RequireAuth>
              <RootLayout />
            </RequireAuth>
          )}
        >
          <Route index element={<HomePage />} />
          <Route path="investigation/:id" element={<InvestigationPage />} />
        </Route>
      </Routes>
    </ThemeProvider>
  );
}
