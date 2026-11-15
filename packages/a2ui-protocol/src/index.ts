/**
 * A2UI v1.0 Core Protocol Definitions
 */

export type A2UIVersion = "1.0";

export type ComponentId = string;
export type SurfaceId = string;

export interface ComponentNode {
  id: ComponentId;
  type: string;
  parentId?: ComponentId | null;
  props?: Record<string, any>;
  children?: ComponentId[];
}

export interface SurfaceLayoutConfig {
  type?: "standard" | "fullscreen" | "modal" | "drawer";
  theme?: {
    mode?: "light" | "dark" | "system";
    primaryColor?: string;
  };
}

export interface CreateSurfaceMessage {
  version: A2UIVersion;
  type: "createSurface";
  surfaceId: SurfaceId;
  catalogId: string;
  title?: string;
  layout?: SurfaceLayoutConfig;
}

export interface UpdateComponentsMessage {
  version: A2UIVersion;
  type: "updateComponents";
  surfaceId: SurfaceId;
  components: ComponentNode[];
}

export interface UpdateDataModelMessage {
  version: A2UIVersion;
  type: "updateDataModel";
  surfaceId: SurfaceId;
  operation: "merge" | "set" | "delete";
  path?: string;
  value: any;
}

export interface DeleteSurfaceMessage {
  version: A2UIVersion;
  type: "deleteSurface";
  surfaceId: SurfaceId;
}

export interface SurfaceActionMessage {
  version: A2UIVersion;
  type: "surfaceAction";
  surfaceId: SurfaceId;
  componentId: ComponentId;
  action: string;
  payload?: Record<string, any>;
}

export type A2UIMessage =
  | CreateSurfaceMessage
  | UpdateComponentsMessage
  | UpdateDataModelMessage
  | DeleteSurfaceMessage
  | SurfaceActionMessage;

export interface SurfaceState {
  surfaceId: SurfaceId;
  title: string;
  catalogId: string;
  layout: SurfaceLayoutConfig;
  components: Map<ComponentId, ComponentNode>;
  rootIds: ComponentId[];
  dataModel: Record<string, any>;
}
