import { useState } from "react";
import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Radar,
  HeartPulse,
  TrendingUp,
  Mountain,
  Menu,
  X,
} from "lucide-react";

const links = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/radar", label: "Tech Radar", icon: Radar },
  { to: "/health", label: "Repo Health", icon: HeartPulse },
  { to: "/forecast", label: "Forecast", icon: TrendingUp },
];

export default function MobileNav() {
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 flex h-14 items-center gap-3 border-b border-gray-800 bg-gray-950/80 backdrop-blur px-4 lg:hidden">
      <button onClick={() => setOpen(!open)} className="text-gray-300">
        {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
      </button>
      <Mountain className="h-5 w-5 text-brand-400" />
      <span className="text-sm font-semibold">DevBerg</span>

      {open && (
        <nav className="absolute top-14 left-0 w-full border-b border-gray-800 bg-gray-950 p-3 space-y-1">
          {links.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              onClick={() => setOpen(false)}
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
      )}
    </header>
  );
}
