import { A2UIMessage, SurfaceState } from '../a2ui/protocol/types';

const API_BASE = 'http://localhost:8000';

export interface StreamChunk {
  message?: A2UIMessage;
  text?: string;
  steps?: string[];
}

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
          }
        : null,
    }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

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
      if (line.startsWith('data: ')) {
        const dataStr = line.slice(6).trim();
        if (dataStr === '[DONE]') return;
        try {
          const parsed = JSON.parse(dataStr);
          onChunk(parsed);
        } catch {
          // Skip if malformed
        }
      }
    }
  }
}

/**
 * Loads deterministic fixture for Phase 1 verification without needing an LLM
 */
export async function loadFixture(name: string): Promise<A2UIMessage | null> {
  try {
    const res = await fetch(`/fixtures/${name}.json`);
    if (!res.ok) {
      // Fallback: try backend endpoint or return null
      const resBackend = await fetch(`${API_BASE}/api/fixtures/${name}`);
      if (resBackend.ok) {
        return await resBackend.json();
      }
      return null;
    }
    return await res.json();
  } catch (err) {
    console.error('Failed to load fixture:', err);
    return null;
  }
}
