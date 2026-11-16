import React from 'react';
import { SurfaceState, ComponentId, A2UIComponentNode } from '../../a2ui/protocol/types';
import { X, Sliders, Type, Palette } from 'lucide-react';

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
    <aside className="w-80 h-full bg-white border-l border-zinc-200/80 flex flex-col shrink-0 select-none z-20 shadow-[0_0_24px_rgba(0,0,0,0.04)]">
      {/* Header */}
      <div className="h-16 px-5 border-b border-zinc-200/80 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <Sliders className="w-4 h-4 text-zinc-700" />
          <h3 className="text-xs font-semibold text-zinc-900 uppercase tracking-wider">Thuộc tính Node</h3>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-full text-zinc-400 hover:text-zinc-900 hover:bg-zinc-100 transition"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Node Info Badge */}
      <div className="p-4 border-b border-zinc-100 bg-[#fbfbfd]">
        <div className="flex items-center gap-2 mb-1.5">
          <span className="px-2.5 py-0.5 rounded-full bg-zinc-900 text-white text-[11px] font-medium font-mono">
            {node.component}
          </span>
          <span className="text-[11px] text-zinc-500 font-mono truncate">#{node.id}</span>
        </div>
        <div className="text-[11px] text-zinc-500">
          Chỉnh sửa trực quan nội dung & thuộc tính component.
        </div>
      </div>

      {/* Properties List */}
      <div className="flex-1 overflow-y-auto p-5 space-y-4 text-xs">
        {/* Text / Label editing if present */}
        {'text' in props && (
          <div className="space-y-1.5">
            <label className="text-[11px] font-medium text-zinc-700 flex items-center gap-1.5">
              <Type className="w-3.5 h-3.5 text-zinc-400" />
              Nội dung Text
            </label>
            <textarea
              rows={3}
              value={props.text || ''}
              onChange={(e) => handlePropChange('text', e.target.value)}
              className="w-full bg-zinc-50 focus:bg-white border border-zinc-200 focus:border-zinc-400 rounded-xl p-3 text-zinc-900 outline-none resize-none transition"
            />
          </div>
        )}

        {'label' in props && (
          <div className="space-y-1.5">
            <label className="text-[11px] font-medium text-zinc-700 flex items-center gap-1.5">
              <Type className="w-3.5 h-3.5 text-zinc-400" />
              Nhãn nút bấm
            </label>
            <input
              type="text"
              value={props.label || ''}
              onChange={(e) => handlePropChange('label', e.target.value)}
              className="w-full bg-zinc-50 focus:bg-white border border-zinc-200 focus:border-zinc-400 rounded-xl px-3.5 py-2.5 text-zinc-900 outline-none transition"
            />
          </div>
        )}

        {'title' in props && (
          <div className="space-y-1.5">
            <label className="text-[11px] font-medium text-zinc-700 flex items-center gap-1.5">
              <Type className="w-3.5 h-3.5 text-zinc-400" />
              Tiêu đề Card
            </label>
            <input
              type="text"
              value={props.title || ''}
              onChange={(e) => handlePropChange('title', e.target.value)}
              className="w-full bg-zinc-50 focus:bg-white border border-zinc-200 focus:border-zinc-400 rounded-xl px-3.5 py-2.5 text-zinc-900 outline-none transition"
            />
          </div>
        )}

        {'description' in props && (
          <div className="space-y-1.5">
            <label className="text-[11px] font-medium text-zinc-700 flex items-center gap-1.5">
              <Type className="w-3.5 h-3.5 text-zinc-400" />
              Mô tả Card
            </label>
            <textarea
              rows={3}
              value={props.description || ''}
              onChange={(e) => handlePropChange('description', e.target.value)}
              className="w-full bg-zinc-50 focus:bg-white border border-zinc-200 focus:border-zinc-400 rounded-xl p-3 text-zinc-900 outline-none resize-none transition"
            />
          </div>
        )}

        {'variant' in props && (
          <div className="space-y-1.5">
            <label className="text-[11px] font-medium text-zinc-700 flex items-center gap-1.5">
              <Palette className="w-3.5 h-3.5 text-zinc-400" />
              Kiểu dáng (Variant)
            </label>
            <select
              value={props.variant || 'primary'}
              onChange={(e) => handlePropChange('variant', e.target.value)}
              className="w-full bg-zinc-50 focus:bg-white border border-zinc-200 focus:border-zinc-400 rounded-xl px-3.5 py-2.5 text-zinc-900 outline-none transition"
            >
              <option value="primary">Primary (Apple Black)</option>
              <option value="secondary">Secondary (Soft Gray)</option>
              <option value="outline">Outline</option>
              <option value="ghost">Ghost</option>
            </select>
          </div>
        )}

        {'placeholder' in props && (
          <div className="space-y-1.5">
            <label className="text-[11px] font-medium text-zinc-700">
              Placeholder
            </label>
            <input
              type="text"
              value={props.placeholder || ''}
              onChange={(e) => handlePropChange('placeholder', e.target.value)}
              className="w-full bg-zinc-50 focus:bg-white border border-zinc-200 focus:border-zinc-400 rounded-xl px-3.5 py-2.5 text-zinc-900 outline-none transition"
            />
          </div>
        )}

        {/* Generic Props JSON preview */}
        <div className="pt-4 border-t border-zinc-100 space-y-1.5">
          <div className="text-[10px] uppercase font-semibold text-zinc-400">Props JSON chi tiết</div>
          <pre className="p-3 rounded-xl bg-zinc-50 border border-zinc-200/80 text-[10px] text-zinc-600 font-mono overflow-x-auto max-h-40">
            {JSON.stringify(props, null, 2)}
          </pre>
        </div>
      </div>
    </aside>
  );
};
