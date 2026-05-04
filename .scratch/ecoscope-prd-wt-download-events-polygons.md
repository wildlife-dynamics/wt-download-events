---
title: 'wt-download-events: Polygon Event Support'
repo_name: 'wt-download-events'
workflow_id: 'download_events'
created: '2026-05-05'
status: 'ready-for-dev'
change_type: 'modification'
data_sources: [set_er_connection]
reference_workflows: [patrols, events, encounter-rate]
new_tasks: [filter_by_geometry_type]
modified_tasks: [get_events, apply_reloc_coord_filter]
---

# PRD: wt-download-events — Polygon Event Support

**Created:** 2026-05-05
**Repo:** `~/MEP/wt-workflows/wt-download-events/`
**Workflow ID:** `download_events`
**Change type:** Modification (not a new workflow)

## Overview

### Problem Statement

EarthRanger event types can have a Polygon geometry — users tap 3+ points to define an area (e.g., project boundaries), and ER stores the result as a closed GeoJSON polygon whose exterior ring vertices are exactly those tapped points. Today, `wt-download-events` silently reduces every polygon event to its centroid, because the underlying `EarthRangerClient.get_events()` defaults `force_point_geometry=True` and the platform `get_events` task does not expose this parameter.

This blocks Eden's workflow: they use polygon events to record project boundaries and want to download the polygons (alongside their point events) for QA. ER Web also doesn't show the per-point breakdown of polygon events, so the downloaded data is currently their only path to verifying vertex placement.

### Solution

Modify `wt-download-events` to preserve polygon geometries end-to-end:

1. Plumb `force_point_geometry=False` through the platform `get_events` task and hardcode it `false` in this workflow's partial.
2. Make `apply_reloc_coord_filter` polygon-safe by passing through non-Point geometries instead of accessing `.x`/`.y`.
3. Add a custom `filter_by_geometry_type` task to split a mixed-geometry GDF by geometry type at the map-rendering stage only (data persistence stays unified).
4. In the Generate Maps group: build a polygon layer alongside the existing point layer, combine the per-group layer lists with `groupbykey`, and feed the merged layer-pairs into the existing `draw_ecomap` chain — one map widget per group, two layer types stacked.
5. Persist behavior is unchanged structurally: a single output file per group with mixed Point + Polygon rows. Parquet preserves geometry natively; CSV emits WKT (documented in field description).

### Scope

**In Scope:**
- Preserve Polygon (and MultiPolygon) geometries in `get_events` output.
- Render polygon events on the existing map widget as a second layer alongside point events.
- One persisted file per group containing all event geometries (mixed Point + Polygon).
- Backwards-compatible behavior for point-only event runs.
- Test coverage for: polygon-only, mixed-geometry, and existing point-only cases.

**Out of Scope:**
- Vertex extraction into a separate point GDF (deferred — partner reviews polygons directly).
- Polygon-aware bounding-box / ROI filtering. Polygons are pass-through in `apply_reloc_coord_filter`.
- New form-level toggle for `force_point_geometry`. Hardcoded `false` for this workflow.
- Changes to `wt-download-patrols`, `wt-download-subjects`, or the catalog `events` workflow.

## Data Sources & Connections

| Source | Type | Connection | Notes |
| ----- | ---- | ---------- | ----- |
| EarthRanger | Events (Point + Polygon) | `set_er_connection` | Same connection as today; only the geometry-handling flag changes |

## Reference Workflows

| Workflow | What we borrow |
| --- | --- |
| `patrols` | The `groupbykey` pattern at [patrols/spec.yaml:461-489](../../patrols/spec.yaml) — combining two parallel per-group layer lists into a single ecomap input via `unpack_depth: 1`. |
| `events` | Polygon layer styling at [events/spec.yaml:441-461](../../events/spec.yaml) — confirms `create_polygon_layer` parameters used in the catalog. |
| `encounter-rate` | Additional reference for `groupbykey` + `draw_ecomap` mapvalues pattern. |

## Task Changes

### New Custom Task

| Task | Purpose | Library |
| --- | --- | --- |
| `filter_by_geometry_type(df, geometry_types: list[str])` | Returns rows of `df` whose `geometry.geom_type` is in `geometry_types`. ~5 lines. Lives in `ecoscope-workflow-task-library` under `tasks/transformation/`. | `ecoscope_workflows_ext_custom` |

### Modified Platform Tasks

