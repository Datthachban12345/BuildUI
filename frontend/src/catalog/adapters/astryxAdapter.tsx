import React from 'react';
import { A2UIComponentNode } from '../../a2ui/protocol/types';

interface AstryxComponentProps {
  node: A2UIComponentNode;
  children?: React.ReactNode;
  dataModel: Record<string, any>;
  onAction?: (actionName: string, payload?: any) => void;
  onUpdateDataModel?: (path: string, value: any) => void;
}

export const AstryxContainer: React.FC<AstryxComponentProps> = ({ node, children }) => {
  const maxWidthMap: Record<string, string> = {
    sm: 'max-w-screen-sm',
    md: 'max-w-screen-md',
    lg: 'max-w-screen-lg',
    xl: 'max-w-screen-xl',
    full: 'w-full',
  };
  const maxW = maxWidthMap[node.props?.maxWidth || 'xl'] || 'max-w-screen-xl';
  return (
    <div className={`mx-auto ${maxW} ${node.props?.className || ''}`} data-a2ui-id={node.id}>
      {children}
    </div>
  );
};

export const AstryxRow: React.FC<AstryxComponentProps> = ({ node, children }) => {
  const justifyMap: Record<string, string> = {
    start: 'justify-start',
    center: 'justify-center',
    end: 'justify-end',
    between: 'justify-between',
    around: 'justify-around',
  };
  const alignMap: Record<string, string> = {
    start: 'items-start',
    center: 'items-center',
    end: 'items-end',
  };
  const gapMap: Record<string, string> = {
    sm: 'gap-2',
    md: 'gap-4',
    lg: 'gap-8',
  };
  const justify = justifyMap[node.props?.justify || 'start'] || 'justify-start';
  const align = alignMap[node.props?.align || 'center'] || 'items-center';
  const gap = gapMap[node.props?.gap || 'md'] || 'gap-4';

  return (
    <div className={`flex flex-wrap ${justify} ${align} ${gap} ${node.props?.className || ''}`} data-a2ui-id={node.id}>
      {children}
    </div>
  );
};

export const AstryxGrid: React.FC<AstryxComponentProps> = ({ node, children }) => {
  const cols = node.props?.cols || 3;
  const colCls = cols === 1 ? 'grid-cols-1' : cols === 2 ? 'grid-cols-1 md:grid-cols-2' : cols === 4 ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4' : 'grid-cols-1 md:grid-cols-3';
  const gapCls = node.props?.gap === 'lg' ? 'gap-8' : node.props?.gap === 'sm' ? 'gap-3' : 'gap-6';

  return (
    <div className={`grid ${colCls} ${gapCls} ${node.props?.className || ''}`} data-a2ui-id={node.id}>
      {children}
    </div>
  );
};

export const AstryxHeading: React.FC<AstryxComponentProps> = ({ node }) => {
  const level = node.props?.level || 2;
  const text = node.props?.text || '';
  const Tag = `h${level}` as keyof JSX.IntrinsicElements;
  const defaultSizes: Record<number, string> = {
    1: 'text-4xl md:text-5xl font-light text-white tracking-tight',
    2: 'text-2xl md:text-3xl font-light text-zinc-100',
    3: 'text-xl font-normal text-zinc-200',
    4: 'text-lg font-medium text-zinc-300',
  };
  return (
    <Tag className={`${defaultSizes[level] || defaultSizes[2]} ${node.props?.className || ''}`} data-a2ui-id={node.id}>
      {text}
    </Tag>
  );
};

export const AstryxText: React.FC<AstryxComponentProps> = ({ node }) => {
  return (
    <p className={`text-zinc-400 font-normal leading-relaxed ${node.props?.className || ''}`} data-a2ui-id={node.id}>
      {node.props?.text || ''}
    </p>
  );
};

export const AstryxButton: React.FC<AstryxComponentProps> = ({ node, onAction }) => {
  const variant = node.props?.variant || 'primary';
  const size = node.props?.size || 'md';

  const variants: Record<string, string> = {
    primary: 'bg-zinc-100 text-zinc-950 hover:bg-white font-medium shadow-sm',
    secondary: 'bg-zinc-800 text-zinc-200 hover:bg-zinc-700',
    outline: 'border border-zinc-700 text-zinc-300 hover:border-zinc-500 hover:text-white',
    ghost: 'text-zinc-400 hover:text-white hover:bg-zinc-900',
  };
  const sizes: Record<string, string> = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-5 py-2 text-sm',
    lg: 'px-7 py-3 text-base',
  };

  const handleClick = () => {
    if (onAction && node.props?.action) {
      onAction(node.props.action, node.props?.actionPayload);
    }
  };

  return (
    <button
      onClick={handleClick}
      className={`rounded-lg transition-all duration-200 cursor-pointer ${variants[variant] || variants.primary} ${sizes[size] || sizes.md} ${node.props?.className || ''}`}
      data-a2ui-id={node.id}
    >
      {node.props?.label || 'Button'}
    </button>
  );
};

export const AstryxCard: React.FC<AstryxComponentProps> = ({ node, children }) => {
  return (
    <div
      className={`rounded-xl p-6 border border-zinc-800/80 bg-zinc-900/40 backdrop-blur-sm transition-all duration-200 hover:border-zinc-700 ${node.props?.className || ''}`}
      data-a2ui-id={node.id}
    >
      {node.props?.title && (
        <h3 className="text-lg font-medium text-white mb-2">{node.props.title}</h3>
      )}
      {node.props?.description && (
        <p className="text-sm text-zinc-400 font-normal leading-relaxed mb-4">{node.props.description}</p>
      )}
      {children}
    </div>
  );
};

