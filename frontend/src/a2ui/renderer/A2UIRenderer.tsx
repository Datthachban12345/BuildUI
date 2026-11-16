import React from 'react';
import { SurfaceState, ComponentId, A2UIComponentNode } from '../protocol/types';
import { ASTRYX_REGISTRY, AstryxFallbackComponent } from '../../catalog/adapters/astryxAdapter';

interface A2UIRendererProps {
  surface: SurfaceState;
  selectedId: ComponentId | null;
  onSelectComponent: (id: ComponentId | null) => void;
  onAction?: (actionName: string, payload?: any) => void;
  onUpdateDataModel?: (path: string, value: any) => void;
}

export const A2UIRenderer: React.FC<A2UIRendererProps> = ({
  surface,
  selectedId,
  onSelectComponent,
  onAction,
  onUpdateDataModel,
}) => {
  const renderNode = (nodeId: ComponentId): React.ReactNode => {
    const node: A2UIComponentNode | undefined = surface.components[nodeId];
    if (!node) return null;

    const ComponentImpl = ASTRYX_REGISTRY[node.component];
    const isSelected = selectedId === node.id;

    const childElements = node.children?.map(childId => renderNode(childId));

    const content = ComponentImpl ? (
      <ComponentImpl
        node={node}
        dataModel={surface.dataModel}
        onAction={onAction}
        onUpdateDataModel={onUpdateDataModel}
      >
        {childElements}
      </ComponentImpl>
    ) : (
      <AstryxFallbackComponent node={node} />
    );

    return (
      <div
        key={node.id}
        onClick={(e) => {
          e.stopPropagation();
          onSelectComponent(node.id);
        }}
        className={`relative transition-all duration-150 ${
          isSelected
            ? 'ring-2 ring-blue-500 ring-offset-2 ring-offset-zinc-950 rounded-lg'
            : 'hover:outline hover:outline-1 hover:outline-blue-500/40 rounded-lg'
        }`}
      >
        {isSelected && (
          <div className="absolute -top-3 left-2 px-1.5 py-0.5 rounded bg-blue-600 text-white font-mono text-[9px] uppercase tracking-wider z-20 pointer-events-none shadow-md">
            {node.component} #{node.id}
          </div>
        )}
        {content}
      </div>
    );
  };

  if (!surface.rootId || !surface.components[surface.rootId]) {
    return (
      <div className="p-8 text-center text-zinc-500 text-sm">
        Empty surface structure.
      </div>
    );
  }

  return (
    <div className="w-full h-full" onClick={() => onSelectComponent(null)}>
      {renderNode(surface.rootId)}
    </div>
  );
};
