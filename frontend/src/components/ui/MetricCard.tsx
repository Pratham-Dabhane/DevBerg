import { motion } from "framer-motion";
import type { ReactNode } from "react";

interface Props {
  label: string;
  value: string | number;
  change?: number;
  icon?: ReactNode;
  className?: string;
}

export default function MetricCard({ label, value, change, icon, className = "" }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className={`dp-card p-4 ${className}`}
    >
      <div className="flex items-center justify-between">
        <p className="text-[11px] font-medium text-dp-text-3 uppercase tracking-wider">{label}</p>
        {icon && <div className="text-dp-text-4">{icon}</div>}
      </div>
      <p className="mt-2 text-2xl font-bold tracking-tight text-dp-text">{value}</p>
      {change !== undefined && (
        <p className={`mt-1 text-xs font-medium ${change >= 0 ? "text-dp-accent" : "text-dp-danger"}`}>
          {change >= 0 ? "+" : ""}
          {change.toFixed(1)}%
        </p>
      )}
    </motion.div>
  );
}
