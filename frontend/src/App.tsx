import React from 'react';
import { SurfaceState, ViewportMode, ComponentId, A2UIMessage } from './types/a2ui';
import { processA2UIMessage, streamA2UIMessages } from './core/a2ui-runtime';
import { CanvasHeader } from './components/CanvasHeader';
import { LayersPanel } from './components/LayersPanel';
import { InspectorPanel } from './components/InspectorPanel';
import { CanvasArtboard } from './components/CanvasArtboard';
import { DataImportModal } from './components/DataImportModal';

const API_BASE = 'http://localhost:8000';

const App: React.FC = () => {
  const [surface, setSurface] = React.useState<SurfaceState | null>(null);
  const [viewport, setViewport] = React.useState<ViewportMode>('desktop');
  const [zoom, setZoom] = React.useState(0.85);
  const [selectedId, setSelectedId] = React.useState<ComponentId | null>(null);
  const [hoveredId, setHoveredId] = React.useState<ComponentId | null>(null);
  const [isStreaming, setIsStreaming] = React.useState(false);
  const [showLayers, setShowLayers] = React.useState(true);
  const [showInspector, setShowInspector] = React.useState(true);
  const [showDataModal, setShowDataModal] = React.useState(false);
  const [streamLog, setStreamLog] = React.useState<string[]>([]);

  const abortRef = React.useRef<AbortController | null>(null);

  const handleStreamGeneration = React.useCallback(async (prompt: string) => {
    // Abort any previous stream
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setIsStreaming(true);
    setSurface(null);
    setSelectedId(null);
    setStreamLog([]);

    try {
      let state: SurfaceState | null = null;
      const stream = streamA2UIMessages(
        `${API_BASE}/api/agent/stream-ui`,
        { prompt, catalog_id: 'astryx-web-v1' },
        controller.signal
      );

      for await (const msg of stream) {
        state = processA2UIMessage(msg, state);
        setSurface(state ? { ...state } : null);
        setStreamLog((prev) => [...prev, `✓ ${msg.type}`]);
      }
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        console.error('Stream error:', err);
        setStreamLog((prev) => [...prev, `✗ Error: ${err.message}`]);
      }
    } finally {
      setIsStreaming(false);
      abortRef.current = null;
    }
  }, []);

  const handleDataImport = React.useCallback(async (data: any) => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setIsStreaming(true);
    setSurface(null);
    setSelectedId(null);
    setStreamLog([]);

    try {
      let state: SurfaceState | null = null;
      const stream = streamA2UIMessages(
        `${API_BASE}/api/agent/stream-ui`,
        { raw_data: data, prompt: 'Generate interactive UI from this data', catalog_id: 'astryx-web-v1' },
        controller.signal
      );

      for await (const msg of stream) {
        state = processA2UIMessage(msg, state);
        setSurface(state ? { ...state } : null);
        setStreamLog((prev) => [...prev, `✓ ${msg.type}`]);
      }
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        console.error('Stream error:', err);
      }
    } finally {
      setIsStreaming(false);
      abortRef.current = null;
    }
  }, []);

  const handlePropertyChange = React.useCallback((id: ComponentId, propKey: string, value: any) => {
    setSurface((prev) => {
      if (!prev) return prev;
      const node = prev.components[id];
      if (!node) return prev;
      const updatedNode = {
        ...node,
        props: { ...node.props, [propKey]: value },
      };
      return {
        ...prev,
        components: { ...prev.components, [id]: updatedNode },
      };
    });
  }, []);

  const handleResetCanvas = React.useCallback(() => {
    abortRef.current?.abort();
    setSurface(null);
    setSelectedId(null);
    setHoveredId(null);
    setIsStreaming(false);
    setStreamLog([]);
  }, []);

  const selectedNode = selectedId && surface ? surface.components[selectedId] || null : null;

  return (
    <div className="h-screen w-screen flex flex-col bg-slate-950 text-slate-100 overflow-hidden">
      <CanvasHeader
        viewport={viewport}
        onViewportChange={setViewport}
        zoom={zoom}
        onZoomChange={setZoom}
        isStreaming={isStreaming}
        onStreamGeneration={handleStreamGeneration}
        onOpenDataModal={() => setShowDataModal(true)}
        showLayers={showLayers}
        onToggleLayers={() => setShowLayers(!showLayers)}
        showInspector={showInspector}
        onToggleInspector={() => setShowInspector(!showInspector)}
        onResetCanvas={handleResetCanvas}
      />

      <div className="flex flex-1 overflow-hidden">
        {showLayers && (
          <LayersPanel
            surface={surface}
            selectedId={selectedId}
            onSelect={setSelectedId}
            onHover={setHoveredId}
          />
        )}

        <CanvasArtboard
          surface={surface}
          viewport={viewport}
          zoom={zoom}
          selectedId={selectedId}
          hoveredId={hoveredId}
          onSelectComponent={setSelectedId}
          isStreaming={isStreaming}
        />

        {showInspector && (
          <InspectorPanel
            selectedNode={selectedNode}
            onPropertyChange={handlePropertyChange}
          />
        )}
      </div>

      {/* Stream Activity Log (bottom bar) */}
      {streamLog.length > 0 && (
        <div className="h-7 border-t border-slate-800 bg-slate-900/80 px-4 flex items-center gap-4 text-[10px] text-slate-500 font-mono overflow-hidden">
          <span className="text-slate-600">A2UI Stream:</span>
          <div className="flex-1 overflow-x-auto whitespace-nowrap flex gap-3">
            {streamLog.map((log, i) => (
              <span key={i} className={log.startsWith('✗') ? 'text-red-400' : 'text-emerald-500'}>{log}</span>
            ))}
          </div>
          {isStreaming && (
            <span className="flex items-center gap-1 text-blue-400">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" />
              Streaming
            </span>
          )}
        </div>
      )}

      <DataImportModal
        isOpen={showDataModal}
        onClose={() => setShowDataModal(false)}
        onImport={handleDataImport}
      />
    </div>
  );
};

export default App;
