import { motion } from "framer-motion";

interface Props {
  technology: string;
  severity: string;
  insight: string;
  category: string;
}

const severityColors: Record<string, string> = {
  critical: "border-red-500/30 bg-red-500/5",
  warning: "border-amber-500/30 bg-amber-500/5",
  info: "border-blue-500/30 bg-blue-500/5",
};

const severityDot: Record<string, string> = {
  critical: "bg-red-400",
  warning: "bg-amber-400",
  info: "bg-blue-400",
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
        <span className="text-sm font-medium text-gray-200">{technology}</span>
        <span className="ml-auto text-[10px] uppercase tracking-wider text-gray-500 font-medium">{category}</span>
      </div>
      <p className="text-sm text-gray-400 leading-relaxed">{insight}</p>
    </motion.div>
  );
}
