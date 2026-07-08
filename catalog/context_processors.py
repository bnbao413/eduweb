import re

from .models import PageOverlay, SiteTheme

_HEX = re.compile(r'#[0-9A-Fa-f]{3,8}\Z')


def site_theme(request):
    """Build a `:root{…}` CSS override string from the saved SiteTheme, injected
    after app.css so a staff-chosen palette applies site-wide (incl. editors)."""
    css = ''
    try:
        t = SiteTheme.objects.first()
        if not t:
            return {'site_theme_css': ''}
        decls = []

        def ok(v):
            return bool(v) and bool(_HEX.match(v))

        if ok(t.bg):
            decls.append(f'--bg:{t.bg};')
        if ok(t.surface):
            decls.append(f'--surface:{t.surface};')
        if ok(t.surface_2):
            decls.append(f'--surface-2:{t.surface_2};')
        if ok(t.border):
            decls.append(f'--border:{t.border};--border-strong:{t.border};')
        if ok(t.text):
            decls.append(f'--text:{t.text};')
        if ok(t.accent):
            a = t.accent
            decls.append(f'--accent:{a};--accent-hover:{a};--accent-active:{a};'
                         f'--accent-border:{a};--ring:0 0 0 2px {a};')
        if ok(t.on_accent):
            decls.append(f'--on-accent:{t.on_accent};')

        if decls:
            css = ':root{' + ''.join(decls) + '}'
    except Exception:
        css = ''
    return {'site_theme_css': css}


def page_overlay(request):
    """Inject the saved overlay items for the current URL path into every page,
    so staff-placed images/GIFs/text show for all visitors."""
    items = []
    try:
        ov = PageOverlay.objects.filter(path=request.path).first()
        if ov and isinstance(ov.items, list):
            items = ov.items
    except Exception:
        items = []
    return {'page_overlay_items': items}
