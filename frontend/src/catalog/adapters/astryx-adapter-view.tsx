import React from 'react';
import { Image as ImageIcon } from 'lucide-react';
import { twMerge } from 'tailwind-merge';
import { A2UIComponentNode } from '../../a2ui/protocol/a2ui-types';

interface AstryxComponentProps {
  node: A2UIComponentNode;
  children?: React.ReactNode;
  dataModel: Record<string, any>;
  onAction?: (actionName: string, payload?: any) => void;
  onUpdateDataModel?: (path: string, value: any) => void;
}

const componentClasses = (node: A2UIComponentNode, ...structural: string[]) =>
  twMerge(
    typeof node.props?.className === 'string' ? node.props.className : '',
    ...structural,
  );

export const AstryxContainer: React.FC<AstryxComponentProps> = ({ node, children }) => {
  const maxWidthMap: Record<string, string> = {
    sm: 'max-w-screen-sm',
    md: 'max-w-screen-md',
    lg: 'max-w-screen-lg',
    xl: 'max-w-7xl',
    full: 'max-w-none',
  };
  const maxWidth = typeof node.props?.maxWidth === 'string' ? node.props.maxWidth : '';
  const maxW = maxWidth ? maxWidthMap[maxWidth] || maxWidthMap.xl : '';
  const paddingMap: Record<string, string> = {
    none: 'px-0',
    sm: 'px-4',
    md: 'px-4 sm:px-6',
    lg: 'px-4 sm:px-6 lg:px-8',
  };
  const paddingX = typeof node.props?.paddingX === 'string' ? node.props.paddingX : '';
  const padding = paddingMap[paddingX] || '';
  return (
    <div
      className={componentClasses(node, 'mx-auto w-full', maxW, padding)}
      data-a2ui-id={node.id}
    >
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
    sm: 'gap-3',
    md: 'gap-4',
    lg: 'gap-8',
  };
  const justify = justifyMap[node.props?.justify || 'start'] || 'justify-start';
  const align = alignMap[node.props?.align || 'center'] || 'items-center';
  const gap = gapMap[node.props?.gap || 'md'] || 'gap-4';

  return (
    <div className={componentClasses(node, 'flex flex-wrap min-w-0', justify, align, gap)} data-a2ui-id={node.id}>
      {children}
    </div>
  );
};

export const AstryxGrid: React.FC<AstryxComponentProps> = ({ node, children }) => {
  const columnClass: Record<number, string> = {
    1: 'grid-cols-1',
    2: 'grid-cols-2',
    3: 'grid-cols-3',
    4: 'grid-cols-4',
  };
  const requestedCols = node.props?.cols ?? 3;
  const isValidCols = (value: unknown): value is number =>
    typeof value === 'number' && Number.isInteger(value) && value >= 1 && value <= 4;
  const responsiveCols: Record<string, number> = {};
  if (typeof requestedCols === 'number') {
    const cols = isValidCols(requestedCols) ? requestedCols : 3;
    Object.assign(responsiveCols, {
      base: 1,
      sm: 2,
      lg: cols === 1 ? 1 : cols,
    });
  } else if (requestedCols && typeof requestedCols === 'object') {
    responsiveCols.base = isValidCols(requestedCols.base) ? requestedCols.base : 1;
    for (const breakpoint of ['sm', 'md', 'lg']) {
      const value = requestedCols[breakpoint as keyof typeof requestedCols];
      if (isValidCols(value)) responsiveCols[breakpoint] = value;
    }
  } else {
    responsiveCols.base = 1;
  }
  const colClasses = [
    columnClass[responsiveCols.base || 1],
    responsiveCols.sm ? `sm:${columnClass[responsiveCols.sm]}` : '',
    responsiveCols.md ? `md:${columnClass[responsiveCols.md]}` : '',
    responsiveCols.lg ? `lg:${columnClass[responsiveCols.lg]}` : '',
  ].filter(Boolean);
  const gapMap: Record<string, string> = { sm: 'gap-3', md: 'gap-6', lg: 'gap-8' };
  const gapCls = gapMap[node.props?.gap || 'md'] || gapMap.md;

  return (
    <div className={componentClasses(node, 'grid w-full min-w-0', ...colClasses, gapCls)} data-a2ui-id={node.id}>
      {children}
    </div>
  );
};

