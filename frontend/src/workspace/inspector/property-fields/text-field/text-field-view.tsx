import React from 'react';
import { Type } from 'lucide-react';

interface TextFieldViewProps { label: string; value: string; multiline?: boolean; onChange: (value: string) => void; }

export const TextFieldView: React.FC<TextFieldViewProps> = ({ label, value, multiline, onChange }) => (
  <div className="space-y-1.5">
    <label className="text-[11px] font-medium text-zinc-700 flex items-center gap-1.5"><Type className="w-3.5 h-3.5 text-zinc-400" />{label}</label>
    {multiline ? <textarea rows={3} value={value} onChange={(event) => onChange(event.target.value)} className="w-full bg-zinc-50 focus:bg-white border border-zinc-200 focus:border-zinc-400 rounded-xl p-3 text-zinc-900 outline-none resize-none transition" /> : <input type="text" value={value} onChange={(event) => onChange(event.target.value)} className="w-full bg-zinc-50 focus:bg-white border border-zinc-200 focus:border-zinc-400 rounded-xl px-3.5 py-2.5 text-zinc-900 outline-none transition" />}
  </div>
);