| Task | File | Change |
| --- | --- | --- |
| `get_events` | `ecoscope/platform/tasks/io/_earthranger.py:576` | Add `force_point_geometry: bool = True` kwarg; pass to `client.get_events(...)`. Backwards-compatible default. |
| `apply_reloc_coord_filter` | `ecoscope/platform/tasks/transformation/_filtering.py:30` | In `envelope_reloc_filter`, return `True` (pass-through) for any geometry whose `geom_type != "Point"`. Single-line guard. |

### Spec.yaml Diff Summary

**Modified existing tasks:**
- `get_event_data` partial: add `force_point_geometry: false`.

**New tasks (in Generate Maps task-group, after `rename_display_columns`):**

```yaml
- name: Filter Points for Map Layer
  id: filter_points_for_map
  task: filter_by_geometry_type
  partial:
    geometry_types: ["Point"]
  mapvalues:
    argnames: df
    argvalues: ${{ workflow.rename_display_columns.return }}

- name: Filter Polygons for Map Layer
  id: filter_polygons_for_map
  task: filter_by_geometry_type
  partial:
    geometry_types: ["Polygon", "MultiPolygon"]
  mapvalues:
    argnames: df
    argvalues: ${{ workflow.rename_display_columns.return }}

- name: Create polygon layer from grouped Events
  id: grouped_events_polygon_layer
  task: create_polygon_layer
  skipif:
    conditions:
      - any_is_empty_df
      - any_dependency_skipped
      - all_geometry_are_none
  partial:
    layer_style:
      fill_color_column: "event_type_colormap"
      get_line_width: 2
      opacity: 0.4
    legend:
      label_column: "Event Type"
      color_column: "event_type_colormap"
    tooltip_columns: ["Event Serial", "Event Time", "Event Type", "Reported By"]
  mapvalues:
    argnames: geodataframe
    argvalues: ${{ workflow.filter_polygons_for_map.return }}

- name: Combine Point and Polygon layers per group
  id: combined_event_map_layers
  task: groupbykey
  skipif:
    conditions:
      - all_keyed_iterables_are_skips
    unpack_depth: 1
  partial:
    # Polygon layer FIRST — deck.gl renders layers in list order, later on top.
    # Points should sit visually on top of polygon fills for readability.
    iterables:
      - ${{ workflow.grouped_events_polygon_layer.return }}
      - ${{ workflow.grouped_events_map_layer.return }}
```

**Rewired existing tasks:**
- `grouped_events_map_layer` (`create_point_layer`): change `mapvalues.argvalues` from `workflow.rename_display_columns.return` to `workflow.filter_points_for_map.return`.
- `grouped_events_ecomap` (`draw_ecomap`): change `mapvalues.argvalues` from `workflow.grouped_events_map_layer.return` to `workflow.combined_event_map_layers.return`.

**Net spec growth:** +4 task entries, 2 input rewires, 1 partial addition. (~25 → ~29 task entries.)

## Output Configuration

### Maps

| Map | Layer Type | Style Config | Legend | Notes |
| --- | --- | --- | --- | --- |
| Events Map (point layer) | `create_point_layer` | `fill_color_column: event_type_colormap`, `get_radius: 5` | label: Event Type, color: event_type_colormap | Unchanged from today; input rewired to point-filter output |
| Events Map (polygon layer) | `create_polygon_layer` | `fill_color_column: event_type_colormap`, `get_line_width: 2`, `opacity: 0.4` | shares legend with point layer | New; rendered on the same ecomap. Layer order in `groupbykey` iterables = polygons first → points painted on top. |

Both layers share the `event_type_colormap` column (applied once before the geometry split), so polygons and their related point events get matching colors.

Tooltips identical across layers: `Event Serial`, `Event Time`, `Event Type`, `Reported By`.

### Charts

None — workflow has no charts.

### Data Exports

| Export | Format | Sanitize | Notes |
| --- | --- | --- | --- |
| Events (per group) | Parquet (default) / CSV (optional) | true | Single output per group with mixed-geometry rows. Polygons preserved natively in Parquet; written as WKT in CSV. |

`persist_events.filetypes.default` stays `["parquet"]`. The field description gains a note: *"For polygon events, parquet preserves geometry natively; CSV writes the geometry column as WKT."*

### Dashboard

Unchanged: one map widget per group. The widget now shows two layer types stacked.

## Form Configuration (rjsf)

### Form Structure (only changed sections)

#### Get Event Data

No change to user-facing fields. `force_point_geometry: false` lives in the partial (hidden).

#### Persist Events

| Field | Label | Type | Default | Visible | Notes |
| --- | --- | --- | --- | --- | --- |
| filetypes | Export Formats | array of enum | `["parquet"]` | advanced | Constrained to csv/parquet. **Description updated** to note CSV emits WKT for polygons. |

