import {
  A2UIMessage,
  SurfaceState,
  ComponentId,
  ComponentNode,
} from '../types/a2ui';

/**
 * Processes an A2UI message and returns the updated SurfaceState.
 * Pure function — no side effects.
 */
export function processA2UIMessage(
  message: A2UIMessage,
  currentState: SurfaceState | null
): SurfaceState | null {
  switch (message.type) {
    case 'createSurface': {
      return {
        surfaceId: message.surfaceId,
        title: message.title || 'Untitled',
        catalogId: message.catalogId,
        layout: message.layout || { type: 'standard' },
        components: {},
        rootIds: [],
        dataModel: {},
      };
    }

    case 'updateComponents': {
      if (!currentState || currentState.surfaceId !== message.surfaceId) return currentState;
      const newComponents = { ...currentState.components };
      const newRootIds = [...currentState.rootIds];

      for (const comp of message.components) {
        newComponents[comp.id] = comp;
        if (!comp.parentId && !newRootIds.includes(comp.id)) {
          newRootIds.push(comp.id);
        }
      }

      return { ...currentState, components: newComponents, rootIds: newRootIds };
    }

    case 'updateDataModel': {
      if (!currentState || currentState.surfaceId !== message.surfaceId) return currentState;
      const newDataModel = { ...currentState.dataModel };

      if (message.operation === 'set') {
        if (message.path) {
          setNestedValue(newDataModel, message.path, message.value);
        } else {
          return { ...currentState, dataModel: message.value };
        }
      } else if (message.operation === 'merge') {
        if (message.path) {
          const existing = getNestedValue(newDataModel, message.path) || {};
          setNestedValue(newDataModel, message.path, { ...existing, ...message.value });
        } else {
          return { ...currentState, dataModel: { ...newDataModel, ...message.value } };
        }
      } else if (message.operation === 'delete') {
        if (message.path) {
          deleteNestedValue(newDataModel, message.path);
        }
      }

      return { ...currentState, dataModel: newDataModel };
    }

    case 'deleteSurface': {
      if (!currentState || currentState.surfaceId !== message.surfaceId) return currentState;
      return null;
    }

    default:
      return currentState;
  }
}

// --- Nested path utility ---
function setNestedValue(obj: Record<string, any>, path: string, value: any): void {
  const parts = path.split('.');
  let current = obj;
  for (let i = 0; i < parts.length - 1; i++) {
    if (!(parts[i] in current)) current[parts[i]] = {};
    current = current[parts[i]];
  }
  current[parts[parts.length - 1]] = value;
}

function getNestedValue(obj: Record<string, any>, path: string): any {
  const parts = path.split('.');
  let current = obj;
  for (const part of parts) {
    if (current == null) return undefined;
    current = current[part];
  }
  return current;
}

function deleteNestedValue(obj: Record<string, any>, path: string): void {
  const parts = path.split('.');
  let current = obj;
  for (let i = 0; i < parts.length - 1; i++) {
    if (current == null) return;
    current = current[parts[i]];
  }
  if (current != null) {
    delete current[parts[parts.length - 1]];
  }
}

/**
 * Connects to the backend SSE stream and yields A2UI messages.
 */
export async function* streamA2UIMessages(
  endpoint: string,
  body: Record<string, any>,
  signal?: AbortSignal
): AsyncGenerator<A2UIMessage> {
  const response = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    signal,
  });

  if (!response.ok) {
    throw new Error(`Stream failed: ${response.status} ${response.statusText}`);
  }

  const reader = response.body?.getReader();
  if (!reader) throw new Error('No readable stream');

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
        const data = line.slice(6).trim();
        if (data === '[DONE]') return;
        try {
          yield JSON.parse(data) as A2UIMessage;
        } catch { /* skip malformed */ }
      }
    }
  }
}
