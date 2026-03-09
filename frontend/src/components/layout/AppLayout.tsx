import { NavLink, Outlet, useLocation } from "react-router-dom";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  LayoutDashboard,
  Zap,
  Radar,
  Flame,
  HeartPulse,
  Share2,
  TrendingUp,
  Sparkles,
  Swords,
  Globe,
  BarChart3,
  Search,
  Menu,
  X,
} from "lucide-react";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/momentum", label: "Momentum Intelligence", icon: Zap },
  { to: "/radar", label: "Technology Radar", icon: Radar },
  { to: "/emerging", label: "Emerging Technologies", icon: Flame },
  { to: "/health", label: "Repo Health", icon: HeartPulse },
  { to: "/ecosystem", label: "Ecosystem Graph", icon: Share2 },
  { to: "/forecast", label: "Forecast", icon: TrendingUp },
  { to: "/recommend", label: "AI Recommendations", icon: Sparkles },
  { to: "/battles", label: "Tech Battles", icon: Swords },
  { to: "/map", label: "Global Map", icon: Globe },
  { to: "/index", label: "Tech Index", icon: BarChart3 },
];

export default function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const location = useLocation();

  return (
    <div className="flex h-screen overflow-hidden bg-dp-bg text-dp-text">
      {/* Desktop Sidebar */}
      <aside className="hidden lg:flex lg:w-[220px] flex-col border-r border-dp-border bg-dp-bg">
        <div className="flex h-14 items-center gap-2 px-5 border-b border-dp-border">
          <span className="text-lg">⚡</span>
          <span className="text-[15px] font-semibold tracking-tight bg-gradient-to-r from-dp-accent to-dp-secondary bg-clip-text text-transparent">
            DevPulse AI
          </span>
          <span className="ml-auto rounded-md bg-dp-accent-dim px-1.5 py-0.5 text-[10px] font-medium text-dp-accent">
            v2
          </span>
        </div>
        <nav className="flex-1 overflow-y-auto px-2.5 py-3 space-y-0.5">
          {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                `group relative flex items-center gap-2.5 rounded-lg px-3 py-[7px] text-[13px] font-medium transition-all duration-200 ${
                  isActive
                    ? "dp-nav-active bg-dp-accent-dim text-dp-accent"
                    : "text-dp-text-3 hover:bg-dp-surface-2 hover:text-dp-text-2"
                }`
              }
            >
              <Icon className="h-[15px] w-[15px] shrink-0" />
              <span className="truncate">{label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="border-t border-dp-border px-5 py-3">
          <p className="text-[11px] text-dp-text-4">Developer Intelligence Platform</p>
        </div>
      </aside>

      {/* Mobile sidebar overlay */}
      <AnimatePresence>
        {sidebarOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-40 bg-black/70 backdrop-blur-sm lg:hidden"
              onClick={() => setSidebarOpen(false)}
            />
            <motion.aside
              initial={{ x: -240 }}
              animate={{ x: 0 }}
              exit={{ x: -240 }}
              transition={{ type: "spring", damping: 28, stiffness: 320 }}
              className="fixed inset-y-0 left-0 z-50 w-[220px] flex flex-col border-r border-dp-border bg-dp-bg lg:hidden"
            >
              <div className="flex h-14 items-center justify-between px-5 border-b border-dp-border">
                <div className="flex items-center gap-2">
                  <span className="text-lg">⚡</span>
                  <span className="text-[15px] font-semibold bg-gradient-to-r from-dp-accent to-dp-secondary bg-clip-text text-transparent">
                    DevPulse AI
                  </span>
                </div>
                <button onClick={() => setSidebarOpen(false)} className="text-dp-text-3 hover:text-dp-text">
                  <X className="h-5 w-5" />
                </button>
              </div>
              <nav className="flex-1 overflow-y-auto px-2.5 py-3 space-y-0.5">
                {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
                  <NavLink
                    key={to}
                    to={to}
                    end={to === "/"}
                    onClick={() => setSidebarOpen(false)}
                    className={({ isActive }) =>
                      `relative flex items-center gap-2.5 rounded-lg px-3 py-[7px] text-[13px] font-medium transition-all duration-200 ${
                        isActive
                          ? "dp-nav-active bg-dp-accent-dim text-dp-accent"
                          : "text-dp-text-3 hover:bg-dp-surface-2 hover:text-dp-text-2"
                      }`
                    }
                  >
                    <Icon className="h-[15px] w-[15px] shrink-0" />
                    {label}
                  </NavLink>
                ))}
              </nav>
            </motion.aside>
          </>
        )}
      </AnimatePresence>

      {/* Main content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Header */}
        <header className="flex h-14 items-center gap-3 border-b border-dp-border bg-dp-bg/80 px-4 backdrop-blur-md lg:px-6">
          <button onClick={() => setSidebarOpen(true)} className="lg:hidden text-dp-text-3 hover:text-dp-text">
            <Menu className="h-5 w-5" />
          </button>
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-dp-text-4" />
            <input
              type="text"
              placeholder="Search technologies..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full rounded-lg border border-dp-border bg-dp-surface py-1.5 pl-9 pr-3 text-sm text-dp-text-2 placeholder-dp-text-4 outline-none transition-colors focus:border-dp-accent/40 focus:ring-1 focus:ring-dp-accent/15"
            />
          </div>
          <div className="ml-auto flex items-center gap-3">
            <div className="h-7 w-7 rounded-full bg-gradient-to-br from-dp-accent to-dp-secondary flex items-center justify-center text-[11px] font-semibold text-dp-bg">
              D
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto" data-lenis-prevent>
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, ease: [0.25, 0.46, 0.45, 0.94] }}
            className="px-4 py-6 lg:px-8"
          >
            <Outlet />
          </motion.div>
        </main>
      </div>
    </div>
  );
}