export const AstryxHeading: React.FC<AstryxComponentProps> = ({ node }) => {
  const requestedLevel = Number(node.props?.level);
  const level = [1, 2, 3, 4].includes(requestedLevel) ? requestedLevel : 2;
  const text = typeof node.props?.text === 'string' ? node.props.text : '';
  const Tag = `h${level}` as keyof JSX.IntrinsicElements;
  const levelStyles: Record<number, string> = {
    1: 'text-4xl md:text-5xl font-semibold tracking-tight leading-tight',
    2: 'text-2xl md:text-3xl font-semibold tracking-tight',
    3: 'text-xl font-medium tracking-tight',
    4: 'text-lg font-medium',
  };
  const scaleStyles: Record<string, string> = {
    sm: 'text-xl md:text-2xl',
    md: 'text-2xl md:text-3xl',
    lg: 'text-3xl md:text-4xl',
    xl: 'text-4xl md:text-5xl',
    display: 'text-5xl md:text-6xl',
  };
  const toneStyles: Record<string, string> = {
    default: level === 1 ? 'text-zinc-950' : 'text-zinc-900',
    muted: 'text-zinc-600',
    accent: 'text-blue-700',
    inverse: 'text-white',
  };
  const alignStyles: Record<string, string> = {
    left: 'text-left',
    center: 'text-center',
    right: 'text-right',
  };
  const scale = typeof node.props?.scale === 'string' ? node.props.scale : '';
  const tone = typeof node.props?.tone === 'string' ? node.props.tone : 'default';
  const align = typeof node.props?.align === 'string' ? node.props.align : 'left';
  const weight = typeof node.props?.weight === 'string' ? node.props.weight : '';
  const weightStyles: Record<string, string> = {
    normal: 'font-normal',
    medium: 'font-medium',
    semibold: 'font-semibold',
    bold: 'font-bold',
  };
  return (
    <Tag className={componentClasses(
      node,
      scaleStyles[scale] || levelStyles[level],
      weightStyles[weight] || '',
      toneStyles[tone] || toneStyles.default,
      alignStyles[align] || alignStyles.left,
    )} data-a2ui-id={node.id}>
      {text}
    </Tag>
  );
};

export const AstryxText: React.FC<AstryxComponentProps> = ({ node }) => {
  const sizeStyles: Record<string, string> = {
    xs: 'text-xs',
    sm: 'text-sm',
    base: 'text-sm md:text-base',
    lg: 'text-lg',
    xl: 'text-xl',
  };
  const toneStyles: Record<string, string> = {
    default: 'text-zinc-700',
    muted: 'text-zinc-600',
    accent: 'text-blue-700',
    inverse: 'text-white',
  };
  const weightStyles: Record<string, string> = {
    normal: 'font-normal',
    medium: 'font-medium',
    semibold: 'font-semibold',
  };
  const alignStyles: Record<string, string> = {
    left: 'text-left',
    center: 'text-center',
    right: 'text-right',
  };
  const size = typeof node.props?.size === 'string' ? node.props.size : 'base';
  const weight = typeof node.props?.weight === 'string' ? node.props.weight : 'normal';
  const tone = typeof node.props?.tone === 'string' ? node.props.tone : 'muted';
  const align = typeof node.props?.align === 'string' ? node.props.align : 'left';
  return (
    <p className={componentClasses(
      node,
      sizeStyles[size] || sizeStyles.base,
      weightStyles[weight] || 'font-normal',
      toneStyles[tone] || toneStyles.muted,
      alignStyles[align] || alignStyles.left,
      'leading-relaxed',
    )} data-a2ui-id={node.id}>
      {typeof node.props?.text === 'string' ? node.props.text : ''}
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
    sm: 'px-3 py-2 text-xs rounded-full',
    md: 'px-5 py-3 text-sm rounded-full',
    lg: 'px-7 py-4 text-base rounded-full',
  };

  const handleClick = () => {
    if (onAction && node.props?.action) {
      onAction(node.props.action, node.props?.actionPayload);
    }
  };

  return (
    <button
      onClick={handleClick}
      className={componentClasses(node, 'transition-all duration-200 cursor-pointer inline-flex items-center justify-center', variants[variant] || variants.primary, sizes[size] || sizes.md)}
      data-a2ui-id={node.id}
    >
      {node.props?.label || 'Button'}
    </button>
  );
};

