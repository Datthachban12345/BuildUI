import { useCallback } from 'react';
import { SurfaceState, ComponentId, A2UIComponentNode } from '../../a2ui/protocol/a2ui-types';

export interface InspectorStoreProps {
  surface: SurfaceState | null;
  selectedId: ComponentId | null;
  onUpdateComponent: (component: A2UIComponentNode) => void;
}

export function useInspectorStore({ surface, selectedId, onUpdateComponent }: InspectorStoreProps) {
  const node = surface && selectedId ? surface.components[selectedId] : null;
  const props = node?.props || {};

  const handlePropChange = useCallback(
    (key: string, value: any) => {
      if (!node) return;
      onUpdateComponent({
        ...node,
        props: {
          ...props,
          [key]: value,
        },
      });
    },
    [node, props, onUpdateComponent]
  );

  return {
    node,
    props,
    handlePropChange,
  };
}
