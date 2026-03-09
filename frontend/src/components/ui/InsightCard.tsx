import { motion } from "framer-motion";

interface Props {
  technology: string;
  severity: string;
  insight: string;
  category: string;
}

const severityColors: Record<string, string> = {
  critical: "border-dp-danger/25 bg-dp-danger/5",
  warning: "border-dp-warning/25 bg-dp-warning/5",
  info: "border-dp-secondary/25 bg-dp-secondary/5",
};

const severityDot: Record<string, string> = {
  critical: "bg-dp-danger",
  warning: "bg-dp-warning",
  info: "bg-dp-secondary",
};

export default function InsightCard({ technology, severity, insight, category }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      className={`rounded-lg border p-4 ${severityColors[severity] ?? severityColors.info}`}
    >
      <div className="flex items-center gap-2 mb-2">
        <span className={`h-2 w-2 rounded-full ${severityDot[severity] ?? severityDot.info}`} />
        <span className="text-sm font-medium text-dp-text">{technology}</span>
        <span className="ml-auto text-[10px] uppercase tracking-wider text-dp-text-3 font-medium">{category}</span>
      </div>
      <p className="text-sm text-dp-text-2 leading-relaxed">{insight}</p>
    </motion.div>
  );
}
