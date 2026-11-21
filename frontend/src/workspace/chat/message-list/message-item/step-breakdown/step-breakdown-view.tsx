import React from 'react';
import { CheckCircle2 } from 'lucide-react';

interface StepBreakdownViewProps {
  steps: string[];
}

export const StepBreakdownView: React.FC<StepBreakdownViewProps> = ({ steps }) => (
  <div className="mt-3 pt-3 border-t border-zinc-100 space-y-2 text-[11px]">
    <div className="text-[10px] uppercase text-zinc-400 font-semibold tracking-wider">Tiến trình triển khai:</div>
    {steps.map((step, index) => (
      <div key={`${step}-${index}`} className="flex items-center gap-2 text-zinc-700">
        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
        <span className="leading-tight">{step}</span>
      </div>
    ))}
  </div>
);
