# A2UI Protocol Specification (v1.0)

## Overview
A2UI (Agent-to-User Interface) is a declarative, streaming UI protocol that enables AI agents to construct, mutate, and manage interactive client interfaces dynamically.

## Core Message Types

### 1. `createSurface`
Initializes a new UI surface (canvas / page / modal) with an assigned ID and layout mode.
```json
{
  "version": "1.0",
  "type": "createSurface",
  "surfaceId": "page-main",
  "catalogId": "astryx-web-v1",
  "title": "Landing Page & Dashboard",
  "layout": {
    "type": "standard",
    "theme": {
      "mode": "dark",
      "primaryColor": "#3b82f6"
    }
  }
}
```

### 2. `updateComponents`
Inserts, updates, or replaces component nodes inside an active surface.
```json
{
  "version": "1.0",
  "type": "updateComponents",
  "surfaceId": "page-main",
  "components": [
    {
      "id": "hero-section",
      "type": "Container",
      "parentId": null,
      "props": {
        "className": "py-16 px-6 max-w-6xl mx-auto text-center"
      },
      "children": ["hero-heading", "hero-subtext", "cta-button"]
    },
    {
      "id": "hero-heading",
      "type": "Heading",
      "parentId": "hero-section",
      "props": {
        "level": 1,
        "text": "Build Interactive Websites with AI"
      }
    }
  ]
}
```

### 3. `updateDataModel`
Merges or updates reactive data within the surface's local store.
```json
{
  "version": "1.0",
  "type": "updateDataModel",
  "surfaceId": "page-main",
  "operation": "merge",
  "path": "dataset",
  "value": {
    "records": [
      { "id": 1, "name": "Enterprise Plan", "status": "Active", "mrr": 2400 },
      { "id": 2, "name": "Startup Plan", "status": "Pending", "mrr": 490 }
    ],
    "filter": "all"
  }
}
```

### 4. `deleteSurface`
Tears down a surface and frees its associated state.
```json
{
  "version": "1.0",
  "type": "deleteSurface",
  "surfaceId": "page-main"
}
```

### 5. `surfaceAction` (Client-to-Agent Event)
Dispatched from the client when a component triggers an agent-bound action.
```json
{
  "version": "1.0",
  "type": "surfaceAction",
  "surfaceId": "page-main",
  "componentId": "generate-chart-btn",
  "action": "executeAgentTask",
  "payload": {
    "task": "generate_revenue_chart",
    "parameters": { "granularity": "monthly" }
  }
}
```
