import React from 'react';
import { SurfaceState, ComponentId, A2UIComponentNode } from '../protocol/a2ui-types';
import { ASTRYX_REGISTRY, AstryxFallbackComponent } from '../../catalog/adapters/astryx-adapter-view';

interface A2UIRendererProps {
  surface: SurfaceState;
  selectedId: ComponentId | null;
  onSelectComponent: (id: ComponentId | null) => void;
  onAction?: (actionName: string, payload?: any) => void;
  onUpdateDataModel?: (path: string, value: any) => void;
  /** While true, section containers awaiting their Live Assembly block shimmer. */
  isGenerating?: boolean;
}

/** Apple-style shimmer bar used by pending Live Assembly sections. */
const ShimmerBar: React.FC<{ width: string }> = ({ width }) => (
  <div className={`h-3 rounded-full bg-zinc-100 animate-pulse ${width}`} />
);

export const A2UIRendererView: React.FC<A2UIRendererProps> = ({
  surface,
  selectedId,
  onSelectComponent,
  onAction,
  onUpdateDataModel,
  isGenerating = false,
}) => {
  const renderNode = (nodeId: ComponentId): React.ReactNode => {
    const node: A2UIComponentNode | undefined = surface.components[nodeId];
    if (!node) return null;

    const ComponentImpl = ASTRYX_REGISTRY[node.component];
    const isSelected = selectedId === node.id;

    const childElements = node.children?.map(childId => renderNode(childId));
    // Live Assembly: while the agent is streaming, a section container that
    // has not received its children block yet renders a shimmer placeholder.
    const isPendingSection =
      isGenerating &&
      node.component === 'Container' &&
      (node.children === undefined || node.children.length === 0);

    let content: React.ReactNode;
    if (!ComponentImpl) {
      content = <AstryxFallbackComponent node={node} />;
    } else if (isPendingSection && (childElements?.length ?? 0) === 0) {
      // Shimmer skeleton while the block for this section is still streaming.
      content = (
        <div
          className="w-full p-8 space-y-4"
          style={{ minHeight: 120 }}
          aria-busy="true"
        >
          <div className="flex items-center gap-2 text-[11px] font-medium text-zinc-400 uppercase tracking-wider">
            <span className="w-2 h-2 rounded-full bg-zinc-300 animate-pulse" />
            Đang lắp ráp khối...
          </div>
          <ShimmerBar width="w-1/3" />
          <ShimmerBar width="w-2/3" />
          <ShimmerBar width="w-full" />
        </div>
      );
    } else {
      content = (
        <ComponentImpl
          node={node}
          dataModel={surface.dataModel}
          onAction={onAction}
          onUpdateDataModel={onUpdateDataModel}
        >
          {childElements}
        </ComponentImpl>
      );
    }

    return (
      <div
        key={node.id}
        onClick={(e) => {
          e.stopPropagation();
          onSelectComponent(node.id);
        }}
        className={`relative transition-all duration-150 ${
          isSelected
            ? 'ring-2 ring-zinc-950 ring-offset-2 ring-offset-white rounded-2xl'
            : 'hover:outline hover:outline-1 hover:outline-zinc-300 rounded-2xl'
        }`}
      >
        {isSelected && (
          <div className="absolute -top-3 left-3 px-2 py-0.5 rounded-full bg-zinc-900 text-white font-mono text-[9px] uppercase tracking-wider z-20 pointer-events-none shadow-md">
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
