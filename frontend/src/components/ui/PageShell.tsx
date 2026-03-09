import { motion } from "framer-motion";

export function PageSpinner() {
  return (
    <div className="flex flex-col items-center justify-center py-32 gap-3">
      <div className="relative h-8 w-8">
        <div className="absolute inset-0 rounded-full border-2 border-dp-border" />
        <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-dp-accent animate-spin" />
      </div>
      <span className="text-xs text-dp-text-4">Loading&hellip;</span>
    </div>
  );
}

export function PageError({ message }: { message: string }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="rounded-lg border border-dp-danger/25 bg-dp-danger/5 px-4 py-3 text-sm text-dp-danger"
    >
      {message}
    </motion.div>
  );
}

export function SectionCard({
  title,
  subtitle,
  children,
  className = "",
  action,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  className?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className={`dp-card ${className}`}>
      <div className="flex items-center justify-between border-b border-dp-border/60 px-5 py-3">
        <div>
          <h3 className="text-sm font-semibold text-dp-text">{title}</h3>
          {subtitle && <p className="mt-0.5 text-xs text-dp-text-3">{subtitle}</p>}
        </div>
        {action}
      </div>
      <div className="p-5">{children}</div>
    </div>
  );
}

export function ChartTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="dp-tooltip rounded-lg px-3 py-2 text-xs">
      <p className="font-medium text-dp-text mb-1">{label}</p>
      {payload.map((p: any) => (
        <p key={p.dataKey} style={{ color: p.color }} className="flex items-center gap-1.5">
          <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: p.color }} />
          {p.name}: {typeof p.value === "number" ? p.value.toFixed(2) : p.value}
        </p>
      ))}
    </div>
  );
}
