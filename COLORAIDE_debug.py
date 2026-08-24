"""
Central debug logging for Coloraide.

Always prints to the system console. When "Create Debug Log" is enabled in
addon preferences, also appends timestamped lines to a Blender text block
(Coloraide_Debug_Log) so users can copy/paste diagnostics into bug reports
without digging through the console.
"""
import datetime
import platform
import sys

import bpy

LOG_NAME = "Coloraide_Debug_Log"
# This module lives at the package root, so __package__ is the full addon
# key Blender registers under (e.g. "bl_ext.user_default.Coloraide" for an
# extension install) — NOT __name__.split('.')[0], which would only be
# "bl_ext" and never match, silently disabling logging.
_ADDON_KEY = __package__


def _get_prefs():
    try:
        return bpy.context.preferences.addons[_ADDON_KEY].preferences
    except Exception:
        return None


def is_enabled():
    prefs = _get_prefs()
    return bool(prefs and getattr(prefs, "enable_debug_log", False))


def log(message, category="INFO"):
    """Log a diagnostic message. Always goes to console; also appended to
    the Coloraide_Debug_Log text block when debug logging is enabled."""
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [{category}] {message}"
    print(f"Coloraide: {line}")

    if not is_enabled():
        return
    try:
        text = bpy.data.texts.get(LOG_NAME)
        if text is None:
            text = bpy.data.texts.new(LOG_NAME)
        text.write(line + "\n")
    except Exception:
        pass


def log_startup_diagnostics():
    """Dump platform/Blender/GPU info - the first thing worth having in any bug report."""
    try:
        import gpu
        backend = gpu.platform.backend_type_get()
    except Exception:
        backend = "unknown"

    log(
        f"Blender {bpy.app.version_string} | Python {sys.version.split()[0]} | "
        f"OS: {platform.platform()} | GPU backend: {backend}",
        "STARTUP",
    )


def clear_log():
    text = bpy.data.texts.get(LOG_NAME)
    if text:
        text.clear()
    else:
        bpy.data.texts.new(LOG_NAME)
