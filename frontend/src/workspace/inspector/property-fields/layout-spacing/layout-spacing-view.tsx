import React from 'react';

interface LayoutSpacingViewProps { value?: string; onChange: (value: string) => void; }
export const LayoutSpacingView: React.FC<LayoutSpacingViewProps> = ({ value = '', onChange }) => (
  <div className="space-y-1.5">
    <label className="text-[11px] font-medium text-zinc-700">Khoảng cách / Layout</label>
    <input type="text" value={value} onChange={(event) => onChange(event.target.value)} placeholder="Ví dụ: gap-4 p-6" className="w-full bg-zinc-50 focus:bg-white border border-zinc-200 focus:border-zinc-400 rounded-xl px-3.5 py-2.5 text-zinc-900 outline-none transition" />
  </div>
);