export const AstryxCard: React.FC<AstryxComponentProps> = ({ node, children }) => {
  const variants: Record<string, string> = {
    default: 'rounded-2xl p-7 border border-zinc-200/90 bg-white shadow-sm hover:shadow-lg transition-all duration-300',
    soft: 'rounded-2xl p-6 border border-zinc-100 bg-zinc-50',
    outline: 'rounded-2xl p-6 border border-zinc-300 bg-white',
    elevated: 'rounded-2xl p-7 border border-zinc-200 bg-white shadow-md hover:shadow-xl transition-shadow duration-300',
  };
  const variant = node.props?.variant || 'default';
  return (
    <div
      className={componentClasses(node, variants[variant] || variants.default)}
      data-a2ui-id={node.id}
    >
      {node.props?.title && (
        <h3 className="mb-2 text-lg font-semibold tracking-tight text-zinc-900">{node.props.title}</h3>
      )}
      {node.props?.description && (
        <p className="mb-4 text-sm font-normal leading-relaxed text-zinc-600">{node.props.description}</p>
      )}
      {children}
    </div>
  );
};

export const AstryxBadge: React.FC<AstryxComponentProps> = ({ node }) => {
  return (
    <span
      className={componentClasses(node, 'inline-flex items-center px-3 py-1 rounded-full text-xs font-medium tracking-wide uppercase bg-zinc-100 text-zinc-800 border border-zinc-200')}
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
      className={componentClasses(node, 'w-full bg-zinc-50 border border-zinc-200 focus:border-zinc-400 focus:bg-white focus:ring-4 focus:ring-zinc-100 rounded-xl px-4 py-3 text-sm text-zinc-900 placeholder-zinc-400 outline-none transition duration-200')}
      data-a2ui-id={node.id}
    />
  );
};

