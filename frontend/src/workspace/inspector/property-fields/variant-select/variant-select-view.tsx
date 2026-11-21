import React from 'react';
import { Palette } from 'lucide-react';

interface VariantSelectViewProps { value: string; onChange: (value: string) => void; }
export const VariantSelectView: React.FC<VariantSelectViewProps> = ({ value, onChange }) => (
  <div className="space-y-1.5">
    <label className="text-[11px] font-medium text-zinc-700 flex items-center gap-1.5"><Palette className="w-3.5 h-3.5 text-zinc-400" />Kiểu dáng (Variant)</label>
    <select value={value} onChange={(event) => onChange(event.target.value)} className="w-full bg-zinc-50 focus:bg-white border border-zinc-200 focus:border-zinc-400 rounded-xl px-3.5 py-2.5 text-zinc-900 outline-none transition">
      <option value="primary">Primary (Apple Black)</option><option value="secondary">Secondary (Soft Gray)</option><option value="outline">Outline</option><option value="ghost">Ghost</option>
    </select>
  </div>
);
