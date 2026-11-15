# Astryx Component Catalog Specification (v1.0)

## Overview
The Astryx Component Catalog defines the standard mapping between A2UI component declarations and rendered UI elements.

## Component Registry

### 1. Layout
- **`Container`**: Max-width wrapper with padding and flex/grid controls.
  - *Props*: `maxWidth` ("sm" | "md" | "lg" | "xl" | "full"), `padding`, `className`, `style`.
- **`Row`**: Horizontal flex container.
  - *Props*: `gap`, `align` ("start" | "center" | "end"), `justify` ("start" | "center" | "between" | "around"), `wrap` (boolean).
- **`Column`**: Vertical flex container.
  - *Props*: `gap`, `align`, `justify`.
- **`Grid`**: Responsive CSS grid.
  - *Props*: `cols` (number | object), `gap`.

### 2. Typography
- **`Heading`**: Headings H1 to H6.
  - *Props*: `level` (1..6), `text` (string | data-bind), `variant` ("default" | "gradient" | "muted").
- **`Text`**: Paragraph or span.
  - *Props*: `text` (string | data-bind), `size` ("xs" | "sm" | "base" | "lg" | "xl"), `color`, `weight`.

### 3. Actions
- **`Button`**: Interactive action trigger.
  - *Props*: `label`, `variant` ("primary" | "secondary" | "outline" | "ghost" | "danger"), `size`, `icon`, `onClickAction` (event dispatch).

### 4. Display
- **`Card`**: Elevated surface card.
  - *Props*: `title`, `description`, `bordered`, `hoverable`.
- **`Badge`**: Status badge or label pill.
  - *Props*: `label`, `variant` ("success" | "warning" | "danger" | "info" | "neutral").
- **`Image`**: Responsive image element.
  - *Props*: `src`, `alt`, `aspectRatio`, `rounded`.

### 5. Form & Inputs
- **`Input`**: Text / number / email input bound to data model.
  - *Props*: `placeholder`, `valuePath` (data binding path), `type`, `label`.
- **`Select`**: Dropdown select.
  - *Props*: `options` (array of {label, value}), `valuePath`, `label`.
- **`Checkbox`**: Toggle switch or checkbox.
  - *Props*: `label`, `checkedPath`.

### 6. Interactive Data Components (Specialized for Table / JSON Inputs)
- **`DataTable`**: Interactive table with sorting, pagination, and search filter.
  - *Props*: `dataPath` (path to records array in dataModel), `columns` (array of {key, title, sortable, type, badgeMap}), `pageSize`, `searchable`.
- **`MetricsCard`**: KPI / statistic summary card.
  - *Props*: `label`, `valuePath`, `change` (+/- percentage), `trend` ("up" | "down").

---

## Validation & Fallback Policy
1. Any component missing from the registry renders `<AstryxFallbackComponent id={id} type={type} error="..." />`.
2. Invalid props are filtered and logged; default prop values are applied gracefully.
