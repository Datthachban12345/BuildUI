import React from 'react';
import { SurfaceState, ComponentId } from '../../a2ui/protocol/a2ui-types';
import { A2UIRendererView } from '../../a2ui/renderer/a2ui-renderer-view';
import { Sparkles } from 'lucide-react';
import { ViewportBarView } from './viewport-bar/viewport-bar-view';
import { usePreviewStore } from './preview-store';

export interface PreviewViewProps {
  surface: SurfaceState | null;
  selectedId: ComponentId | null;
  onSelectComponent: (id: ComponentId | null) => void;
  onAction?: (actionName: string, payload?: any) => void;
  onUpdateDataModel?: (path: string, value: any) => void;
  isGenerating: boolean;
}

export const PreviewView: React.FC<PreviewViewProps> = ({
  surface,
  selectedId,
  onSelectComponent,
  onAction,
  onUpdateDataModel,
  isGenerating,
}) => {
  const {
    viewport,
    setViewport,
    zoom,
    zoomIn,
    zoomOut,
    resetZoom,
    viewportWidths,
  } = usePreviewStore();

  return (
    <main className="flex-1 flex flex-col h-full bg-[#f5f5f7] overflow-hidden select-none">
      {/* Top Canvas Bar */}
      <ViewportBarView
        title={surface ? surface.title : 'Live Preview Canvas'}
        componentCount={surface ? Object.keys(surface.components).length : undefined}
        viewport={viewport}
        onViewportChange={setViewport}
        zoom={zoom}
        onZoomIn={zoomIn}
        onZoomOut={zoomOut}
        onResetZoom={resetZoom}
      />

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
              <A2UIRendererView
                surface={surface}
                selectedId={selectedId}
                onSelectComponent={onSelectComponent}
                onAction={onAction}
                onUpdateDataModel={onUpdateDataModel}
                isGenerating={isGenerating}
              />
            </div>
          </div>
        )}
      </div>
    </main>
  );
};