export const AstryxBadge: React.FC<AstryxComponentProps> = ({ node }) => {
  return (
    <span
      className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium tracking-wide uppercase border border-zinc-800 bg-zinc-900 text-zinc-300 ${node.props?.className || ''}`}
      data-a2ui-id={node.id}
    >
      {node.props?.label || ''}
    </span>
  );
};

export const AstryxInput: React.FC<AstryxComponentProps> = ({ node, dataModel, onUpdateDataModel }) => {
  const [val, setVal] = React.useState('');
  const dataPath = node.props?.dataPath;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const next = e.target.value;
    setVal(next);
    if (dataPath && onUpdateDataModel) {
      onUpdateDataModel(dataPath, next);
    }
  };

  return (
    <input
      type={node.props?.type || 'text'}
      value={dataPath ? dataModel[dataPath] ?? val : val}
      onChange={handleChange}
      placeholder={node.props?.placeholder || ''}
      className={`w-full bg-zinc-900/90 border border-zinc-800 focus:border-zinc-500 rounded-lg px-4 py-2.5 text-sm text-zinc-100 placeholder-zinc-500 outline-none transition ${node.props?.className || ''}`}
      data-a2ui-id={node.id}
    />
  );
};

export const AstryxMetricsCard: React.FC<AstryxComponentProps> = ({ node }) => {
  const trend = node.props?.trend;
  return (
    <div className="bg-zinc-900/40 border border-zinc-800 rounded-xl p-5" data-a2ui-id={node.id}>
      <div className="text-xs uppercase tracking-wider text-zinc-500 font-medium mb-1.5">{node.props?.label || 'Metric'}</div>
      <div className="text-3xl font-light text-white tracking-tight">{node.props?.value || '0'}</div>
      {node.props?.change && (
        <div className={`text-xs mt-2 font-medium ${trend === 'up' ? 'text-emerald-400' : 'text-rose-400'}`}>
          {trend === 'up' ? '↑' : '↓'} {node.props.change}
        </div>
      )}
    </div>
  );
};

export const AstryxDataTable: React.FC<AstryxComponentProps> = ({ node, dataModel }) => {
  const [search, setSearch] = React.useState('');
  const [sortKey, setSortKey] = React.useState<string | null>(null);
  const [sortAsc, setSortAsc] = React.useState(true);

  const dataPath = node.props?.dataPath;
  let records: any[] = [];
  if (dataPath && Array.isArray(dataModel[dataPath])) {
    records = dataModel[dataPath];
  } else if (Array.isArray(node.props?.data)) {
    records = node.props.data;
  }

  if (search) {
    const q = search.toLowerCase();
    records = records.filter(r => Object.values(r).some(v => String(v).toLowerCase().includes(q)));
  }

  if (sortKey) {
    records = [...records].sort((a, b) => {
      const av = a[sortKey], bv = b[sortKey];
      if (av < bv) return sortAsc ? -1 : 1;
      if (av > bv) return sortAsc ? 1 : -1;
      return 0;
    });
  }

  const columns: Array<{ key: string; title: string; sortable?: boolean; type?: string }> = node.props?.columns || [];

  return (
    <div className="space-y-4" data-a2ui-id={node.id}>
      {node.props?.searchable && (
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Filter records..."
          className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3.5 py-2 text-xs text-zinc-200 outline-none focus:border-zinc-600 placeholder-zinc-600"
        />
      )}
      <div className="overflow-x-auto rounded-lg border border-zinc-800">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-zinc-800 bg-zinc-900/60">
              {columns.map(col => (
                <th
                  key={col.key}
                  onClick={() => {
                    if (col.sortable) {
                      if (sortKey === col.key) setSortAsc(!sortAsc);
                      else { setSortKey(col.key); setSortAsc(true); }
                    }
                  }}
                  className={`px-4 py-3 text-left font-medium text-zinc-400 uppercase tracking-wider ${col.sortable ? 'cursor-pointer hover:text-zinc-200 select-none' : ''}`}
                >
                  {col.title}
                  {sortKey === col.key && <span className="ml-1">{sortAsc ? '↑' : '↓'}</span>}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800/60">
            {records.map((row, i) => (
              <tr key={i} className="hover:bg-zinc-800/30 transition">
                {columns.map(col => (
                  <td key={col.key} className="px-4 py-3 text-zinc-300 font-normal">
                    {col.type === 'badge' ? (
                      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-medium bg-zinc-800 text-zinc-300 border border-zinc-700">
                        {row[col.key]}
                      </span>
                    ) : (
                      String(row[col.key] ?? '')
                    )}
                  </td>
                ))}
              </tr>
            ))}
            {records.length === 0 && (
              <tr><td colSpan={columns.length} className="text-center py-8 text-zinc-600">No records found</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export const AstryxFallbackComponent: React.FC<{ node: A2UIComponentNode }> = ({ node }) => {
  return (
    <div className="p-4 rounded-lg border border-dashed border-amber-800/80 bg-amber-950/20 text-xs text-amber-400 font-mono" data-a2ui-id={node.id}>
      ⚠ Component &lt;{node.component}&gt; is not registered in Astryx Catalog.
    </div>
  );
};

export const ASTRYX_REGISTRY: Record<string, React.FC<AstryxComponentProps>> = {
  Container: AstryxContainer,
  Row: AstryxRow,
  Grid: AstryxGrid,
  Heading: AstryxHeading,
  Text: AstryxText,
  Button: AstryxButton,
  Card: AstryxCard,
  Badge: AstryxBadge,
  Input: AstryxInput,
  MetricsCard: AstryxMetricsCard,
  DataTable: AstryxDataTable,
};
