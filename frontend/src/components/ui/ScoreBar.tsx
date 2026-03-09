export default function ScoreBar({ value, max = 100, className = "" }: { value: number; max?: number; className?: string }) {
  const pct = Math.min((value / max) * 100, 100);
  const color =
    pct >= 70 ? "bg-dp-accent" : pct >= 40 ? "bg-dp-warning" : "bg-dp-danger";

  return (
    <div className={`h-1.5 w-full rounded-full bg-dp-border ${className}`}>
      <div
        className={`h-1.5 rounded-full transition-all duration-500 ${color}`}
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}
