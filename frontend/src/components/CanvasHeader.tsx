import React from 'react';
import {
  Monitor,
  Tablet,
  Smartphone,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Sparkles,
  Database,
  Layers,
  Sliders,
  Play,
  RotateCcw
} from 'lucide-react';
import { ViewportMode } from '../types/a2ui';

interface CanvasHeaderProps {
  viewport: ViewportMode;
  onViewportChange: (vp: ViewportMode) => void;
  zoom: number;
  onZoomChange: (zoom: number) => void;
  isStreaming: boolean;
  onStreamGeneration: (prompt: string) => void;
  onOpenDataModal: () => void;
  showLayers: boolean;
  onToggleLayers: () => void;
  showInspector: boolean;
  onToggleInspector: () => void;
  onResetCanvas: () => void;
}

export const CanvasHeader: React.FC<CanvasHeaderProps> = ({
  viewport,
  onViewportChange,
  zoom,
  onZoomChange,
  isStreaming,
  onStreamGeneration,
  onOpenDataModal,
  showLayers,
  onToggleLayers,
  showInspector,
  onToggleInspector,
  onResetCanvas
}) => {
  const [prompt, setPrompt] = React.useState('SaaS Analytics Dashboard with revenue metrics & customer data table');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!isStreaming && prompt.trim()) {
      onStreamGeneration(prompt.trim());
    }
  };

  return (
    <header className="h-14 border-b border-slate-800 bg-slate-900/90 backdrop-blur px-4 flex items-center justify-between gap-4 z-30 select-none">
      {/* Left: Brand & Sidebar Toggles */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 font-bold text-base text-white tracking-wide">
          <span className="w-7 h-7 rounded-lg bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white shadow-lg shadow-blue-500/20">
            ⚡
          </span>
          <span className="bg-gradient-to-r from-blue-400 via-indigo-300 to-purple-400 bg-clip-text text-transparent">
            A2UI Studio
          </span>
          <span className="text-xs px-2 py-0.5 rounded-full bg-blue-950 text-blue-400 border border-blue-800/60 font-mono">
            v1.0
          </span>
        </div>

        <div className="h-4 w-px bg-slate-800 mx-1" />

        <button
          onClick={onToggleLayers}
          title="Toggle Layers & Component Tree"
          className={`p-1.5 rounded-md text-xs flex items-center gap-1.5 transition ${
            showLayers
              ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
          }`}
        >
          <Layers className="w-4 h-4" />
          <span className="hidden sm:inline">Layers</span>
        </button>
      </div>

      {/* Middle: AI Prompt Bar */}
      <form onSubmit={handleSubmit} className="flex-1 max-w-xl">
        <div className="relative flex items-center">
          <Sparkles className="w-4 h-4 text-blue-400 absolute left-3 pointer-events-none" />
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            disabled={isStreaming}
            placeholder="Describe the website or interface to generate..."
            className="w-full bg-slate-950/80 border border-slate-800 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 rounded-lg pl-9 pr-28 py-1.5 text-xs text-slate-100 placeholder-slate-500 outline-none transition"
          />
          <button
            type="submit"
            disabled={isStreaming}
            className={`absolute right-1 px-3 py-1 rounded-md text-xs font-medium flex items-center gap-1.5 transition ${
              isStreaming
                ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-500 text-white shadow-sm'
            }`}
          >
            {isStreaming ? (
              <>
                <span className="w-3 h-3 border-2 border-slate-400 border-t-transparent rounded-full animate-spin" />
                <span>Streaming...</span>
              </>
            ) : (
              <>
                <Play className="w-3 h-3 fill-current" />
                <span>Stream Swarm</span>
              </>
            )}
          </button>
        </div>
      </form>

      {/* Right: Viewport, Data Import & Inspector Toggles */}
      <div className="flex items-center gap-2">
        {/* JSON / Data Import Button */}
        <button
          onClick={onOpenDataModal}
          className="px-2.5 py-1.5 rounded-md text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 flex items-center gap-1.5 transition"
          title="Import arbitrary JSON or Table Data to generate UI"
        >
          <Database className="w-3.5 h-3.5 text-emerald-400" />
          <span className="hidden md:inline">Data-to-UI</span>
        </button>

        <div className="h-4 w-px bg-slate-800 mx-1" />

        {/* Viewport Switcher */}
        <div className="flex items-center bg-slate-950 p-0.5 rounded-lg border border-slate-800">
          <button
            onClick={() => onViewportChange('desktop')}
            title="Desktop View (1440px)"
            className={`p-1.5 rounded-md transition ${
              viewport === 'desktop' ? 'bg-slate-800 text-blue-400' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Monitor className="w-4 h-4" />
          </button>
          <button
            onClick={() => onViewportChange('tablet')}
            title="Tablet View (768px)"
            className={`p-1.5 rounded-md transition ${
              viewport === 'tablet' ? 'bg-slate-800 text-blue-400' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Tablet className="w-4 h-4" />
          </button>
          <button
            onClick={() => onViewportChange('mobile')}
            title="Mobile View (375px)"
            className={`p-1.5 rounded-md transition ${
              viewport === 'mobile' ? 'bg-slate-800 text-blue-400' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Smartphone className="w-4 h-4" />
          </button>
        </div>

        {/* Zoom Controls */}
        <div className="hidden lg:flex items-center bg-slate-950 px-2 py-1 rounded-lg border border-slate-800 gap-1 text-xs text-slate-400">
          <button
            onClick={() => onZoomChange(Math.max(0.5, zoom - 0.1))}
            className="hover:text-slate-200"
            title="Zoom Out"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <span className="w-10 text-center font-mono text-slate-300">
            {Math.round(zoom * 100)}%
          </span>
          <button
            onClick={() => onZoomChange(Math.min(1.5, zoom + 0.1))}
            className="hover:text-slate-200"
            title="Zoom In"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => onZoomChange(1.0)}
            className="hover:text-slate-200 ml-1"
            title="Reset to 100%"
          >
            <Maximize2 className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Reset Canvas */}
        <button
          onClick={onResetCanvas}
          title="Reset Surface"
          className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-md transition"
        >
          <RotateCcw className="w-4 h-4" />
        </button>

        {/* Inspector Toggle */}
        <button
          onClick={onToggleInspector}
          title="Toggle Property Inspector"
          className={`p-1.5 rounded-md text-xs flex items-center gap-1.5 transition ${
            showInspector
              ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
          }`}
        >
          <Sliders className="w-4 h-4" />
          <span className="hidden sm:inline">Inspector</span>
        </button>
      </div>
    </header>
  );
};
