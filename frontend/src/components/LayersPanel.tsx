import React from 'react';
import { ComponentNode, SurfaceState, ComponentId } from '../types/a2ui';
import { ChevronRight, ChevronDown, Box, Type, MousePointer2, Layout, Image, Table, BarChart3 } from 'lucide-react';

interface LayersPanelProps {
  surface: SurfaceState | null;
  selectedId: ComponentId | null;
  onSelect: (id: ComponentId | null) => void;
  onHover: (id: ComponentId | null) => void;
}

const COMPONENT_ICONS: Record<string, React.ReactNode> = {
  Container: <Layout className="w-3.5 h-3.5 text-blue-400" />,
  Row: <Layout className="w-3.5 h-3.5 text-cyan-400" />,
  Column: <Layout className="w-3.5 h-3.5 text-cyan-400" />,
  Grid: <Layout className="w-3.5 h-3.5 text-indigo-400" />,
  Heading: <Type className="w-3.5 h-3.5 text-amber-400" />,
  Text: <Type className="w-3.5 h-3.5 text-amber-300" />,
  Button: <MousePointer2 className="w-3.5 h-3.5 text-green-400" />,
  Card: <Box className="w-3.5 h-3.5 text-purple-400" />,
  Image: <Image className="w-3.5 h-3.5 text-pink-400" />,
  DataTable: <Table className="w-3.5 h-3.5 text-emerald-400" />,
  MetricsCard: <BarChart3 className="w-3.5 h-3.5 text-orange-400" />,
};

const LayerNode: React.FC<{
  node: ComponentNode;
  components: Record<ComponentId, ComponentNode>;
  depth: number;
  selectedId: ComponentId | null;
  onSelect: (id: ComponentId | null) => void;
  onHover: (id: ComponentId | null) => void;
}> = ({ node, components, depth, selectedId, onSelect, onHover }) => {
  const [expanded, setExpanded] = React.useState(true);
  const hasChildren = node.children && node.children.length > 0;
  const isSelected = selectedId === node.id;

  return (
    <div>
      <div
        className={`flex items-center gap-1 px-2 py-1 cursor-pointer text-xs transition-colors ${
          isSelected
            ? 'bg-blue-600/20 text-blue-300 border-l-2 border-blue-500'
            : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 border-l-2 border-transparent'
        }`}
        style={{ paddingLeft: `${depth * 16 + 8}px` }}
        onClick={() => onSelect(isSelected ? null : node.id)}
        onMouseEnter={() => onHover(node.id)}
        onMouseLeave={() => onHover(null)}
      >
        {hasChildren ? (
          <button
            onClick={(e) => { e.stopPropagation(); setExpanded(!expanded); }}
            className="p-0.5 hover:bg-slate-700 rounded"
          >
            {expanded ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
          </button>
        ) : (
          <span className="w-4" />
        )}
        {COMPONENT_ICONS[node.type] || <Box className="w-3.5 h-3.5 text-slate-500" />}
        <span className="truncate flex-1 font-mono">{node.type}</span>
        <span className="text-[10px] text-slate-600 font-mono truncate max-w-[80px]">{node.id}</span>
      </div>
      {hasChildren && expanded && (
        <div>
          {node.children!.map((childId) => {
            const child = components[childId];
            return child ? (
              <LayerNode
                key={childId}
                node={child}
                components={components}
                depth={depth + 1}
                selectedId={selectedId}
                onSelect={onSelect}
                onHover={onHover}
              />
            ) : null;
          })}
        </div>
      )}
    </div>
  );
};

export const LayersPanel: React.FC<LayersPanelProps> = ({ surface, selectedId, onSelect, onHover }) => {
  if (!surface) {
    return (
      <aside className="w-56 border-r border-slate-800 bg-slate-900/80 flex flex-col">
        <div className="p-3 border-b border-slate-800 text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Layers
        </div>
        <div className="flex-1 flex items-center justify-center text-xs text-slate-600 px-4 text-center">
          No surface active. Generate a website to see the component tree.
        </div>
      </aside>
    );
  }

  return (
    <aside className="w-56 border-r border-slate-800 bg-slate-900/80 flex flex-col overflow-hidden">
      <div className="p-3 border-b border-slate-800 text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center justify-between">
        <span>Layers</span>
        <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-500 font-mono">
          {Object.keys(surface.components).length}
        </span>
      </div>
      <div className="flex-1 overflow-y-auto py-1">
        {surface.rootIds.map((rootId) => {
          const node = surface.components[rootId];
          return node ? (
            <LayerNode
              key={rootId}
              node={node}
              components={surface.components}
              depth={0}
              selectedId={selectedId}
              onSelect={onSelect}
              onHover={onHover}
            />
          ) : null;
        })}
      </div>
    </aside>
  );
};
