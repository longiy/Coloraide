# Coloraide Architecture

Blender 5.0+ extension. Python 3.11+. No external dependencies beyond `numpy` and `mathutils`.

---

## Module Map

```
__init__.py                  Registration, app handlers, keymap setup
COLORAIDE_panel.py           Top-level panel dispatcher (Image, View3D, Clip editors)
COLORAIDE_state.py           Single source of mutable runtime state
COLORAIDE_sync.py            Color sync pipeline (picker → all sliders/brush)
COLORAIDE_brush_sync.py      Brush-specific sync path (separate lock from UI sync)
COLORAIDE_cache.py           Deferred Blender property writes (live-sync perf)
COLORAIDE_monitor.py         bpy.app.timers polling loop for color change detection
COLORAIDE_mode_manager.py    Unified API for mode-specific paint settings
COLORAIDE_object_colors.py   Object color detection, scan cache, get/set helpers
COLORAIDE_color_grouping.py  Groups identical colors across objects (Grouped mode)
COLORAIDE_colorspace.py      sRGB ↔ linear math (no Blender API calls)
COLORAIDE_utils.py           HSV, LAB, XYZ conversions + barycentric weights
COLORAIDE_properties.py      WindowManager-level display state (show_* toggles)
operators/                   One file per operator class
panels/                      One file per panel section; panel_helpers.py shared
properties/                  One PropertyGroup per color space; base.py shared
```

---

## Key Design Decisions

### 1. Centralized state (`COLORAIDE_state.py`)

All mutable runtime flags live in one module-level namespace instead of scattered globals across `COLORAIDE_sync.py`, `COLORAIDE_brush_sync.py`, and `COLORAIDE_cache.py`.

**Why:** Recursive sync loops (picker → brush → picker) are prevented by boolean guards. When those guards lived in three modules, debugging required tracing across files. One module = one place to inspect when a sync loop breaks.

**Rule:** Never add new mutable cross-module state outside `COLORAIDE_state.py`. Add it there and import via `from . import COLORAIDE_state as _state`.

---

### 2. Recursion guards as context managers

`update_lock()`, `live_sync_lock()`, `brush_update_lock()` are `@contextmanager` functions that set a flag on enter and clear it on exit, yielding whether the lock was acquired.

```python
with update_lock() as acquired:
    if not acquired:
        return
    # safe to update
```

**Why:** A plain `if _state.is_updating: return` guard can leave the flag set if the protected code raises. Context managers guarantee cleanup even on exception.

---

### 3. Color cache for live sync (`COLORAIDE_cache.py`)

When live-sync is active and the user drags a slider, writing to every synced Blender property on every `update` callback (~60/sec) causes lag. The cache stores pending writes in a plain Python dict and flushes to Blender on a timer (default 100ms) or on mouse release.

**Cache key:** `(obj_name, prop_path)` tuple — intentionally overwrites stale entries for the same property so only the latest value is flushed.

**Three modes** (controlled by addon preferences `live_sync_mode`):
- `IMMEDIATE` — flush on every update (no cache, for low object counts)
- `BATCHED_TIMER` — flush via `bpy.app.timers` at 100ms intervals
- `ON_RELEASE` — flush only when triggered externally on mouse release

---

### 4. Scan cache for object colors (`COLORAIDE_object_colors.py`)

Scanning an object's materials, GeoNodes, and light data can take 50–500ms per object. Results are cached in `_SCAN_CACHE: dict[str, tuple[str, list]]` keyed by `obj.name`.

**Invalidation:** Each cache entry stores a fingerprint hash computed from the object's name, type, modifier count, material names, and node group names. On next access the fingerprint is recomputed and compared; a mismatch triggers a fresh scan.

**Manual invalidation:** `clear_object_cache(obj_name)` uses `dict.pop(obj_name)` — O(1), no string prefix scan.

---

### 5. `SuppressUpdatesMixin` for PropertyGroups (`properties/base.py`)

All Coloraide `PropertyGroup` subclasses share a `suppress_updates: BoolProperty` flag. When code writes to a property programmatically (not from user input), it sets `suppress_updates = True` first so the `update` callback is a no-op.

```python
item.suppress_updates = True
item.color = new_color
item.suppress_updates = False
```

**Rule:** `SuppressUpdatesMixin` must NOT be registered with Blender — only its concrete subclasses. Blender will error if you register a base PropertyGroup.

---

### 6. `ModeManager` for paint settings

Blender 5.0 moved `unified_paint_settings` into mode-specific structs. `ModeManager.get_paint_settings(context)` returns the right struct for the active mode without callers needing to branch on `context.mode`.

**Use this everywhere** instead of inline mode checks. The only exception is poll methods that need fast rejection before `ModeManager` is imported.

---

### 7. Color space convention

All internal color values are **scene linear RGB** (0.0–1.0 floats).

- Hex strings and UI display: sRGB (via `COLORAIDE_colorspace`)
- Blender brush/material colors: scene linear (stored natively)
- `COLOR_GAMMA` Blender properties: sRGB stored, linear needed → convert with `rgb_srgb_to_linear` before use

**Never use the deleted `rgb_to_hex` / `hex_to_rgb` functions** — they bypassed color space conversion and were incorrect. Use `linear_to_hex` / `hex_to_linear`.

---

### 8. Panel structure

`COLORAIDE_panel.py` is the single entry point that calls each sub-panel's `draw_*` function. Order is fixed and controlled by addon preferences (`enable_*` flags).

`draw_collapsible_header(layout, wm_display, show_attr, title)` in `panels/panel_helpers.py` is the standard way to open a collapsible box. Returns `(box, is_open)`.

---

## What Not to Touch

| Area | Reason |
|------|--------|
| Color space math (`COLORAIDE_colorspace.py`) | Photoshop-accurate; tested against reference values |
| LAB/XYZ matrices (`COLORAIDE_utils.py`) | D50/D65 Bradford transform; changing breaks perceptual accuracy |
| Object color scanning logic | Complex BFS + error handling; optimized for single-pass |
| Live sync batching strategy | Performance-critical; regression = UI lag |
| Panel preference flags | User-facing; changing names breaks saved preferences |
