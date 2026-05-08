"""Shared UI drawing helpers for Coloraide panels."""


def draw_collapsible_header(layout, wm_display, show_attr, title):
    """Draw a collapsible box header.

    Returns (box, is_open) so the caller can conditionally draw content inside box.
    """
    box = layout.box()
    is_open = getattr(wm_display, show_attr)
    row = box.row()
    row.prop(wm_display, show_attr,
             text=title,
             icon='TRIA_DOWN' if is_open else 'TRIA_RIGHT',
             emboss=False)
    return box, is_open
