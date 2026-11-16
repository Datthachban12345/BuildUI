import React from 'react';
import { SurfaceState, ComponentId, A2UIComponentNode } from '../../a2ui/protocol/types';
import { X, Sliders, Type, Layout, Palette } from 'lucide-react';

interface PropertyInspectorProps {
  surface: SurfaceState | null;
  selectedId: ComponentId | null;
  onClose: () => void;
  onUpdateComponent: (component: A2UIComponentNode) => void;
}

export const PropertyInspector: React.FC<PropertyInspectorProps> = ({
  surface,
  selectedId,
  onClose,
  onUpdateComponent,
}) => {
  if (!surface || !selectedId) return null;
  const node = surface.components[selectedId];
  if (!node) return null;

  const props = node.props || {};

  const handlePropChange = (key: string, value: any) => {
    onUpdateComponent({
      ...node,
      props: {
        ...props,
        [key]: value,
      },
    });
  };

  return (
    <aside className="w-80 h-full bg-zinc-950 border-l border-zinc-800/80 flex flex-col shrink-0 select-none z-20 shadow-xl">
      {/* Header */}
      <div className="h-14 px-4 border-b border-zinc-800/80 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sliders className="w-4 h-4 text-zinc-400" />
          <h3 className="text-xs font-semibold text-white uppercase tracking-wider">Property Inspector</h3>
        </div>
        <button
          onClick={onClose}
          className="p-1 rounded-md text-zinc-400 hover:text-white hover:bg-zinc-900 transition"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Node Info Badge */}
      <div className="p-4 border-b border-zinc-800/50 bg-zinc-900/30">
        <div className="flex items-center gap-2 mb-1">
          <span className="px-2 py-0.5 rounded bg-blue-600/20 text-blue-400 border border-blue-500/30 text-xs font-mono font-medium">
            {node.component}
          </span>
          <span className="text-[11px] text-zinc-500 font-mono truncate">#{node.id}</span>
        </div>
        <div className="text-[10px] text-zinc-500">
          Chỉnh sửa trực quan thuộc tính component đã chọn.
        </div>
      </div>

      {/* Properties List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs">
        {/* Text / Label editing if present */}
        {'text' in props && (
          <div className="space-y-1.5">
            <label className="text-[10px] uppercase font-semibold text-zinc-400 flex items-center gap-1.5">
              <Type className="w-3 h-3 text-zinc-500" />
              Nội dung Text
            </label>
            <textarea
              rows={3}
              value={props.text || ''}
              onChange={(e) => handlePropChange('text', e.target.value)}
              className="w-full bg-zinc-900 border border-zinc-800 focus:border-zinc-500 rounded-lg p-2.5 text-zinc-100 outline-none resize-none transition"
            />
          </div>
        )}

        {'label' in props && (
          <div className="space-y-1.5">
            <label className="text-[10px] uppercase font-semibold text-zinc-400 flex items-center gap-1.5">
              <Type className="w-3 h-3 text-zinc-500" />
              Label nút bấm
            </label>
            <input
              type="text"
              value={props.label || ''}
              onChange={(e) => handlePropChange('label', e.target.value)}
              className="w-full bg-zinc-900 border border-zinc-800 focus:border-zinc-500 rounded-lg px-3 py-2 text-zinc-100 outline-none transition"
            />
          </div>
        )}

        {'title' in props && (
          <div className="space-y-1.5">
            <label className="text-[10px] uppercase font-semibold text-zinc-400 flex items-center gap-1.5">
              <Type className="w-3 h-3 text-zinc-500" />
              Tiêu đề Card
            </label>
            <input
              type="text"
              value={props.title || ''}
              onChange={(e) => handlePropChange('title', e.target.value)}
              className="w-full bg-zinc-900 border border-zinc-800 focus:border-zinc-500 rounded-lg px-3 py-2 text-zinc-100 outline-none transition"
            />
          </div>
        )}

        {'description' in props && (
          <div className="space-y-1.5">
            <label className="text-[10px] uppercase font-semibold text-zinc-400 flex items-center gap-1.5">
              <Type className="w-3 h-3 text-zinc-500" />
              Mô tả chi tiết
            </label>
            <textarea
              rows={3}
              value={props.description || ''}
              onChange={(e) => handlePropChange('description', e.target.value)}
              className="w-full bg-zinc-900 border border-zinc-800 focus:border-zinc-500 rounded-lg p-2.5 text-zinc-100 outline-none resize-none transition"
            />
          </div>
        )}

        {'variant' in props && (
          <div className="space-y-1.5">
            <label className="text-[10px] uppercase font-semibold text-zinc-400 flex items-center gap-1.5">
              <Palette className="w-3 h-3 text-zinc-500" />
              Kiểu dáng (Variant)
            </label>
            <select
              value={props.variant || 'primary'}
              onChange={(e) => handlePropChange('variant', e.target.value)}
              className="w-full bg-zinc-900 border border-zinc-800 focus:border-zinc-500 rounded-lg px-3 py-2 text-zinc-100 outline-none transition"
            >
              <option value="primary">Primary</option>
              <option value="secondary">Secondary</option>
              <option value="outline">Outline</option>
              <option value="ghost">Ghost</option>
            </select>
          </div>
        )}

        {'placeholder' in props && (
          <div className="space-y-1.5">
            <label className="text-[10px] uppercase font-semibold text-zinc-400">
              Placeholder
            </label>
            <input
              type="text"
              value={props.placeholder || ''}
              onChange={(e) => handlePropChange('placeholder', e.target.value)}
              className="w-full bg-zinc-900 border border-zinc-800 focus:border-zinc-500 rounded-lg px-3 py-2 text-zinc-100 outline-none transition"
            />
          </div>
        )}

        {/* Generic Props JSON preview */}
        <div className="pt-4 border-t border-zinc-800/80 space-y-1.5">
          <div className="text-[10px] uppercase font-semibold text-zinc-500">Props Raw JSON</div>
          <pre className="p-2.5 rounded-lg bg-zinc-900 border border-zinc-800 text-[10px] text-zinc-400 font-mono overflow-x-auto max-h-40">
            {JSON.stringify(props, null, 2)}
          </pre>
        </div>
      </div>
    </aside>
  );
};
