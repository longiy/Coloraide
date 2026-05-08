"""
Centralized mutable state for the Coloraide addon.

All modules that need to coordinate update-lock or cache state import this
module and read/write its attributes directly.  Using a single module means
there is one place to look when debugging race conditions or unexpected state.
"""

# ---------------------------------------------------------------------------
# Update-pipeline guards (prevent recursive sync loops)
# ---------------------------------------------------------------------------

is_updating: bool = False
update_source = None
previous_color: tuple = (0.5, 0.5, 0.5)
is_live_sync_updating: bool = False
is_brush_updating: bool = False

# ---------------------------------------------------------------------------
# Color-cache state (deferred Blender property writes for performance)
# ---------------------------------------------------------------------------

color_cache: dict = {}
is_flush_scheduled: bool = False


def reset():
    """Reset all state — called on unregister or file load."""
    global is_updating, update_source, previous_color
    global is_live_sync_updating, is_brush_updating
    global is_flush_scheduled

    is_updating = False
    update_source = None
    previous_color = (0.5, 0.5, 0.5)
    is_live_sync_updating = False
    is_brush_updating = False
    color_cache.clear()
    is_flush_scheduled = False
