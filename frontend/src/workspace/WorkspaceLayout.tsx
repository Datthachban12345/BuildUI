import React, { useState } from 'react';
import { SurfaceState, ComponentId, A2UIComponentNode, A2UIMessage } from '../a2ui/protocol/types';
import { A2UIRuntime } from '../a2ui/runtime/A2UIRuntime';
import { ChatPanel, ChatMessage } from './chat/ChatPanel';
import { PreviewCanvas } from './preview/PreviewCanvas';
import { PropertyInspector } from './inspector/PropertyInspector';

interface WorkspaceLayoutProps {
  onSendPromptToBackend: (
    prompt: string,
    currentSurface: SurfaceState | null,
    onStreamChunk: (chunk: { message?: A2UIMessage; text?: string; steps?: string[] }) => void
  ) => Promise<void>;
  onLoadFixtureData: (fixtureName: string) => Promise<A2UIMessage | null>;
}

export const WorkspaceLayout: React.FC<WorkspaceLayoutProps> = ({
  onSendPromptToBackend,
  onLoadFixtureData,
}) => {
  const [surface, setSurface] = useState<SurfaceState | null>(null);
  const [selectedId, setSelectedId] = useState<ComponentId | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);

  // 1. Handle user prompt sent via Chat
  const handleSendMessage = async (prompt: string) => {
    const userMsgId = Date.now().toString();
    const userMsg: ChatMessage = {
      id: userMsgId,
      sender: 'user',
      content: prompt,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    const agentMsgId = (Date.now() + 1).toString();
    const agentMsg: ChatMessage = {
      id: agentMsgId,
      sender: 'agent',
      content: '',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      steps: ['Đang phân tích prompt...', 'Lên kế hoạch cấu trúc trang...'],
      isStreaming: true,
    };

    setMessages((prev) => [...prev, userMsg, agentMsg]);
    setIsGenerating(true);

    try {
      await onSendPromptToBackend(
        prompt,
        surface,
        (chunk) => {
          if (chunk.text) {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === agentMsgId ? { ...m, content: (m.content || '') + chunk.text } : m
              )
            );
          }
          if (chunk.steps) {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === agentMsgId ? { ...m, steps: chunk.steps } : m
              )
            );
          }
          if (chunk.message) {
            setSurface((current) => A2UIRuntime.processMessage(chunk.message!, current));
          }
        }
      );
    } catch (err: any) {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === agentMsgId
            ? {
                ...m,
                content: m.content || `Đã xảy ra lỗi khi kết nối Agent: ${err.message}`,
                isStreaming: false,
              }
            : m
        )
      );
    } finally {
      setIsGenerating(false);
      setMessages((prev) =>
        prev.map((m) => (m.id === agentMsgId ? { ...m, isStreaming: false } : m))
      );
    }
  };

  // 2. Direct property edit from PropertyInspector (Incremental Update)
  const handleUpdateComponent = (updatedComp: A2UIComponentNode) => {
    if (!surface) return;
    const msg: A2UIMessage = {
      version: '1.0',
      updateComponents: {
        surfaceId: surface.surfaceId,
        components: [updatedComp],
      },
    };
    setSurface((current) => A2UIRuntime.processMessage(msg, current));
  };

  // 3. Update data model from inputs
  const handleUpdateDataModel = (path: string, value: any) => {
    if (!surface) return;
    const msg: A2UIMessage = {
      version: '1.0',
      updateDataModel: {
        surfaceId: surface.surfaceId,
        path,
        value,
        operation: 'set',
      },
    };
    setSurface((current) => A2UIRuntime.processMessage(msg, current));
  };

  // 4. Load fixture test for deterministic validation
  const handleLoadFixture = async (fixtureName: string) => {
    const fixture = await onLoadFixtureData(fixtureName);
    if (fixture) {
      const nextSurface = A2UIRuntime.processMessage(fixture, null);
      setSurface(nextSurface);
      setSelectedId(null);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          sender: 'agent',
          content: `Đã nạp fixture kiểm thử deterministic: [${fixtureName}]. Bạn có thể xem và tương tác trực tiếp trên canvas.`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          steps: ['Nạp JSON Fixture v1.0', 'Render component tree', 'Khởi tạo dataModel reactive'],
        },
      ]);
    }
  };

  return (
    <div className="flex w-screen h-screen overflow-hidden bg-[#f5f5f7] text-zinc-900 font-sans">
      {/* 1. Left Chat Copilot Panel */}
      <ChatPanel
        messages={messages}
        onSendMessage={handleSendMessage}
        isGenerating={isGenerating}
        onLoadFixture={handleLoadFixture}
      />

      {/* 2. Center Live Canvas Artboard */}
      <PreviewCanvas
        surface={surface}
        selectedId={selectedId}
        onSelectComponent={setSelectedId}
        onUpdateDataModel={handleUpdateDataModel}
        isGenerating={isGenerating}
      />

      {/* 3. Right Property Inspector Drawer */}
      {selectedId && (
        <PropertyInspector
          surface={surface}
          selectedId={selectedId}
          onClose={() => setSelectedId(null)}
          onUpdateComponent={handleUpdateComponent}
        />
      )}
    </div>
  );
};
