import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Radar,
  HeartPulse,
  TrendingUp,
  Mountain,
} from "lucide-react";

const links = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/radar", label: "Tech Radar", icon: Radar },
  { to: "/health", label: "Repo Health", icon: HeartPulse },
  { to: "/forecast", label: "Forecast", icon: TrendingUp },
];

export default function Sidebar() {
  return (
    <aside className="fixed inset-y-0 left-0 z-30 hidden w-56 flex-col border-r border-gray-800 bg-gray-950 lg:flex">
      {/* Brand */}
      <div className="flex h-16 items-center gap-2 px-5 border-b border-gray-800">
        <Mountain className="h-6 w-6 text-brand-400" />
        <span className="text-lg font-semibold tracking-tight">DevBerg</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                isActive
                  ? "bg-brand-600/15 text-brand-400"
                  : "text-gray-400 hover:bg-gray-800/60 hover:text-gray-200"
              }`
            }
          >
            <Icon className="h-4 w-4" />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-gray-800 px-5 py-4">
        <p className="text-xs text-gray-500">DevBerg v1.0</p>
      </div>
    </aside>
  );
}
