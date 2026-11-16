import React from 'react';
import { SurfaceState, ComponentId } from '../../a2ui/protocol/types';
import { A2UIRenderer } from '../../a2ui/renderer/A2UIRenderer';
import { Monitor, Tablet, Smartphone, ZoomIn, ZoomOut, Maximize2, Sparkles, Layers } from 'lucide-react';

export type ViewportMode = 'desktop' | 'tablet' | 'mobile';

interface PreviewCanvasProps {
  surface: SurfaceState | null;
  selectedId: ComponentId | null;
  onSelectComponent: (id: ComponentId | null) => void;
  onAction?: (actionName: string, payload?: any) => void;
  onUpdateDataModel?: (path: string, value: any) => void;
  isGenerating: boolean;
}

export const PreviewCanvas: React.FC<PreviewCanvasProps> = ({
  surface,
  selectedId,
  onSelectComponent,
  onAction,
  onUpdateDataModel,
  isGenerating
}) => {
  const [viewport, setViewport] = React.useState<ViewportMode>('desktop');
  const [zoom, setZoom] = React.useState(0.9);

  const viewportWidths: Record<ViewportMode, string> = {
    desktop: 'max-w-[1280px]',
    tablet: 'max-w-[768px]',
    mobile: 'max-w-[390px]',
  };

  return (
    <main className="flex-1 flex flex-col h-full bg-zinc-950 overflow-hidden select-none">
      {/* Top Canvas Bar */}
      <div className="h-14 px-6 border-b border-zinc-800/80 bg-zinc-950/90 backdrop-blur flex items-center justify-between z-10">
        <div className="flex items-center gap-3">
          <span className="text-xs font-medium text-zinc-300">
            {surface ? surface.title : 'Live Canvas Artboard'}
          </span>
          {surface && (
            <span className="px-2 py-0.5 rounded-full text-[10px] bg-zinc-900 border border-zinc-800 text-zinc-400 font-mono">
              {Object.keys(surface.components).length} components
            </span>
          )}
        </div>

        {/* Viewport Switcher */}
        <div className="flex items-center gap-1 p-1 bg-zinc-900/80 rounded-lg border border-zinc-800">
          <button
            onClick={() => setViewport('desktop')}
            title="Desktop View"
            className={`p-1.5 rounded-md transition ${viewport === 'desktop' ? 'bg-zinc-800 text-white' : 'text-zinc-400 hover:text-zinc-200'}`}
          >
            <Monitor className="w-4 h-4" />
          </button>
          <button
            onClick={() => setViewport('tablet')}
            title="Tablet View"
            className={`p-1.5 rounded-md transition ${viewport === 'tablet' ? 'bg-zinc-800 text-white' : 'text-zinc-400 hover:text-zinc-200'}`}
          >
            <Tablet className="w-4 h-4" />
          </button>
          <button
            onClick={() => setViewport('mobile')}
            title="Mobile View"
            className={`p-1.5 rounded-md transition ${viewport === 'mobile' ? 'bg-zinc-800 text-white' : 'text-zinc-400 hover:text-zinc-200'}`}
          >
            <Smartphone className="w-4 h-4" />
          </button>
        </div>

        {/* Zoom Controls */}
        <div className="flex items-center gap-2 text-xs text-zinc-400">
          <button
            onClick={() => setZoom(Math.max(0.5, zoom - 0.1))}
            className="p-1.5 hover:text-white rounded hover:bg-zinc-900"
            title="Zoom Out"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <span className="font-mono text-zinc-300 w-10 text-center">{Math.round(zoom * 100)}%</span>
          <button
            onClick={() => setZoom(Math.min(1.5, zoom + 0.1))}
            className="p-1.5 hover:text-white rounded hover:bg-zinc-900"
            title="Zoom In"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => setZoom(0.9)}
            className="p-1.5 hover:text-white rounded hover:bg-zinc-900"
            title="Reset Zoom"
          >
            <Maximize2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Canvas Viewport Scroll Area */}
      <div className="flex-1 overflow-auto p-8 flex items-start justify-center bg-zinc-950/60">
        {!surface ? (
          /* Empty Canvas Placeholder */
          <div className="my-auto max-w-md text-center p-8 rounded-2xl border border-dashed border-zinc-800 bg-zinc-900/20 space-y-4">
            <div className="w-16 h-16 rounded-2xl bg-zinc-900 border border-zinc-800 flex items-center justify-center mx-auto text-zinc-400 shadow-xl">
              <Sparkles className="w-7 h-7 text-zinc-300" />
            </div>
            <div>
              <h3 className="text-base font-medium text-white mb-1.5">Canvas Artboard đang trống</h3>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Nhập yêu cầu vào khung chat bên trái (ví dụ: <em>"Tạo landing page cho studio chụp ảnh"</em>). Agent sẽ lập cấu trúc trang và sinh website tương tác trực tiếp lên đây.
              </p>
            </div>
            {isGenerating && (
              <div className="pt-2 flex items-center justify-center gap-2 text-xs text-amber-400">
                <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping" />
                <span>Agent đang dựng cấu trúc trang...</span>
              </div>
            )}
          </div>
        ) : (
          /* Live Interactive Surface Artboard */
          <div
            className={`w-full ${viewportWidths[viewport]} bg-zinc-950 border border-zinc-800/80 rounded-2xl shadow-2xl overflow-hidden transition-all duration-300`}
            style={{
              transform: `scale(${zoom})`,
              transformOrigin: 'top center',
            }}
          >
            <div className="min-h-[700px] p-2">
              <A2UIRenderer
                surface={surface}
                selectedId={selectedId}
                onSelectComponent={onSelectComponent}
                onAction={onAction}
                onUpdateDataModel={onUpdateDataModel}
              />
            </div>
          </div>
        )}
      </div>
    </main>
  );
};
