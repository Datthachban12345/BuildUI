import { useState } from 'react';

export type ViewportMode = 'desktop' | 'tablet' | 'mobile';

export function useViewportBarStore() {
  const [viewport, setViewport] = useState<ViewportMode>('desktop');
  const [zoom, setZoom] = useState<number>(0.9);

  const zoomIn = () => setZoom((z) => Math.min(1.5, z + 0.1));
  const zoomOut = () => setZoom((z) => Math.max(0.5, z - 0.1));
  const resetZoom = () => setZoom(0.9);

  return {
    viewport,
    setViewport,
    zoom,
    setZoom,
    zoomIn,
    zoomOut,
    resetZoom,
  };
}
