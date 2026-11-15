import React from 'react';
import { ComponentNode, SurfaceState, ComponentId, ViewportMode, ViewportConfig } from '../types/a2ui';

const VIEWPORT_CONFIGS: Record<ViewportMode, ViewportConfig> = {
  desktop: { name: 'desktop', width: 1440, height: 900, label: 'Desktop' },
  tablet: { name: 'tablet', width: 768, height: 1024, label: 'Tablet' },
  mobile: { name: 'mobile', width: 375, height: 812, label: 'Mobile' },
};

interface CanvasArtboardProps {
  surface: SurfaceState | null;
  viewport: ViewportMode;
  zoom: number;
  selectedId: ComponentId | null;
  hoveredId: ComponentId | null;
  onSelectComponent: (id: ComponentId | null) => void;
  isStreaming: boolean;
}

/* ---------- Astryx Placeholder Renderers ---------- */

const AstryxContainer: React.FC<{ node: ComponentNode; children: React.ReactNode }> = ({ node, children }) => (
  <div className={node.props?.className || 'p-4'} data-a2ui-id={node.id}>
    {children}
  </div>
);

const AstryxRow: React.FC<{ node: ComponentNode; children: React.ReactNode }> = ({ node, children }) => (
  <div className={`flex items-center ${node.props?.gap === 'md' ? 'gap-3' : 'gap-2'} ${node.props?.className || ''}`} data-a2ui-id={node.id}>
    {children}
  </div>
);

const AstryxGrid: React.FC<{ node: ComponentNode; children: React.ReactNode }> = ({ node, children }) => {
  const cols = node.props?.cols || 3;
  return (
    <div
      className={`grid ${cols === 2 ? 'grid-cols-2' : cols === 3 ? 'grid-cols-3' : cols === 4 ? 'grid-cols-4' : 'grid-cols-3'} ${node.props?.gap === 'md' ? 'gap-4' : 'gap-3'} ${node.props?.className || ''}`}
      data-a2ui-id={node.id}
    >
      {children}
    </div>
  );
};

const AstryxHeading: React.FC<{ node: ComponentNode }> = ({ node }) => {
  const level = node.props?.level || 2;
  const text = node.props?.text || '';
  const cls = node.props?.className || '';
  const Tag = `h${level}` as keyof JSX.IntrinsicElements;
  const sizeMap: Record<number, string> = {
    1: 'text-4xl font-extrabold',
    2: 'text-2xl font-bold',
    3: 'text-xl font-bold',
    4: 'text-lg font-semibold',
    5: 'text-base font-semibold',
    6: 'text-sm font-semibold',
  };
  return (
    <Tag className={`${sizeMap[level] || sizeMap[2]} text-white ${cls}`} data-a2ui-id={node.id}>
      {text}
    </Tag>
  );
};

const AstryxText: React.FC<{ node: ComponentNode }> = ({ node }) => (
  <p className={`${node.props?.className || 'text-slate-300'}`} data-a2ui-id={node.id}>
    {node.props?.text || ''}
  </p>
);

const AstryxButton: React.FC<{ node: ComponentNode }> = ({ node }) => {
  const variant = node.props?.variant || 'primary';
  const variantCls: Record<string, string> = {
    primary: 'bg-blue-600 hover:bg-blue-500 text-white',
    secondary: 'bg-slate-700 hover:bg-slate-600 text-slate-100',
    outline: 'border border-slate-600 hover:bg-slate-800 text-slate-200',
    ghost: 'hover:bg-slate-800 text-slate-300',
    danger: 'bg-red-600 hover:bg-red-500 text-white',
  };
  const sizeCls = node.props?.size === 'sm' ? 'px-3 py-1 text-xs' : 'px-4 py-2 text-sm';
  return (
    <button
      className={`rounded-lg font-medium transition ${sizeCls} ${variantCls[variant] || variantCls.primary}`}
      data-a2ui-id={node.id}
    >
      {node.props?.label || 'Button'}
    </button>
  );
};

const AstryxCard: React.FC<{ node: ComponentNode; children: React.ReactNode }> = ({ node, children }) => (
  <div
    className={`bg-slate-800/60 border border-slate-700/60 rounded-xl p-5 ${node.props?.className || ''}`}
    data-a2ui-id={node.id}
  >
    {node.props?.title && <h3 className="text-base font-semibold text-white mb-1">{node.props.title}</h3>}
    {node.props?.description && <p className="text-xs text-slate-400 mb-4">{node.props.description}</p>}
    {children}
  </div>
);

const AstryxMetricsCard: React.FC<{ node: ComponentNode }> = ({ node }) => {
  const trend = node.props?.trend;
  return (
    <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4" data-a2ui-id={node.id}>
      <div className="text-xs text-slate-400 mb-1">{node.props?.label || 'Metric'}</div>
      <div className="text-2xl font-bold text-white">{node.props?.value || '0'}</div>
      {node.props?.change && (
        <div className={`text-xs mt-1 font-medium ${trend === 'up' ? 'text-emerald-400' : 'text-red-400'}`}>
          {trend === 'up' ? '↑' : '↓'} {node.props.change}
        </div>
      )}
    </div>
  );
};

