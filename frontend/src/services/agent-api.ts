import { A2UIMessage, SurfaceState } from '../a2ui/protocol/a2ui-types';

const API_BASE = 'http://localhost:8000';

export type StreamEvent =
  | { type: 'text'; payload: string }
  | { type: 'steps'; payload: string[] }
  | { type: 'a2ui'; payload: A2UIMessage }
  | { type: 'console'; payload: ConsoleEventPayload }
  | { type: string; payload: unknown };

export interface ConsoleEventPayload {
  level: 'info' | 'success' | 'warning' | 'error';
  message: string;
  provider?: string;
  model?: string;
  data?: unknown;
}

/** Legacy shape is accepted during backend rollout. */
export interface LegacyStreamChunk {
  message?: A2UIMessage;
  text?: string;
  steps?: string[];
}

export type StreamChunk = StreamEvent | LegacyStreamChunk;

export async function sendPromptToAgent(
  prompt: string,
  currentSurface: SurfaceState | null,
  onChunk: (chunk: StreamChunk) => void
): Promise<void> {
  const response = await fetch(`${API_BASE}/api/agent/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      prompt,
      current_surface_id: currentSurface?.surfaceId || null,
      current_surface_summary: currentSurface
        ? {
            title: currentSurface.title,
            component_count: Object.keys(currentSurface.components).length,
            component_ids: Object.keys(currentSurface.components),
            component_props: Object.fromEntries(Object.entries(currentSurface.components).map(([id, node]) => [id, { component: node.component, props: node.props || {} }])),
          }
        : null,
    }),
  });

  if (!response.ok) throw new Error(`API error: ${response.status} ${response.statusText}`);
  const reader = response.body?.getReader();
  if (!reader) throw new Error('Response body is not readable');

  const decoder = new TextDecoder();
  let buffer = '';
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      if (!line.startsWith('data: ')) continue;
      const data = line.slice(6).trim();
      if (data === '[DONE]') return;
      try {
        onChunk(JSON.parse(data) as StreamChunk);
      } catch {
        // Ignore malformed SSE frames and continue reading the stream.
      }
    }
  }
}

export async function loadFixture(name: string): Promise<A2UIMessage | null> {
  try {
    const response = await fetch(`/fixtures/${name}.json`);
    if (response.ok) return await response.json();
    const backendResponse = await fetch(`${API_BASE}/api/fixtures/${name}`);
    return backendResponse.ok ? await backendResponse.json() : null;
  } catch (error) {
    console.error('Failed to load fixture:', error);
    return null;
  }
}
