"""Inline downloads delivered with the current session's rendered UI.

No shared /media URL, file registry, static directory or disk export is created.
An inline URI can still be copied/shared by its recipient; this is not DRM.
"""
import base64
import html
from .safety import MAX_TOTAL, ValidationError, safe_name

MIMES = {
    'text/csv', 'text/plain', 'application/zip', 'application/pdf', 'application/json',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
}

def download_markup(label: str, data: bytes, filename: str, mime: str) -> str:
    safe_name(filename)
    if mime not in MIMES:
        raise ValidationError('Unsupported download format.')
    if len(data) > MAX_TOTAL:
        raise ValidationError('Output exceeds the 30 MiB download limit. Filter the data or split the job.')
    encoded = base64.b64encode(data).decode('ascii')
    return (
        f'<a role="button" class="toolkit-download" '
        f'download="{html.escape(filename, quote=True)}" '
        f'href="data:{mime};base64,{encoded}">{html.escape(label)}</a>'
    )

def image_markup(png: bytes) -> str:
    encoded = base64.b64encode(png).decode('ascii')
    return f'<img alt="First page of the original PDF" style="max-width:100%;height:auto" src="data:image/png;base64,{encoded}">'
