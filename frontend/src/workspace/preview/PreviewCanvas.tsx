import React from 'react';
import { SurfaceState, ComponentId } from '../../a2ui/protocol/types';
import { A2UIRenderer } from '../../a2ui/renderer/A2UIRenderer';
import { Monitor, Tablet, Smartphone, ZoomIn, ZoomOut, Maximize2, Sparkles } from 'lucide-react';

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
    desktop: 'max-w-[1240px]',
    tablet: 'max-w-[768px]',
    mobile: 'max-w-[390px]',
  };

  return (
    <main className="flex-1 flex flex-col h-full bg-[#f5f5f7] overflow-hidden select-none">
      {/* Top Canvas Bar - Apple frosted bar */}
      <div className="h-16 px-6 border-b border-zinc-200/80 bg-white/80 backdrop-blur-md flex items-center justify-between z-10">
        <div className="flex items-center gap-3">
          <span className="text-sm font-semibold tracking-tight text-zinc-900">
            {surface ? surface.title : 'Live Preview Canvas'}
          </span>
          {surface && (
            <span className="px-2.5 py-0.5 rounded-full text-[11px] bg-zinc-100 border border-zinc-200 text-zinc-600 font-medium">
              {Object.keys(surface.components).length} components
            </span>
          )}
        </div>

        {/* Viewport Segmented Control (Apple style) */}
        <div className="flex items-center p-1 bg-zinc-100 rounded-full border border-zinc-200/60 shadow-inner">
          <button
            onClick={() => setViewport('desktop')}
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
            onClick={() => setViewport('tablet')}
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
            onClick={() => setViewport('mobile')}
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
          <button
            onClick={() => setZoom(Math.max(0.5, zoom - 0.1))}
            className="p-1 hover:text-zinc-950 transition"
            title="Thu nhỏ"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <span className="font-mono text-zinc-800 w-9 text-center font-medium">{Math.round(zoom * 100)}%</span>
          <button
            onClick={() => setZoom(Math.min(1.5, zoom + 0.1))}
            className="p-1 hover:text-zinc-950 transition"
            title="Phóng to"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => setZoom(0.9)}
            className="p-1 hover:text-zinc-950 transition ml-1"
            title="Đặt lại 100%"
          >
            <Maximize2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Canvas Viewport Scroll Area */}
      <div className="flex-1 overflow-auto p-10 flex items-start justify-center">
        {!surface ? (
          /* Apple-style Empty Canvas */
          <div className="my-auto max-w-md text-center p-10 rounded-3xl border border-zinc-200/80 bg-white shadow-[0_4px_24px_rgba(0,0,0,0.04)] space-y-4">
            <div className="w-16 h-16 rounded-3xl bg-zinc-50 border border-zinc-200/80 flex items-center justify-center mx-auto text-zinc-900 shadow-sm">
              <Sparkles className="w-7 h-7 text-zinc-800" />
            </div>
            <div>
              <h3 className="text-base font-semibold text-zinc-900 tracking-tight mb-1.5">Không gian vẽ trống</h3>
              <p className="text-xs text-zinc-500 leading-relaxed">
                Nhập yêu cầu vào khung chat bên trái (ví dụ: <em>"Tạo landing page cho studio chụp ảnh tối giản"</em>). Agent sẽ lập kế hoạch và dựng giao diện trực tiếp lên màn hình này.
              </p>
            </div>
            {isGenerating && (
              <div className="pt-3 flex items-center justify-center gap-2 text-xs text-zinc-700 font-medium">
                <span className="w-2 h-2 rounded-full bg-zinc-900 animate-ping" />
                <span>Agent đang dựng cấu trúc trang...</span>
              </div>
            )}
          </div>
        ) : (
          /* Live Interactive Surface Artboard - Apple floating display */
          <div
            className={`w-full ${viewportWidths[viewport]} bg-white border border-zinc-200/90 rounded-3xl shadow-[0_24px_70px_rgba(0,0,0,0.08)] overflow-hidden transition-all duration-300`}
            style={{
              transform: `scale(${zoom})`,
              transformOrigin: 'top center',
            }}
          >
            <div className="min-h-[720px] p-2 bg-white">
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
