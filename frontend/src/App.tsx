import { BrowserRouter, Routes, Route } from "react-router-dom";
import { lazy, Suspense } from "react";
import AppLayout from "./components/layout/AppLayout";
import { PageSpinner } from "./components/ui/PageShell";

const DashboardPage = lazy(() => import("./pages/DashboardPage"));
const MomentumPage = lazy(() => import("./pages/MomentumPage"));
const TechRadarPage = lazy(() => import("./pages/TechRadarPage"));
const EmergingPage = lazy(() => import("./pages/EmergingPage"));
const RepoHealthPage = lazy(() => import("./pages/RepoHealthPage"));
const EcosystemGraphPage = lazy(() => import("./pages/EcosystemGraphPage"));
const ForecastPage = lazy(() => import("./pages/ForecastPage"));
const RecommendPage = lazy(() => import("./pages/RecommendPage"));
const BattlesPage = lazy(() => import("./pages/BattlesPage"));
const GlobalMapPage = lazy(() => import("./pages/GlobalMapPage"));
const TechIndexPage = lazy(() => import("./pages/TechIndexPage"));

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<Suspense fallback={<PageSpinner />}><DashboardPage /></Suspense>} />
          <Route path="/momentum" element={<Suspense fallback={<PageSpinner />}><MomentumPage /></Suspense>} />
          <Route path="/radar" element={<Suspense fallback={<PageSpinner />}><TechRadarPage /></Suspense>} />
          <Route path="/emerging" element={<Suspense fallback={<PageSpinner />}><EmergingPage /></Suspense>} />
          <Route path="/health" element={<Suspense fallback={<PageSpinner />}><RepoHealthPage /></Suspense>} />
          <Route path="/ecosystem" element={<Suspense fallback={<PageSpinner />}><EcosystemGraphPage /></Suspense>} />
          <Route path="/forecast" element={<Suspense fallback={<PageSpinner />}><ForecastPage /></Suspense>} />
          <Route path="/recommend" element={<Suspense fallback={<PageSpinner />}><RecommendPage /></Suspense>} />
          <Route path="/battles" element={<Suspense fallback={<PageSpinner />}><BattlesPage /></Suspense>} />
          <Route path="/map" element={<Suspense fallback={<PageSpinner />}><GlobalMapPage /></Suspense>} />
          <Route path="/index" element={<Suspense fallback={<PageSpinner />}><TechIndexPage /></Suspense>} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
