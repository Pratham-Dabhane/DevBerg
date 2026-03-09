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
  Mountain,
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
    <div className="flex h-screen overflow-hidden bg-gray-950 text-gray-100">
      {/* Desktop Sidebar */}
      <aside className="hidden lg:flex lg:w-60 flex-col border-r border-gray-800/60 bg-gray-950">
        <div className="flex h-14 items-center gap-2.5 px-5 border-b border-gray-800/60">
          <Mountain className="h-5 w-5 text-blue-400" />
          <span className="text-base font-semibold tracking-tight">DevBerg</span>
          <span className="ml-auto rounded bg-blue-500/10 px-1.5 py-0.5 text-[10px] font-medium text-blue-400">
            v2.0
          </span>
        </div>
        <nav className="flex-1 overflow-y-auto px-3 py-3 space-y-0.5">
          {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                `group flex items-center gap-2.5 rounded-lg px-3 py-2 text-[13px] font-medium transition-all duration-150 ${
                  isActive
                    ? "bg-blue-500/10 text-blue-400"
                    : "text-gray-500 hover:bg-gray-800/50 hover:text-gray-300"
                }`
              }
            >
              <Icon className="h-4 w-4 shrink-0" />
              <span className="truncate">{label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="border-t border-gray-800/60 px-5 py-3">
          <p className="text-[11px] text-gray-600">AI Developer Ecosystem Intelligence</p>
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
              className="fixed inset-0 z-40 bg-black/60 lg:hidden"
              onClick={() => setSidebarOpen(false)}
            />
            <motion.aside
              initial={{ x: -260 }}
              animate={{ x: 0 }}
              exit={{ x: -260 }}
              transition={{ type: "spring", damping: 25, stiffness: 300 }}
              className="fixed inset-y-0 left-0 z-50 w-60 flex flex-col border-r border-gray-800/60 bg-gray-950 lg:hidden"
            >
              <div className="flex h-14 items-center justify-between px-5 border-b border-gray-800/60">
                <div className="flex items-center gap-2.5">
                  <Mountain className="h-5 w-5 text-blue-400" />
                  <span className="text-base font-semibold">DevBerg</span>
                </div>
                <button onClick={() => setSidebarOpen(false)} className="text-gray-400 hover:text-gray-200">
                  <X className="h-5 w-5" />
                </button>
              </div>
              <nav className="flex-1 overflow-y-auto px-3 py-3 space-y-0.5">
                {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
                  <NavLink
                    key={to}
                    to={to}
                    end={to === "/"}
                    onClick={() => setSidebarOpen(false)}
                    className={({ isActive }) =>
                      `flex items-center gap-2.5 rounded-lg px-3 py-2 text-[13px] font-medium transition-all duration-150 ${
                        isActive
                          ? "bg-blue-500/10 text-blue-400"
                          : "text-gray-500 hover:bg-gray-800/50 hover:text-gray-300"
                      }`
                    }
                  >
                    <Icon className="h-4 w-4 shrink-0" />
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
        <header className="flex h-14 items-center gap-3 border-b border-gray-800/60 bg-gray-950/80 px-4 backdrop-blur-sm lg:px-6">
          <button onClick={() => setSidebarOpen(true)} className="lg:hidden text-gray-400 hover:text-gray-200">
            <Menu className="h-5 w-5" />
          </button>
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-gray-500" />
            <input
              type="text"
              placeholder="Search technologies..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full rounded-lg border border-gray-800/60 bg-gray-900/50 py-1.5 pl-9 pr-3 text-sm text-gray-300 placeholder-gray-600 outline-none transition-colors focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20"
            />
          </div>
          <div className="ml-auto flex items-center gap-3">
            <div className="h-7 w-7 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-[11px] font-semibold text-white">
              D
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2, ease: "easeOut" }}
            className="px-4 py-6 lg:px-8"
          >
            <Outlet />
          </motion.div>
        </main>
      </div>
    </div>
  );
}
