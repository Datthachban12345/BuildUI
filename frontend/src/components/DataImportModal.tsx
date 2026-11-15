import React from 'react';
import { Database, Upload, FileJson, X, Play, Sparkles } from 'lucide-react';

interface DataImportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onImport: (data: any) => void;
}

const SAMPLE_JSON = `{
  "products": [
    { "id": "P-001", "name": "AI Web Agent Core", "price": 299, "status": "Active", "category": "AI Platform" },
    { "id": "P-002", "name": "Astryx Design Studio", "price": 149, "status": "Active", "category": "Design" },
    { "id": "P-003", "name": "Swarm Rebuilder Engine", "price": 499, "status": "Beta", "category": "Infrastructure" },
    { "id": "P-004", "name": "Data Schema Inference", "price": 99, "status": "Active", "category": "Data" },
    { "id": "P-005", "name": "Canvas Bridge SDK", "price": 199, "status": "Preview", "category": "SDK" }
  ],
  "summary": { "total_products": 5, "total_revenue": 1245, "active_rate": 0.6 }
}`;

export const DataImportModal: React.FC<DataImportModalProps> = ({ isOpen, onClose, onImport }) => {
  const [jsonText, setJsonText] = React.useState(SAMPLE_JSON);
  const [parseError, setParseError] = React.useState<string | null>(null);

  if (!isOpen) return null;

  const handleImport = () => {
    try {
      const parsed = JSON.parse(jsonText);
      setParseError(null);
      onImport(parsed);
      onClose();
    } catch (err: any) {
      setParseError(err.message);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (evt) => {
      const text = evt.target?.result as string;
      setJsonText(text);
      try {
        JSON.parse(text);
        setParseError(null);
      } catch (err: any) {
        setParseError(err.message);
      }
    };
    reader.readAsText(file);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-slate-900 border border-slate-700 rounded-xl shadow-2xl w-full max-w-2xl mx-4 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-emerald-600/20 flex items-center justify-center">
              <Database className="w-4.5 h-4.5 text-emerald-400" />
            </div>
            <div>
              <div className="text-sm font-semibold text-white">Data-to-UI Import</div>
              <div className="text-[11px] text-slate-500">Paste any JSON or upload a file — AI will infer schema and generate interactive UI</div>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-md transition">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="p-5 space-y-4">
          {/* Upload Button */}
          <div className="flex items-center gap-3">
            <label className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-dashed border-slate-700 hover:border-slate-600 cursor-pointer text-xs text-slate-400 hover:text-slate-200 transition">
              <Upload className="w-3.5 h-3.5" />
              Upload JSON File
              <input type="file" accept=".json,.csv,.txt" className="hidden" onChange={handleFileUpload} />
            </label>
            <span className="text-[10px] text-slate-600">or paste below</span>
          </div>

          {/* JSON Editor Area */}
          <div className="relative">
            <div className="absolute top-2 left-3 pointer-events-none">
              <FileJson className="w-4 h-4 text-slate-600" />
            </div>
            <textarea
              value={jsonText}
              onChange={(e) => {
                setJsonText(e.target.value);
                setParseError(null);
              }}
              rows={14}
              spellCheck={false}
              className={`w-full bg-slate-950 border rounded-lg pl-9 pr-4 py-3 text-xs text-slate-200 font-mono outline-none resize-none transition ${
                parseError ? 'border-red-500/60 focus:border-red-500' : 'border-slate-800 focus:border-blue-500'
              }`}
            />
            {parseError && (
              <div className="mt-1 text-[11px] text-red-400 flex items-center gap-1.5">
                <span className="w-1 h-1 rounded-full bg-red-400" />
                JSON Parse Error: {parseError}
              </div>
            )}
          </div>

          {/* Schema Preview Hint */}
          <div className="bg-slate-950 border border-slate-800 rounded-lg p-3 flex items-start gap-2.5">
            <Sparkles className="w-4 h-4 text-blue-400 mt-0.5 shrink-0" />
            <div className="text-[11px] text-slate-400 leading-relaxed">
              <strong className="text-slate-300">Schema Inference Engine</strong> will detect field types
              (strings, numbers, dates, status enums, URLs) and auto-select the best UI paradigm:
              DataTable, MetricsCards, Card Grid, Filter Bar, or Detail Drawer.
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 px-5 py-3.5 border-t border-slate-800 bg-slate-900/50">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition"
          >
            Cancel
          </button>
          <button
            onClick={handleImport}
            className="px-4 py-1.5 rounded-lg text-xs font-medium bg-emerald-600 hover:bg-emerald-500 text-white shadow-sm flex items-center gap-1.5 transition"
          >
            <Play className="w-3 h-3 fill-current" />
            Generate UI from Data
          </button>
        </div>
      </div>
    </div>
  );
};
