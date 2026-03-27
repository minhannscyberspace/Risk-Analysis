import { Suspense, lazy, useState } from "react";
import { BrowserRouter, Link, Route, Routes } from "react-router-dom";

import UploadPage from "./pages/UploadPage";
import { type AppState } from "./types/app";

const DashboardPage = lazy(() => import("./pages/DashboardPage"));
const ScenariosPage = lazy(() => import("./pages/ScenariosPage"));
const ReportPage = lazy(() => import("./pages/ReportPage"));

function App() {
  const [state, setState] = useState<AppState>({
    datasetId: "",
    analysisId: "",
    scenarioId: "",
    reportId: "",
    confidenceLevel: 0.95,
    weightsInput: "",
    pca: null,
    risk: null,
    metrics: null,
    scenarios: null,
    summary: null,
    report: null,
  });

  return (
    <BrowserRouter>
      <main className="layout">
        <header>
          <h1>Portfolio Risk Analysis</h1>
          <nav className="nav">
            <Link to="/">Upload</Link>
            <Link to="/dashboard">Dashboard</Link>
            <Link to="/scenarios">Scenarios</Link>
            <Link to="/report">Report</Link>
          </nav>
        </header>

        <Suspense fallback={<section className="card">Loading page...</section>}>
          <Routes>
            <Route path="/" element={<UploadPage state={state} setState={setState} />} />
            <Route path="/dashboard" element={<DashboardPage state={state} setState={setState} />} />
            <Route path="/scenarios" element={<ScenariosPage state={state} setState={setState} />} />
            <Route path="/report" element={<ReportPage state={state} setState={setState} />} />
          </Routes>
        </Suspense>
      </main>
    </BrowserRouter>
  );
}

export default App;
