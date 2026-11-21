import React, { useState } from 'react';
import { Code2 } from 'lucide-react';

interface FixturePickerViewProps {
  onLoadFixture: (fixtureName: string) => void;
}

const FIXTURES = [
  { name: 'landing_page', emoji: '📷', label: 'Minimalist Studio' },
  { name: 'data_table', emoji: '📊', label: 'Analytics Dashboard' },
];

export const FixturePickerView: React.FC<FixturePickerViewProps> = ({ onLoadFixture }) => {
  const [open, setOpen] = useState(false);

  return (
    <div className="relative" onMouseEnter={() => setOpen(true)} onMouseLeave={() => setOpen(false)}>
      <button
        type="button"
        title="Load Deterministic Fixture"
        onClick={() => setOpen((value) => !value)}
        className="px-2.5 py-1.5 rounded-full bg-zinc-100 hover:bg-zinc-200/70 text-zinc-700 transition flex items-center gap-1.5 text-xs font-medium border border-zinc-200/60"
      >
        <Code2 className="w-3.5 h-3.5 text-zinc-600" />
        <span>Mẫu thử</span>
      </button>
      <div className={`absolute right-0 top-full mt-2 w-56 bg-white border border-zinc-200 rounded-2xl shadow-xl p-1.5 ${open ? 'block' : 'hidden'} z-50`}>
        <div className="text-[10px] font-semibold text-zinc-400 uppercase tracking-wider px-2.5 py-1.5">Offline Fixtures</div>
        {FIXTURES.map((fixture) => (
          <button
            key={fixture.name}
            type="button"
            onClick={() => { onLoadFixture(fixture.name); setOpen(false); }}
            className="w-full text-left px-2.5 py-2 rounded-xl text-xs text-zinc-800 hover:bg-zinc-100 transition flex items-center gap-2"
          >
            <span>{fixture.emoji}</span>
            <span>{fixture.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
};
