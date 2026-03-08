import { BrowserRouter, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import MobileNav from "./components/MobileNav";
import DashboardPage from "./pages/DashboardPage";
import TechRadarPage from "./pages/TechRadarPage";
import RepoHealthPage from "./pages/RepoHealthPage";
import ForecastPage from "./pages/ForecastPage";

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex flex-1 flex-col lg:pl-56">
          <MobileNav />
          <main className="flex-1 px-4 py-6 sm:px-6 lg:px-8">
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/radar" element={<TechRadarPage />} />
              <Route path="/health" element={<RepoHealthPage />} />
              <Route path="/forecast" element={<ForecastPage />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
}
