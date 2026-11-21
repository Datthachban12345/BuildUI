import { useViewportBarStore, ViewportMode } from './viewport-bar/viewport-bar-store';

export const VIEWPORT_WIDTHS: Record<ViewportMode, string> = {
  desktop: 'max-w-[1240px]',
  tablet: 'max-w-[768px]',
  mobile: 'max-w-[390px]',
};

export function usePreviewStore() {
  const viewportControls = useViewportBarStore();

  return {
    ...viewportControls,
    viewportWidths: VIEWPORT_WIDTHS,
  };
}
