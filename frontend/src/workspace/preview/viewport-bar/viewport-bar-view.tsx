import React from 'react';
import { Monitor, Tablet, Smartphone, ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';
import { ViewportMode } from './viewport-bar-store';

export interface ViewportBarViewProps {
  title: string;
  componentCount?: number;
  viewport: ViewportMode;
  onViewportChange: (mode: ViewportMode) => void;
  zoom: number;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onResetZoom: () => void;
}

export const ViewportBarView: React.FC<ViewportBarViewProps> = ({
  title,
  componentCount,
  viewport,
  onViewportChange,
  zoom,
  onZoomIn,
  onZoomOut,
  onResetZoom,
}) => {
  return (
    <div className="h-16 px-6 border-b border-zinc-200/80 bg-white/80 backdrop-blur-md flex items-center justify-between z-10 shrink-0">
      <div className="flex items-center gap-3">
        <span className="text-sm font-semibold tracking-tight text-zinc-900">{title}</span>
        {componentCount !== undefined && (
          <span className="px-2.5 py-0.5 rounded-full text-[11px] bg-zinc-100 border border-zinc-200 text-zinc-600 font-medium">
            {componentCount} components
          </span>
        )}
      </div>

      {/* Viewport Segmented Control (Apple style) */}
      <div className="flex items-center p-1 bg-zinc-100 rounded-full border border-zinc-200/60 shadow-inner">
        <button
          onClick={() => onViewportChange('desktop')}
          title="Desktop View"
          className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
            viewport === 'desktop' ? 'bg-white text-zinc-950 shadow-sm' : 'text-zinc-500 hover:text-zinc-900'
          }`}
        >
          <div className="flex items-center gap-1.5">
            <Monitor className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Desktop</span>
          </div>
        </button>
        <button
          onClick={() => onViewportChange('tablet')}
          title="Tablet View"
          className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
            viewport === 'tablet' ? 'bg-white text-zinc-950 shadow-sm' : 'text-zinc-500 hover:text-zinc-900'
          }`}
        >
          <div className="flex items-center gap-1.5">
            <Tablet className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Tablet</span>
          </div>
        </button>
        <button
          onClick={() => onViewportChange('mobile')}
          title="Mobile View"
          className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
            viewport === 'mobile' ? 'bg-white text-zinc-950 shadow-sm' : 'text-zinc-500 hover:text-zinc-900'
          }`}
        >
          <div className="flex items-center gap-1.5">
            <Smartphone className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Mobile</span>
          </div>
        </button>
      </div>

      {/* Zoom Controls */}
      <div className="flex items-center gap-1.5 text-xs text-zinc-600 bg-zinc-100 px-3 py-1.5 rounded-full border border-zinc-200/60">
        <button onClick={onZoomOut} className="p-1 hover:text-zinc-950 transition" title="Thu nhỏ">
          <ZoomOut className="w-3.5 h-3.5" />
        </button>
        <span className="font-mono text-zinc-800 w-9 text-center font-medium">{Math.round(zoom * 100)}%</span>
        <button onClick={onZoomIn} className="p-1 hover:text-zinc-950 transition" title="Phóng to">
          <ZoomIn className="w-3.5 h-3.5" />
        </button>
        <button onClick={onResetZoom} className="p-1 hover:text-zinc-950 transition ml-1" title="Đặt lại 100%">
          <Maximize2 className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};
