import { useState, useCallback } from 'react';
import { SurfaceState, ComponentId, A2UIComponentNode, A2UIMessage } from '../a2ui/protocol/a2ui-types';
import { A2UIRuntime } from '../a2ui/runtime/a2ui-runtime';
import { ChatMessage } from './chat/chat-store';
import type { ConsoleEventPayload, StreamChunk } from '../services/agent-api';

export type { ChatMessage } from './chat/chat-store';

export interface WorkspaceStoreProps {
  onSendPromptToBackend: (
    prompt: string,
    currentSurface: SurfaceState | null,
    onStreamChunk: (chunk: StreamChunk) => void
  ) => Promise<void>;
  onLoadFixtureData: (fixtureName: string) => Promise<A2UIMessage | null>;
}

function normalizeChunk(chunk: StreamChunk): {
  text?: string;
  steps?: string[];
  message?: A2UIMessage;
  console?: ConsoleEventPayload;
} {
  if ('type' in chunk) {
    if (chunk.type === 'text' && typeof chunk.payload === 'string') return { text: chunk.payload };
    if (chunk.type === 'steps' && Array.isArray(chunk.payload)) return { steps: chunk.payload };
    if (chunk.type === 'a2ui') return { message: chunk.payload as A2UIMessage };
    if (chunk.type === 'console' && isConsoleEventPayload(chunk.payload)) return { console: chunk.payload };
    return {};
  }
  const legacy = chunk as { text?: string; steps?: string[]; message?: A2UIMessage };
  return {
    text: legacy.text,
    steps: legacy.steps,
    message: legacy.message,
  };
}

function isConsoleEventPayload(value: unknown): value is ConsoleEventPayload {
  if (!value || typeof value !== 'object') return false;
  const payload = value as Partial<ConsoleEventPayload>;
  return (
    typeof payload.message === 'string' &&
    ['info', 'success', 'warning', 'error'].includes(payload.level || '')
  );
}

export function useWorkspaceStore({ onSendPromptToBackend, onLoadFixtureData }: WorkspaceStoreProps) {
  const [surface, setSurface] = useState<SurfaceState | null>(null);
  const [selectedId, setSelectedId] = useState<ComponentId | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);

  // 1. Send Prompt to Agent
  const handleSendMessage = useCallback(async (prompt: string) => {
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
        (rawChunk) => {
          const chunk = normalizeChunk(rawChunk);
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
          if (chunk.console) {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === agentMsgId
                  ? { ...m, console: [...(m.console || []), chunk.console!] }
                  : m
              )
            );
          }
          if (chunk.message) {
            setSurface((current) => A2UIRuntime.processMessage(chunk.message!, current));
          }
        }
      );
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : String(err);
      setMessages((prev) =>
        prev.map((m) =>
          m.id === agentMsgId
            ? {
                ...m,
                content: `${m.content ? `${m.content}\n\n` : ''}Lỗi kết nối Agent: ${errorMessage}`,
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
  }, [onSendPromptToBackend, surface]);

  // 2. Direct property edit from Inspector
  const handleUpdateComponent = useCallback((updatedComp: A2UIComponentNode) => {
    if (!surface) return;
    const msg: A2UIMessage = {
      version: '1.0',
      updateComponents: {
        surfaceId: surface.surfaceId,
        components: [updatedComp],
      },
    };
    setSurface((current) => A2UIRuntime.processMessage(msg, current));
  }, [surface]);

  // 3. Update reactive data model
  const handleUpdateDataModel = useCallback((path: string, value: any) => {
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
  }, [surface]);

  // 4. Load fixture test
  const handleLoadFixture = useCallback(async (fixtureName: string) => {
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
  }, [onLoadFixtureData]);

  return {
    surface,
    selectedId,
    setSelectedId,
    messages,
    isGenerating,
    handleSendMessage,
    handleUpdateComponent,
    handleUpdateDataModel,
    handleLoadFixture,
  };
}
