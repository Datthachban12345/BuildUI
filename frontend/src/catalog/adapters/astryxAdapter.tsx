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
    sm: 'gap-2.5',
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
    1: 'text-4xl md:text-5xl font-semibold tracking-tight text-zinc-950 leading-tight',
    2: 'text-2xl md:text-3xl font-semibold tracking-tight text-zinc-900',
    3: 'text-xl font-medium tracking-tight text-zinc-900',
    4: 'text-lg font-medium text-zinc-800',
  };
  return (
    <Tag className={`${defaultSizes[level] || defaultSizes[2]} ${node.props?.className || ''}`} data-a2ui-id={node.id}>
      {text}
    </Tag>
  );
};

export const AstryxText: React.FC<AstryxComponentProps> = ({ node }) => {
  return (
    <p className={`text-zinc-600 font-normal leading-relaxed text-sm md:text-base ${node.props?.className || ''}`} data-a2ui-id={node.id}>
      {node.props?.text || ''}
    </p>
  );
};

export const AstryxButton: React.FC<AstryxComponentProps> = ({ node, onAction }) => {
  const variant = node.props?.variant || 'primary';
  const size = node.props?.size || 'md';

  // Apple-grade Button Styling: crisp black primary, clean borders, smooth hover scale
  const variants: Record<string, string> = {
    primary: 'bg-zinc-900 text-white hover:bg-black font-medium shadow-[0_2px_8px_rgba(0,0,0,0.12)] active:scale-[0.98]',
    secondary: 'bg-zinc-100 text-zinc-900 hover:bg-zinc-200/80 font-medium active:scale-[0.98]',
    outline: 'border border-zinc-300 text-zinc-800 hover:border-zinc-400 hover:bg-zinc-50/80 font-medium active:scale-[0.98]',
    ghost: 'text-zinc-600 hover:text-zinc-950 hover:bg-zinc-100/80 font-medium active:scale-[0.98]',
  };
  const sizes: Record<string, string> = {
    sm: 'px-3.5 py-1.5 text-xs rounded-full',
    md: 'px-5 py-2.5 text-sm rounded-full',
    lg: 'px-7 py-3.5 text-base rounded-full',
  };

  const handleClick = () => {
    if (onAction && node.props?.action) {
      onAction(node.props.action, node.props?.actionPayload);
    }
  };

  return (
    <button
      onClick={handleClick}
      className={`transition-all duration-200 cursor-pointer inline-flex items-center justify-center ${variants[variant] || variants.primary} ${sizes[size] || sizes.md} ${node.props?.className || ''}`}
      data-a2ui-id={node.id}
    >
      {node.props?.label || 'Button'}
    </button>
  );
};

export const AstryxCard: React.FC<AstryxComponentProps> = ({ node, children }) => {
  return (
    <div
      className={`rounded-2xl p-7 border border-zinc-200/90 bg-white shadow-[0_2px_12px_rgba(0,0,0,0.03)] hover:shadow-[0_12px_32px_rgba(0,0,0,0.07)] hover:border-zinc-300 transition-all duration-300 ${node.props?.className || ''}`}
      data-a2ui-id={node.id}
    >
      {node.props?.title && (
        <h3 className="text-lg font-semibold tracking-tight text-zinc-900 mb-2">{node.props.title}</h3>
      )}
      {node.props?.description && (
        <p className="text-sm text-zinc-600 font-normal leading-relaxed mb-4">{node.props.description}</p>
      )}
      {children}
    </div>
  );
};

export const AstryxBadge: React.FC<AstryxComponentProps> = ({ node }) => {
  return (
    <span
      className={`inline-flex items-center px-3.5 py-1 rounded-full text-xs font-medium tracking-wide uppercase bg-zinc-100 text-zinc-800 border border-zinc-200/80 ${node.props?.className || ''}`}
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
      className={`w-full bg-zinc-50 border border-zinc-200 focus:border-zinc-400 focus:bg-white focus:ring-4 focus:ring-zinc-100 rounded-xl px-4 py-3 text-sm text-zinc-900 placeholder-zinc-400 outline-none transition duration-200 ${node.props?.className || ''}`}
      data-a2ui-id={node.id}
    />
  );
};

export const AstryxMetricsCard: React.FC<AstryxComponentProps> = ({ node }) => {
  const trend = node.props?.trend;
  return (
    <div className="bg-white border border-zinc-200/90 rounded-2xl p-6 shadow-[0_2px_10px_rgba(0,0,0,0.03)]" data-a2ui-id={node.id}>
      <div className="text-xs uppercase tracking-wider text-zinc-500 font-medium mb-1.5">{node.props?.label || 'Metric'}</div>
      <div className="text-3xl font-semibold text-zinc-950 tracking-tight">{node.props?.value || '0'}</div>
      {node.props?.change && (
        <div className={`inline-flex items-center gap-1 text-xs mt-2.5 font-medium px-2 py-0.5 rounded-full ${
          trend === 'up' ? 'text-emerald-700 bg-emerald-50 border border-emerald-200/60' : 'text-rose-700 bg-rose-50 border border-rose-200/60'
        }`}>
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
          placeholder="Lọc dữ liệu..."
          className="w-full bg-zinc-50 border border-zinc-200 rounded-xl px-4 py-2.5 text-xs text-zinc-900 outline-none focus:border-zinc-400 focus:bg-white placeholder-zinc-400 transition"
        />
      )}
      <div className="overflow-x-auto rounded-xl border border-zinc-200 bg-white shadow-sm">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-zinc-200 bg-zinc-50/80">
              {columns.map(col => (
                <th
                  key={col.key}
                  onClick={() => {
                    if (col.sortable) {
                      if (sortKey === col.key) setSortAsc(!sortAsc);
                      else { setSortKey(col.key); setSortAsc(true); }
                    }
                  }}
                  className={`px-4 py-3.5 text-left font-medium text-zinc-600 uppercase tracking-wider ${col.sortable ? 'cursor-pointer hover:text-zinc-900 select-none' : ''}`}
                >
                  {col.title}
                  {sortKey === col.key && <span className="ml-1 text-zinc-900">{sortAsc ? '↑' : '↓'}</span>}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-100">
            {records.map((row, i) => (
              <tr key={i} className="hover:bg-zinc-50/70 transition">
                {columns.map(col => (
                  <td key={col.key} className="px-4 py-3.5 text-zinc-700 font-normal">
                    {col.type === 'badge' ? (
                      <span className="px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-zinc-100 text-zinc-800 border border-zinc-200/80">
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
              <tr><td colSpan={columns.length} className="text-center py-10 text-zinc-400">Không tìm thấy dữ liệu</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export const AstryxFallbackComponent: React.FC<{ node: A2UIComponentNode }> = ({ node }) => {
  return (
    <div className="p-4 rounded-xl border border-dashed border-amber-300 bg-amber-50 text-xs text-amber-800 font-mono" data-a2ui-id={node.id}>
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
