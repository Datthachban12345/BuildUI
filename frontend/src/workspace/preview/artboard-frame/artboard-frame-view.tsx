import React from 'react';
import { SurfaceState, ComponentId } from '../../../a2ui/protocol/a2ui-types';
import { A2UIRendererView } from '../../../a2ui/renderer/a2ui-renderer-view';

interface ArtboardFrameViewProps {
  surface: SurfaceState;
  selectedId: ComponentId | null;
  widthClass: string;
  zoom: number;
  onSelectComponent: (id: ComponentId | null) => void;
  onAction?: (actionName: string, payload?: any) => void;
  onUpdateDataModel?: (path: string, value: any) => void;
}

export const ArtboardFrameView: React.FC<ArtboardFrameViewProps> = ({ surface, selectedId, widthClass, zoom, onSelectComponent, onAction, onUpdateDataModel }) => (
  <div className={`w-full ${widthClass} bg-white border border-zinc-200/90 rounded-3xl shadow-[0_24px_70px_rgba(0,0,0,0.08)] overflow-hidden transition-all duration-300`} style={{ transform: `scale(${zoom})`, transformOrigin: 'top center' }}>
    <div className="min-h-[720px] p-2 bg-white">
      <A2UIRendererView surface={surface} selectedId={selectedId} onSelectComponent={onSelectComponent} onAction={onAction} onUpdateDataModel={onUpdateDataModel} />
    </div>
  </div>
);
