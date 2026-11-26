/**
 * A2UI Protocol v1.0 Core Specification
 * Standard Envelope & Message Definitions
 */

export type A2UIVersion = "1.0";
export type ComponentId = string;
export type SurfaceId = string;

export type GridColumns = 1 | 2 | 3 | 4;
export interface ResponsiveGridColumns {
  base?: GridColumns;
  sm?: GridColumns;
  md?: GridColumns;
  lg?: GridColumns;
}

export interface A2UIComponentProps extends Record<string, any> {
  className?: string;
  maxWidth?: "sm" | "md" | "lg" | "xl" | "full";
  paddingX?: "none" | "sm" | "md" | "lg";
  cols?: GridColumns | ResponsiveGridColumns;
  gap?: "sm" | "md" | "lg";
  scale?: "sm" | "md" | "lg" | "xl" | "display";
  size?: "xs" | "sm" | "base" | "md" | "lg" | "xl";
  weight?: "normal" | "medium" | "semibold" | "bold";
  tone?: "default" | "muted" | "accent" | "inverse";
  align?: "left" | "center" | "right";
  variant?: "default" | "soft" | "outline" | "elevated" | "primary" | "secondary" | "ghost";
  ratio?: "wide" | "tall" | "square";
  fit?: "cover" | "contain";
  position?: "center" | "top" | "bottom" | "left" | "right";
}

export interface A2UIComponentNode {
  id: ComponentId;
  component: string;
  props?: A2UIComponentProps;
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
