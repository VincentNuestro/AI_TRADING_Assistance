import { useState } from "react";
import { Route, Routes } from "react-router-dom";
import { DashboardPage } from "./pages/DashboardPage";
import { LoginPage } from "./pages/LoginPage";
import { PredictionsPage } from "./pages/PredictionsPage";
import { MonteCarloPage } from "./pages/MonteCarloPage";
import { RiskPage } from "./pages/RiskPage";
import { HistoryPage } from "./pages/HistoryPage";
import { AccountsPage } from "./pages/AccountsPage";
import { ReportsPage } from "./pages/ReportsPage";
import { UsersPage } from "./pages/UsersPage";
import { AppShell } from "./components/AppShell";

export default function App() {
  const [isAuthenticated, setAuthenticated] = useState(false);

  if (!isAuthenticated) {
    return <LoginPage onSuccess={() => setAuthenticated(true)} />;
  }

  return (
    <Routes>
      <Route path="/" element={<AppShell onLogout={() => setAuthenticated(false)} />}>
        <Route index element={<DashboardPage />} />
        <Route path="predictions" element={<PredictionsPage />} />
        <Route path="monte-carlo" element={<MonteCarloPage />} />
        <Route path="risk" element={<RiskPage />} />
        <Route path="history" element={<HistoryPage />} />
        <Route path="accounts" element={<AccountsPage />} />
        <Route path="reports" element={<ReportsPage />} />
        <Route path="users" element={<UsersPage />} />
      </Route>
    </Routes>
  );
}
