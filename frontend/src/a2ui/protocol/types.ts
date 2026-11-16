/**
 * A2UI Protocol v1.0 Core Specification
 * Standard Envelope & Message Definitions
 */

export type A2UIVersion = "1.0";
export type ComponentId = string;
export type SurfaceId = string;

export interface A2UIComponentNode {
  id: ComponentId;
  component: string;
  props?: Record<string, any>;
  children?: ComponentId[];
}

export interface CreateSurfacePayload {
  surfaceId: SurfaceId;
  catalogId: string;
  title?: string;
  components: A2UIComponentNode[];
  dataModel?: Record<string, any>;
}

export interface UpdateComponentsPayload {
  surfaceId: SurfaceId;
  components: A2UIComponentNode[];
}

export interface UpdateDataModelPayload {
  surfaceId: SurfaceId;
  path?: string;
  value: any;
  operation?: "set" | "merge" | "delete";
}

export interface DeleteSurfacePayload {
  surfaceId: SurfaceId;
}

export interface SurfaceActionPayload {
  surfaceId: SurfaceId;
  componentId: ComponentId;
  action: string;
  payload?: Record<string, any>;
}

// Standard Envelope format
export type A2UIMessage =
  | { version: A2UIVersion; createSurface: CreateSurfacePayload }
  | { version: A2UIVersion; updateComponents: UpdateComponentsPayload }
  | { version: A2UIVersion; updateDataModel: UpdateDataModelPayload }
  | { version: A2UIVersion; deleteSurface: DeleteSurfacePayload }
  | { version: A2UIVersion; surfaceAction: SurfaceActionPayload };

export interface SurfaceState {
  surfaceId: SurfaceId;
  title: string;
  catalogId: string;
  components: Record<ComponentId, A2UIComponentNode>;
  rootId: ComponentId | null;
  dataModel: Record<string, any>;
}