const AstryxDataTable: React.FC<{ node: ComponentNode; dataModel: Record<string, any> }> = ({ node, dataModel }) => {
  const [sortKey, setSortKey] = React.useState<string | null>(null);
  const [sortAsc, setSortAsc] = React.useState(true);
  const [search, setSearch] = React.useState('');
  const [page, setPage] = React.useState(0);

  const dataPath = node.props?.dataPath || '';
  const columns: Array<{ key: string; title: string; sortable?: boolean; type?: string }> = node.props?.columns || [];
  const pageSize = node.props?.pageSize || 10;

  // Resolve data from dataModel using dot-path
  let records: any[] = [];
  if (dataPath) {
    const parts = dataPath.split('.');
    let cur: any = dataModel;
    for (const p of parts) {
      cur = cur?.[p];
    }
    if (Array.isArray(cur)) records = cur;
  }

  // Filter
  if (search) {
    const q = search.toLowerCase();
    records = records.filter((r) =>
      Object.values(r).some((v) => String(v).toLowerCase().includes(q))
    );
  }

  // Sort
  if (sortKey) {
    records = [...records].sort((a, b) => {
      const av = a[sortKey], bv = b[sortKey];
      if (av < bv) return sortAsc ? -1 : 1;
      if (av > bv) return sortAsc ? 1 : -1;
      return 0;
    });
  }

  const totalPages = Math.ceil(records.length / pageSize);
  const paged = records.slice(page * pageSize, (page + 1) * pageSize);

  const handleSort = (key: string) => {
    if (sortKey === key) setSortAsc(!sortAsc);
    else { setSortKey(key); setSortAsc(true); }
  };

  const statusColors: Record<string, string> = {
    Active: 'bg-emerald-600/20 text-emerald-400 border-emerald-500/30',
    Testing: 'bg-amber-600/20 text-amber-400 border-amber-500/30',
    Beta: 'bg-amber-600/20 text-amber-400 border-amber-500/30',
    Review: 'bg-blue-600/20 text-blue-400 border-blue-500/30',
    Preview: 'bg-purple-600/20 text-purple-400 border-purple-500/30',
    Pending: 'bg-slate-600/20 text-slate-400 border-slate-500/30',
  };

  return (
    <div data-a2ui-id={node.id} className="space-y-3">
      {node.props?.searchable && (
        <input
          type="text"
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(0); }}
          placeholder="Search records..."
          className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 outline-none focus:border-blue-500 placeholder-slate-500"
        />
      )}
      <div className="overflow-x-auto rounded-lg border border-slate-700/60">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-slate-700/60">
              {columns.map((col) => (
                <th
                  key={col.key}
                  onClick={() => col.sortable && handleSort(col.key)}
                  className={`px-3 py-2.5 text-left text-slate-400 font-semibold uppercase tracking-wider bg-slate-800/40 ${
                    col.sortable ? 'cursor-pointer hover:text-slate-200 select-none' : ''
                  }`}
                >
                  {col.title}
                  {sortKey === col.key && <span className="ml-1">{sortAsc ? '↑' : '↓'}</span>}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paged.map((row, idx) => (
              <tr key={idx} className="border-b border-slate-800/40 hover:bg-slate-800/30 transition">
                {columns.map((col) => (
                  <td key={col.key} className="px-3 py-2 text-slate-300">
                    {col.type === 'badge' ? (
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium border ${
                        statusColors[row[col.key]] || statusColors.Pending
                      }`}>
                        {row[col.key]}
                      </span>
                    ) : (
                      String(row[col.key] ?? '')
                    )}
                  </td>
                ))}
              </tr>
            ))}
            {paged.length === 0 && (
              <tr><td colSpan={columns.length} className="text-center py-6 text-slate-600">No records</td></tr>
            )}
          </tbody>
        </table>
      </div>
      {totalPages > 1 && (
        <div className="flex items-center justify-between text-xs text-slate-500">
          <span>Page {page + 1} of {totalPages} ({records.length} records)</span>
          <div className="flex gap-1">
            <button disabled={page === 0} onClick={() => setPage(page - 1)} className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-40">Prev</button>
            <button disabled={page >= totalPages - 1} onClick={() => setPage(page + 1)} className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-40">Next</button>
          </div>
        </div>
      )}
    </div>
  );
};

const AstryxFallback: React.FC<{ node: ComponentNode }> = ({ node }) => (
  <div className="border border-dashed border-slate-700 rounded-lg p-3 text-xs text-slate-500 bg-slate-800/30" data-a2ui-id={node.id}>
    <span className="font-mono text-orange-400">&lt;{node.type}&gt;</span> — unsupported component (fallback)
  </div>
);

/* ---------- Recursive Component Renderer ---------- */

const RenderNode: React.FC<{
  nodeId: ComponentId;
  surface: SurfaceState;
  selectedId: ComponentId | null;
  hoveredId: ComponentId | null;
  onSelect: (id: ComponentId | null) => void;
}> = ({ nodeId, surface, selectedId, hoveredId, onSelect }) => {
  const node = surface.components[nodeId];
  if (!node) return null;

  const childElements = (node.children || []).map((cid) => (
    <RenderNode key={cid} nodeId={cid} surface={surface} selectedId={selectedId} hoveredId={hoveredId} onSelect={onSelect} />
  ));

  const isSelected = selectedId === node.id;
  const isHovered = hoveredId === node.id;

  const wrapperCls = `relative ${
    isSelected ? 'ring-2 ring-blue-500 ring-offset-1 ring-offset-slate-900 rounded' : ''
  } ${isHovered && !isSelected ? 'ring-1 ring-blue-400/40 rounded' : ''}`;

  const renderComponent = () => {
    switch (node.type) {
      case 'Container': return <AstryxContainer node={node}>{childElements}</AstryxContainer>;
      case 'Row': return <AstryxRow node={node}>{childElements}</AstryxRow>;
      case 'Column': return <div className={`flex flex-col ${node.props?.gap === 'md' ? 'gap-4' : 'gap-2'}`} data-a2ui-id={node.id}>{childElements}</div>;
      case 'Grid': return <AstryxGrid node={node}>{childElements}</AstryxGrid>;
      case 'Heading': return <AstryxHeading node={node} />;
      case 'Text': return <AstryxText node={node} />;
      case 'Button': return <AstryxButton node={node} />;
      case 'Card': return <AstryxCard node={node}>{childElements}</AstryxCard>;
      case 'MetricsCard': return <AstryxMetricsCard node={node} />;
      case 'DataTable': return <AstryxDataTable node={node} dataModel={surface.dataModel} />;
      default: return <AstryxFallback node={node} />;
    }
  };

  return (
    <div className={wrapperCls} onClick={(e) => { e.stopPropagation(); onSelect(node.id); }}>
      {renderComponent()}
    </div>
  );
};

/* ---------- Skeleton Shimmer ---------- */

const SkeletonShimmer: React.FC = () => (
  <div className="animate-pulse space-y-6 p-8">
    <div className="flex items-center justify-between">
      <div className="h-6 w-48 bg-slate-800 rounded-lg" />
      <div className="flex gap-2">
        <div className="h-8 w-24 bg-slate-800 rounded-lg" />
        <div className="h-8 w-28 bg-slate-800 rounded-lg" />
      </div>
    </div>
    <div className="space-y-4 mt-12 text-center">
      <div className="h-10 w-3/4 bg-slate-800 rounded-lg mx-auto" />
      <div className="h-4 w-2/3 bg-slate-800/60 rounded mx-auto" />
    </div>
    <div className="grid grid-cols-3 gap-4 mt-8">
      {[1,2,3].map(i => <div key={i} className="h-24 bg-slate-800/50 rounded-xl" />)}
    </div>
    <div className="h-48 bg-slate-800/40 rounded-xl mt-6" />
  </div>
);

/* ---------- Canvas Artboard ---------- */

export const CanvasArtboard: React.FC<CanvasArtboardProps> = ({
  surface,
  viewport,
  zoom,
  selectedId,
  hoveredId,
  onSelectComponent,
  isStreaming,
}) => {
  const vpConfig = VIEWPORT_CONFIGS[viewport];

  return (
    <div className="flex-1 bg-slate-950 overflow-auto flex items-start justify-center p-6">
      {/* Artboard Frame */}
      <div
        className="relative bg-slate-900 border border-slate-800 rounded-xl shadow-2xl overflow-hidden transition-all duration-300"
        style={{
          width: `${vpConfig.width * zoom}px`,
          minHeight: `${vpConfig.height * zoom}px`,
          transform: `scale(1)`,
          transformOrigin: 'top center',
        }}
        onClick={() => onSelectComponent(null)}
      >
        {/* Viewport Label */}
        <div className="absolute top-0 left-0 right-0 h-6 bg-slate-800/60 flex items-center justify-center text-[10px] text-slate-500 font-mono z-10 pointer-events-none">
          {vpConfig.label} — {vpConfig.width}×{vpConfig.height} @ {Math.round(zoom * 100)}%
        </div>

        {/* Render Area */}
        <div className="pt-6" style={{ fontSize: `${zoom * 100}%` }}>
          {!surface && !isStreaming && (
            <div className="flex flex-col items-center justify-center min-h-[400px] text-slate-600 space-y-4">
              <div className="w-16 h-16 rounded-2xl bg-slate-800/60 flex items-center justify-center text-3xl">⚡</div>
              <div className="text-sm font-medium">A2UI Canvas</div>
              <div className="text-xs text-slate-700 max-w-xs text-center">
                Use the prompt bar above or import JSON data to generate an interactive website surface.
              </div>
            </div>
          )}

          {isStreaming && !surface && <SkeletonShimmer />}

          {surface && surface.rootIds.map((rootId) => (
            <RenderNode
              key={rootId}
              nodeId={rootId}
              surface={surface}
              selectedId={selectedId}
              hoveredId={hoveredId}
              onSelect={onSelectComponent}
            />
          ))}
        </div>
      </div>
    </div>
  );
};
