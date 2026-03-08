import type { ReactNode } from "react";

interface Props {
  title: string;
  subtitle?: string;
  children: ReactNode;
  className?: string;
}

export default function Card({ title, subtitle, children, className = "" }: Props) {
  return (
    <div className={`rounded-xl border border-gray-800 bg-gray-900/60 ${className}`}>
      <div className="border-b border-gray-800 px-5 py-3.5">
        <h3 className="text-sm font-semibold text-gray-100">{title}</h3>
        {subtitle && <p className="mt-0.5 text-xs text-gray-500">{subtitle}</p>}
      </div>
      <div className="p-5">{children}</div>
    </div>
  );
}