export const AstryxMetricsCard: React.FC<AstryxComponentProps> = ({ node }) => {
  const trend = node.props?.trend;
  return (
    <div className={componentClasses(node, 'bg-white border border-zinc-200/90 rounded-2xl p-6 shadow-[0_2px_10px_rgba(0,0,0,0.03)]')} data-a2ui-id={node.id}>
      <div className="text-xs uppercase tracking-wider text-zinc-500 font-medium mb-2">{node.props?.label || 'Metric'}</div>
      <div className="text-3xl font-semibold text-zinc-950 tracking-tight">{node.props?.value || '0'}</div>
      {node.props?.change && (
        <div className={`inline-flex items-center gap-1 text-xs mt-3 font-medium px-2 py-1 rounded-full ${
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
  const [page, setPage] = React.useState(1);

  const dataPath = node.props?.dataPath;
  const pageSize: number = Number(node.props?.pageSize) || 5;

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

  // Pagination is fully client-side (60fps, no server round-trip).
  const totalPages = Math.max(1, Math.ceil(records.length / pageSize));
  const safePage = Math.min(page, totalPages);
  const pagedRecords = records.slice((safePage - 1) * pageSize, safePage * pageSize);

  const columns: Array<{ key: string; title: string; sortable?: boolean; type?: string }> = node.props?.columns || [];

  return (
    <div className={componentClasses(node, 'space-y-4')} data-a2ui-id={node.id}>
      {node.props?.searchable && (
        <input
          type="text"
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          placeholder="Lọc dữ liệu..."
          className="w-full bg-zinc-50 border border-zinc-200 rounded-xl px-4 py-2 text-xs text-zinc-900 outline-none focus:border-zinc-400 focus:bg-white placeholder-zinc-400 transition"
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
                      setPage(1);
                    }
                  }}
                  className={`px-4 py-4 text-left font-medium text-zinc-600 uppercase tracking-wider ${col.sortable ? 'cursor-pointer hover:text-zinc-900 select-none' : ''}`}
                >
                  {col.title}
                  {sortKey === col.key && <span className="ml-1 text-zinc-900">{sortAsc ? '↑' : '↓'}</span>}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-100">
            {pagedRecords.map((row, i) => (
              <tr key={i} className="hover:bg-zinc-50/70 transition">
                {columns.map(col => (
                  <td key={col.key} className="px-4 py-4 text-zinc-700 font-normal">
                    {col.type === 'badge' ? (
                      <span className="px-2 py-1 rounded-full text-[11px] font-medium bg-zinc-100 text-zinc-800 border border-zinc-200">
                        {row[col.key]}
                      </span>
                    ) : (
                      String(row[col.key] ?? '')
                    )}
                  </td>
                ))}
              </tr>
            ))}
            {pagedRecords.length === 0 && (
              <tr><td colSpan={columns.length} className="text-center py-10 text-zinc-400">Không tìm thấy dữ liệu</td></tr>
            )}
          </tbody>
        </table>
      </div>
      {totalPages > 1 && (
        <div className="flex items-center justify-between text-xs text-zinc-500">
          <span>
            {(safePage - 1) * pageSize + 1}–{Math.min(safePage * pageSize, records.length)} / {records.length} bản ghi
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={safePage === 1}
              className="px-3 py-2 rounded-full border border-zinc-200 bg-white text-zinc-700 hover:bg-zinc-50 disabled:opacity-40 disabled:cursor-not-allowed transition"
            >
              Trước
            </button>
            <span className="px-2 font-medium text-zinc-700">{safePage} / {totalPages}</span>
            <button
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={safePage === totalPages}
              className="px-3 py-2 rounded-full border border-zinc-200 bg-white text-zinc-700 hover:bg-zinc-50 disabled:opacity-40 disabled:cursor-not-allowed transition"
            >
              Sau
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export const AstryxImage: React.FC<AstryxComponentProps> = ({ node }) => {
  const rawSrc = typeof node.props?.src === 'string' ? node.props.src.trim() : '';
  const isHttpUrl = /^https?:\/\//i.test(rawSrc);
  const isRelativePath = /^(?!\/\/)(?:\/|\.\/|\.\.\/)/.test(rawSrc);
  const src = isHttpUrl || isRelativePath ? rawSrc : '';
  const alt = String(node.props?.alt || '');
  const ratio = node.props?.ratio;
  const ratioCls = ratio === 'wide'
    ? 'aspect-[2/1]'
    : ratio === 'tall'
      ? 'aspect-[3/4]'
      : ratio === 'square'
        ? 'aspect-square'
        : 'aspect-video';
  const fitStyles: Record<string, string> = {
    cover: 'object-cover',
    contain: 'object-contain',
  };
  const positionStyles: Record<string, string> = {
    center: 'object-center',
    top: 'object-top',
    bottom: 'object-bottom',
    left: 'object-left',
    right: 'object-right',
  };
  const fit = typeof node.props?.fit === 'string' ? node.props.fit : 'cover';
  const position = typeof node.props?.position === 'string' ? node.props.position : 'center';
  const [imageFailed, setImageFailed] = React.useState(false);
  React.useEffect(() => setImageFailed(false), [src]);
  if (src && !imageFailed) {
    return (
      <div
        className={componentClasses(node, 'overflow-hidden rounded-2xl border border-zinc-200 bg-zinc-50', ratioCls)}
        data-a2ui-id={node.id}
      >
        <img
          src={src}
          alt={alt}
          className={twMerge(
            'h-full w-full',
            fitStyles[fit] || fitStyles.cover,
            positionStyles[position] || positionStyles.center,
          )}
          loading="lazy"
          onError={() => setImageFailed(true)}
        />
      </div>
    );
  }
  // No src: Apple-style placeholder tile so layouts with image slots stay balanced.
  return (
    <div
      className={componentClasses(node, 'flex items-center justify-center rounded-2xl border border-zinc-200 bg-zinc-100', ratioCls)}
      data-a2ui-id={node.id}
    >
      <ImageIcon className="h-6 w-6 text-zinc-400" aria-hidden />
      {alt && <span className="ml-3 text-xs font-medium text-zinc-500">{alt}</span>}
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
  Image: AstryxImage,
};