#### Generate Maps

No new top-level fields. The polygon layer's style is hardcoded in the partial; not exposed to the form. `Skip Map Generation` toggle still applies to the whole map group (both layers).

### rjsf-overrides Diff

```yaml
rjsf-overrides:
  properties:
    # Existing entries unchanged. New/changed entries:
    persist_events.properties.filetypes.description: >-
      Output filetypes for the events dataset. Parquet preserves all geometry types
      natively (recommended for polygon events). CSV writes the geometry column as
      Well-Known Text (WKT) — readable but not directly round-trippable into all GIS
      tools.
```

### Validation Checklist

- [x] No new user-facing fields introduced
- [x] CSV/WKT note added to filetypes description
- [x] Existing form structure preserved
- [x] No `ui:order` introduced

## Test Strategy

### Test Cases

Existing 11 cases are unchanged in behavior — they should all continue to pass since the underlying mock for `get_events` is point-only and the polygon branch will skip cleanly via `all_geometry_are_none`.

**New cases:**

| Case Name | mock_io | mock_io_overrides | Purpose |
| --- | --- | --- | --- |
| `polygon-events` | true | `ecoscope.platform.tasks.io.get_events: dev/fixtures/get-events-polygon.example-return.parquet` | Validate polygon branch end-to-end with deterministic mocked data. Fixture contains mixed Point + Polygon rows so the geometry-split logic is exercised. |
| `mixed-geometries-live` | false | (none) | Live integration against `mep_dev` for an event-type set known to contain Eden's polygon events. Validates the real-world shape. |

**Params drafting:** Both new cases inherit the structure of `base` (workflow_details, time_range, er_client_name with `data_source.name: mep_dev`, filter_events with empty filter_point_coords, persist_events with `filetypes: ["parquet"]`, etc.). Case-specific decisions:
- `polygon-events.params.time_range`: any window — fixture data ignores this since IO is mocked. Reuse `base`'s 2026-01-01 → 2026-01-16 range.
- `mixed-geometries-live.params.get_event_data.event_types`: `["arr_project_boundary"]` — Eden's polygon event type for project boundaries. Pick a `time_range` known to contain at least one such event (TBD at implementation: query mep_dev for the date of an existing `arr_project_boundary` event and use a window around it; if none exist yet, ask Eden to create a test record before running the live case).

**Credentials for `mixed-geometries-live`:** Resolved from environment variables at runtime — never in test-cases.yaml, never in spec.yaml. Required vars (from the `ecoscope-workflows-ext-ecoscope` connection convention):

```bash
ECOSCOPE_WORKFLOWS__CONNECTIONS__EARTHRANGER__MEP_DEV__SERVER=https://mep-dev.pamdas.org
ECOSCOPE_WORKFLOWS__CONNECTIONS__EARTHRANGER__MEP_DEV__USERNAME=<user>
ECOSCOPE_WORKFLOWS__CONNECTIONS__EARTHRANGER__MEP_DEV__PASSWORD=<password>
# OR token-based auth:
ECOSCOPE_WORKFLOWS__CONNECTIONS__EARTHRANGER__MEP_DEV__TOKEN=<token>
```

Set these in a local `.env` (gitignored) or `export` in the shell before running `./dev/run-test-cases.sh --case mixed-geometries-live`. The mocked `polygon-events` case does NOT need them.

### Mock Fixture Contents (`dev/fixtures/get-events-polygon.example-return.parquet`)

- 5 rows total
- 2 Polygon events (one with 4 vertices, one with 5 vertices) using event_type values that match the mock display-name lookups
- 2 Point events using overlapping event_types so the colormap shares colors
- 1 row with null geometry to exercise the `include_null_geometry` / `all_geometry_are_none` skipif paths
- Times spread across the test case's `time_range` so the temporal index has something to do
- All other columns present in the existing point-only mock fixture (event_details, reported_by, etc.) so downstream processing is fully exercised

### skipif Conditions (changes only)

| Task | Conditions | Rationale |
| --- | --- | --- |
| `filter_points_for_map` | inherits global (`any_is_empty_df`, `any_dependency_skipped`) | If no point events, polygon-only branch still runs |
| `filter_polygons_for_map` | inherits global | If no polygon events, point-only branch still runs |
| `grouped_events_polygon_layer` | + `all_geometry_are_none` | Polygon layer skips cleanly when filter yields empty |
| `combined_event_map_layers` | `all_keyed_iterables_are_skips`, `unpack_depth: 1` | Standard `groupbykey` skip |

### Validation Approach

