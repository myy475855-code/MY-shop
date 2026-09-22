"""
A small, self-contained set of line icons (24x24, stroke-based) so the app
never depends on an external icon font or CDN. Usage in templates:

    {{ icon('cart') }}
    {{ icon('heart', size=22, css_class='wish-icon') }}
"""

from markupsafe import Markup

ICONS = {
    "search": '<circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
    "cart": '<circle cx="9" cy="20" r="1.4"/><circle cx="18" cy="20" r="1.4"/>'
            '<path d="M2 3h2l2.4 12.2a2 2 0 0 0 2 1.9h8.6a2 2 0 0 0 2-1.6L21 7H6"/>',
    "heart": '<path d="M12 20.5s-7-4.4-9.5-8.6C.8 8.6 2.2 5 5.7 5c2 0 3.4 1.2 4.4 2.7'
             'C11.1 6.2 12.5 5 14.5 5c3.5 0 4.9 3.6 3.1 6.9-2.5 4.2-9.6 8.6-9.6 8.6z"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7"/>',
    "user-plus": '<circle cx="9" cy="8" r="4"/><path d="M2 21c0-4 3.1-6.5 7-6.5s7 2.5 7 6.5"/>'
                 '<line x1="19" y1="8" x2="19" y2="14"/><line x1="16" y1="11" x2="22" y2="11"/>',
    "package": '<path d="M3 7l9-4 9 4-9 4-9-4z"/><path d="M3 7v10l9 4 9-4V7"/>'
               '<line x1="12" y1="11" x2="12" y2="21"/>',
    "box": '<rect x="4" y="8" width="16" height="12" rx="1"/><path d="M4 8l8-5 8 5"/>'
           '<line x1="12" y1="3" x2="12" y2="8"/>',
    "layers": '<path d="M12 3l9 5-9 5-9-5 9-5z"/><path d="M3 13l9 5 9-5"/>',
    "shield": '<path d="M12 2l8 4v6c0 5-3.4 8.6-8 10-4.6-1.4-8-5-8-10V6l8-4z"/>',
    "log-out": '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>'
               '<polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>',
    "tag": '<path d="M20 12l-8 8-9-9V4h7l10 8z"/><circle cx="7.5" cy="7.5" r="1.2"/>',
    "map-pin": '<path d="M12 22s7-6.2 7-12a7 7 0 1 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="10" r="2.4"/>',
    "phone": '<path d="M3 5c0-1 1-2 2-2h2l2 5-2 1c1 3 3 5 6 6l1-2 5 2v2c0 1-1 2-2 2C9 19 3 13 3 5z"/>',
    "plus-circle": '<circle cx="12" cy="12" r="9"/><line x1="12" y1="8" x2="12" y2="16"/>'
                   '<line x1="8" y1="12" x2="16" y2="12"/>',
    "edit": '<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5z"/>',
    "trash": '<path d="M3 6h18"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>'
             '<path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>'
             '<line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/>',
    "check-circle": '<circle cx="12" cy="12" r="9"/><polyline points="8 12 11 15 16 9"/>',
    "circle": '<circle cx="12" cy="12" r="9"/>',
    "x-circle": '<circle cx="12" cy="12" r="9"/><line x1="9" y1="9" x2="15" y2="15"/>'
                '<line x1="15" y1="9" x2="9" y2="15"/>',
    "truck": '<rect x="1" y="7" width="14" height="10" rx="1"/><path d="M15 10h4l3 3v4h-7z"/>'
             '<circle cx="6" cy="19" r="1.6"/><circle cx="17.5" cy="19" r="1.6"/>',
    "trending-up": '<polyline points="3 17 9 11 13 15 21 6"/><polyline points="15 6 21 6 21 12"/>',
    "users": '<circle cx="9" cy="8" r="3.2"/><path d="M3 20c0-3.5 2.7-5.8 6-5.8s6 2.3 6 5.8"/>'
             '<circle cx="17.5" cy="9" r="2.6"/><path d="M15.5 14.3c2.6.4 4.5 2.3 4.5 5.7"/>',
    "grid": '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/>'
            '<rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
    "shopping-bag": '<path d="M6 8h12l1.2 12.2a1.8 1.8 0 0 1-1.8 2H6.6a1.8 1.8 0 0 1-1.8-2L6 8z"/>'
                    '<path d="M9 8V6a3 3 0 0 1 6 0v2"/>',
    "arrow-right": '<line x1="4" y1="12" x2="20" y2="12"/><polyline points="14 6 20 12 14 18"/>',
    "image": '<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="9" r="1.6"/>'
             '<path d="M21 15l-5-5-9 9"/>',
    "chevron-right": '<polyline points="9 6 15 12 9 18"/>',
    "menu": '<line x1="4" y1="7" x2="20" y2="7"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="17" x2="20" y2="17"/>',
    "x": '<line x1="6" y1="6" x2="18" y2="18"/><line x1="18" y1="6" x2="6" y2="18"/>',
    "refresh": '<path d="M21 11a9 9 0 1 0-2.6 6.4"/><polyline points="21 4 21 11 14 11"/>',
}


def icon(name, size=18, css_class="icon", stroke_width="2"):
    """Return an inline <svg> Markup object for the given icon name."""
    body = ICONS.get(name)
    if body is None:
        return Markup("")
    return Markup(
        f'<svg class="{css_class}" width="{size}" height="{size}" viewBox="0 0 24 24" '
        f'fill="none" stroke="currentColor" stroke-width="{stroke_width}" '
        f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>'
    )
