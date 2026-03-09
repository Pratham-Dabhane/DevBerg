import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface Props {
  direction: string;
  value?: number;
  className?: string;
}

export default function TrendIndicator({ direction, value, className = "" }: Props) {
  if (direction === "up" || direction === "accelerating") {
    return (
      <span className={`inline-flex items-center gap-1 text-emerald-400 ${className}`}>
        <TrendingUp className="h-3.5 w-3.5" />
        {value !== undefined && <span className="text-xs font-medium">+{value.toFixed(1)}%</span>}
      </span>
    );
  }
  if (direction === "down" || direction === "declining" || direction === "decelerating") {
    return (
      <span className={`inline-flex items-center gap-1 text-red-400 ${className}`}>
        <TrendingDown className="h-3.5 w-3.5" />
        {value !== undefined && <span className="text-xs font-medium">{value.toFixed(1)}%</span>}
      </span>
    );
  }
  return (
    <span className={`inline-flex items-center gap-1 text-gray-500 ${className}`}>
      <Minus className="h-3.5 w-3.5" />
      {value !== undefined && <span className="text-xs font-medium">{value.toFixed(1)}%</span>}
    </span>
  );
}