- `polygon-events` (mocked): verify map output HTML contains both polygon and point layer references; verify single persisted file per group has mixed geometry types preserved.
- `mixed-geometries-live`: verify against `mep_dev` that polygon events come back with Polygon geometry (not centroid) and the workflow completes without error.
- `base` (existing, point-only): regression — full pipeline still passes; output unchanged.
- All other existing cases: regression pass (no behavior change expected).

## Development Strategy

This is a modification, not a new workflow. No phasing dance with `load_df` is needed since the data source (ER) and overall pipeline structure are unchanged. Implementation order:

1. **Phase A — Task-library changes (blocking).** Add `filter_by_geometry_type` to `ecoscope-workflow-task-library`. Modify `get_events` and `apply_reloc_coord_filter` in the `ecoscope` platform task library. Cut a release of each (or use `path:` + `editable: true` during dev).

2. **Phase B — Spec changes.** Wire up `force_point_geometry: false`, the two filter tasks, the polygon layer, and the `groupbykey` combine. Compile + run the existing test cases as regression.

3. **Phase C — Test fixtures + new cases.** Generate the polygon mock fixture (likely by hand-crafting a parquet with shapely, or by snapshotting from a live ER call). Add the two new test cases.

4. **Phase D — Validate at config-form-playground.** Confirm the form is unchanged for users and the description update on filetypes is visible.

## Implementation Plan

### progress.yaml

Generated at `.scratch/progress-wt-download-events-polygons.yaml`.

### Acceptance Criteria

- [ ] **AC 1 (polygon preservation):** Given an EarthRanger time range that contains polygon events, when the workflow runs, then the persisted parquet file contains rows where `geometry.geom_type == "Polygon"` (i.e., not silently centroidized).
- [ ] **AC 2 (mixed-geometry persist):** Given a time range with both polygon and point events, when the workflow runs, then a single output file per group contains rows of both geometry types.
- [ ] **AC 3 (map rendering):** Given polygon and point events in the same group, when the map is rendered, then both layer types appear on the same ecomap, sharing the `event_type_colormap` and legend.
- [ ] **AC 4 (point-only regression):** Given a time range with only point events, when the workflow runs, then existing behavior is preserved (single point layer, point-only persisted file, no errors from empty polygon branch).
- [ ] **AC 5 (polygon-only):** Given a time range with only polygon events, when the workflow runs, then the persisted file contains polygon geometries, the polygon layer renders, and the point layer skips cleanly without breaking the dashboard.
- [ ] **AC 6 (CSV WKT):** Given a polygon event and CSV output enabled, when the file is written, then the geometry column contains a valid WKT POLYGON string.
- [ ] **AC 7 (filter pass-through):** Given a polygon event in a region the user has set up a bounding-box exclusion for, when `apply_reloc_coord_filter` runs, then the polygon passes through unchanged (no `.x`/`.y` AttributeError, no incorrect filtering).
- [ ] **AC 8 (form unchanged):** Given the rjsf form for this workflow, when rendered at config-form-playground, then no new top-level fields appear and the existing form structure is preserved.

## Additional Context

### Dependencies

- `ecoscope-platform >= 2.11.11, < 2.12.0` — needs a release that includes the `get_events` and `apply_reloc_coord_filter` changes (or a bump if those changes ship in a later platform version).
- `ecoscope-workflows-ext-custom` — needs a release that includes `filter_by_geometry_type` (currently `0.1.0rc3` in spec.yaml).

### Notes

- The `force_point_geometry=False` change at the `get_event_data` partial means **all** events in the result preserve their native geometry, not just polygons. Point events are already Points; this is a no-op for them.
- The `apply_reloc_coord_filter` change is intentionally permissive — polygons are pass-through, never excluded by bounding-box or exact-coord filters. If we ever want polygon-aware ROI filtering, that's a separate task (e.g., `filter_polygons_by_intersect`).
- The polygon layer's `opacity: 0.4` default lets underlying basemap and overlapping point events remain visible. Adjustable in the partial if Eden requests a stronger fill.
- The mock-IO override mechanism (`mock_io_overrides` in test-cases.yaml) was added to `run-test-cases.sh` recently — see [template/dev/run-test-cases.sh:189-202](../../../infra/ecoscope-hub/template/dev/run-test-cases.sh) for the implementation. This is the first PRD that uses it.
- ER docs validation: polygon events store the user's tapped points as the polygon's exterior ring vertices (closed GeoJSON polygon). There is no separate "tap log" or related-event store. See [ER Support: Report Areas Web](https://support.earthranger.com/report-area-as-location).
