import React from 'react';
import { ComponentNode, ComponentId } from '../types/a2ui';

interface InspectorPanelProps {
  selectedNode: ComponentNode | null;
  onPropertyChange: (id: ComponentId, propKey: string, value: any) => void;
}

export const InspectorPanel: React.FC<InspectorPanelProps> = ({ selectedNode, onPropertyChange }) => {
  if (!selectedNode) {
    return (
      <aside className="w-64 border-l border-slate-800 bg-slate-900/80 flex flex-col">
        <div className="p-3 border-b border-slate-800 text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Inspector
        </div>
        <div className="flex-1 flex items-center justify-center text-xs text-slate-600 px-4 text-center">
          Click a component on the canvas or in the Layers panel to inspect its properties.
        </div>
      </aside>
    );
  }

  const props = selectedNode.props || {};

  return (
    <aside className="w-64 border-l border-slate-800 bg-slate-900/80 flex flex-col overflow-hidden">
      <div className="p-3 border-b border-slate-800">
        <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Inspector</div>
        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 rounded bg-blue-600/20 text-blue-400 text-xs font-mono border border-blue-500/30">
            {selectedNode.type}
          </span>
          <span className="text-[10px] text-slate-600 font-mono truncate">{selectedNode.id}</span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        {/* Identity */}
        <div className="p-3 border-b border-slate-800/50">
          <div className="text-[10px] uppercase tracking-wider text-slate-500 mb-2 font-semibold">Identity</div>
          <div className="space-y-2">
            <div>
              <label className="text-[10px] text-slate-500 block mb-0.5">ID</label>
              <input
                readOnly
                value={selectedNode.id}
                className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1 text-xs text-slate-400 font-mono"
              />
            </div>
            <div>
              <label className="text-[10px] text-slate-500 block mb-0.5">Type</label>
              <input
                readOnly
                value={selectedNode.type}
                className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1 text-xs text-slate-400 font-mono"
              />
            </div>
            {selectedNode.parentId && (
              <div>
                <label className="text-[10px] text-slate-500 block mb-0.5">Parent</label>
                <input
                  readOnly
                  value={selectedNode.parentId}
                  className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1 text-xs text-slate-400 font-mono"
                />
              </div>
            )}
          </div>
        </div>

        {/* Props */}
        <div className="p-3">
          <div className="text-[10px] uppercase tracking-wider text-slate-500 mb-2 font-semibold">Properties</div>
          <div className="space-y-2">
            {Object.entries(props).map(([key, value]) => (
              <div key={key}>
                <label className="text-[10px] text-slate-500 block mb-0.5">{key}</label>
                {typeof value === 'boolean' ? (
                  <button
                    onClick={() => onPropertyChange(selectedNode.id, key, !value)}
                    className={`px-2.5 py-1 rounded text-xs font-medium transition ${
                      value
                        ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30'
                        : 'bg-slate-800 text-slate-400 border border-slate-700'
                    }`}
                  >
                    {value ? 'true' : 'false'}
                  </button>
                ) : typeof value === 'number' ? (
                  <input
                    type="number"
                    value={value}
                    onChange={(e) => onPropertyChange(selectedNode.id, key, Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 focus:border-blue-500 rounded px-2 py-1 text-xs text-slate-200 font-mono outline-none"
                  />
                ) : typeof value === 'string' ? (
                  <input
                    type="text"
                    value={value}
                    onChange={(e) => onPropertyChange(selectedNode.id, key, e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 focus:border-blue-500 rounded px-2 py-1 text-xs text-slate-200 font-mono outline-none"
                  />
                ) : (
                  <pre className="bg-slate-950 border border-slate-800 rounded px-2 py-1 text-[10px] text-slate-400 font-mono overflow-x-auto max-h-24">
                    {JSON.stringify(value, null, 2)}
                  </pre>
                )}
              </div>
            ))}
            {Object.keys(props).length === 0 && (
              <div className="text-xs text-slate-600 italic">No properties</div>
            )}
          </div>
        </div>

        {/* Children */}
        {selectedNode.children && selectedNode.children.length > 0 && (
          <div className="p-3 border-t border-slate-800/50">
            <div className="text-[10px] uppercase tracking-wider text-slate-500 mb-2 font-semibold">
              Children ({selectedNode.children.length})
            </div>
            <div className="flex flex-wrap gap-1">
              {selectedNode.children.map((cid) => (
                <span
                  key={cid}
                  className="px-1.5 py-0.5 rounded bg-slate-800 text-[10px] text-slate-400 font-mono border border-slate-700"
                >
                  {cid}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </aside>
  );
};
