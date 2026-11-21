import {
  A2UIMessage,
  SurfaceState,
  A2UIComponentNode,
  ComponentId
} from '../protocol/a2ui-types';

/**
 * A2UI v1.0 Pure Message Processor
 */
export class A2UIRuntime {
  /**
   * Applies an A2UI protocol message to the current surface state
   */
  public static processMessage(
    message: A2UIMessage,
    currentState: SurfaceState | null
  ): SurfaceState | null {
    if (!message || message.version !== '1.0') {
      console.warn('A2UIRuntime: Unsupported protocol message', message);
      return currentState;
    }

    // 1. createSurface
    if ('createSurface' in message) {
      const payload = message.createSurface;
      const componentMap: Record<ComponentId, A2UIComponentNode> = {};
      let rootId: ComponentId | null = null;

      for (const comp of payload.components) {
        componentMap[comp.id] = comp;
        if (comp.id === 'root' || (!rootId && !payload.components.some(c => c.children?.includes(comp.id)))) {
          rootId = comp.id;
        }
      }

      return {
        surfaceId: payload.surfaceId,
        title: payload.title || 'Untitled Surface',
        catalogId: payload.catalogId,
        components: componentMap,
        rootId: rootId || (payload.components[0]?.id ?? null),
        dataModel: payload.dataModel || {},
      };
    }

    // 2. updateComponents
    if ('updateComponents' in message) {
      const payload = message.updateComponents;
      if (!currentState || currentState.surfaceId !== payload.surfaceId) {
        return currentState;
      }

      const updatedMap = { ...currentState.components };
      for (const comp of payload.components) {
        updatedMap[comp.id] = comp;
      }

      return {
        ...currentState,
        components: updatedMap,
      };
    }

    // 3. updateDataModel
    if ('updateDataModel' in message) {
      const payload = message.updateDataModel;
      if (!currentState || currentState.surfaceId !== payload.surfaceId) {
        return currentState;
      }

      const newDataModel = { ...currentState.dataModel };
      if (payload.path) {
        this.setPathValue(newDataModel, payload.path, payload.value, payload.operation || 'set');
      } else {
        if (payload.operation === 'merge' && typeof payload.value === 'object') {
          Object.assign(newDataModel, payload.value);
        } else {
          return { ...currentState, dataModel: payload.value };
        }
      }

      return {
        ...currentState,
        dataModel: newDataModel,
      };
    }

    // 4. deleteSurface
    if ('deleteSurface' in message) {
      if (currentState && currentState.surfaceId === message.deleteSurface.surfaceId) {
        return null;
      }
      return currentState;
    }

    return currentState;
  }

  private static setPathValue(target: Record<string, any>, path: string, value: any, op: 'set' | 'merge' | 'delete'): void {
    // Normalizes JSON pointer path (e.g., "/pricing/tier" -> ["pricing", "tier"])
    const cleanPath = path.startsWith('/') ? path.slice(1) : path;
    const parts = cleanPath.split('/');
    let current = target;

    for (let i = 0; i < parts.length - 1; i++) {
      const part = parts[i];
      if (!(part in current) || typeof current[part] !== 'object') {
        current[part] = {};
      }
      current = current[part];
    }

    const lastKey = parts[parts.length - 1];
    if (op === 'delete') {
      delete current[lastKey];
    } else if (op === 'merge' && typeof value === 'object') {
      current[lastKey] = { ...current[lastKey], ...value };
    } else {
      current[lastKey] = value;
    }
  }
}
