"""Bound uploads and archive expansion without extracting untrusted ZIPs."""
from io import BytesIO
from pathlib import PurePosixPath
import re
import zipfile

MAX_FILE = 10 * 1024 * 1024
MAX_TOTAL = 30 * 1024 * 1024
MAX_FILES = 30
MAX_EXPANDED = 60 * 1024 * 1024

class ValidationError(ValueError):
    """An actionable, safe-to-display validation failure."""

def safe_name(name: str) -> str:
    if not name or name in {'.', '..'} or '/' in name or '\\' in name:
        raise ValidationError('Use a plain filename without folders or path separators.')
    if any(ord(c) < 32 for c in name) or re.search(r'[<>:"|?*]', name):
        raise ValidationError('Filename contains unsupported characters.')
    if name.endswith((' ', '.')) or len(name.encode('utf-8')) > 180:
        raise ValidationError('Filename is too long or ends with a space/dot.')
    if name.split('.')[0].upper() in {'CON','PRN','AUX','NUL',*(f'COM{i}' for i in range(1,10)),*(f'LPT{i}' for i in range(1,10))}:
        raise ValidationError('Reserved filename. Choose another name.')
    return name

def validate_upload(name: str, data: bytes, allowed: set[str] | None = None):
    safe_name(name)
    if not data:
        raise ValidationError('The file is empty.')
    if len(data) > MAX_FILE:
        raise ValidationError('Each file must be at most 10 MiB.')
    suffix = PurePosixPath(name).suffix.lower()
    if allowed is not None and suffix not in allowed:
        raise ValidationError('Unsupported file type. Allowed: ' + ', '.join(sorted(allowed)))
    return suffix

def validate_batch(files: list[tuple[str, bytes]]):
    if not files or len(files) > MAX_FILES:
        raise ValidationError('Choose between 1 and 30 files.')
    if sum(len(data) for _, data in files) > MAX_TOTAL:
        raise ValidationError('Combined uploads must be at most 30 MiB.')
    for name, data in files:
        validate_upload(name, data)

def check_workbook(data: bytes):
    try:
        with zipfile.ZipFile(BytesIO(data)) as z:
            infos = z.infolist()
            if len(infos) > 2000 or sum(i.file_size for i in infos) > MAX_EXPANDED:
                raise ValidationError('Workbook expands beyond the safety limit.')
            names = {i.filename for i in infos}
            if len(names) != len(infos):
                raise ValidationError('Workbook archive contains duplicate entries.')
            if not {'[Content_Types].xml', 'xl/workbook.xml'} <= names:
                raise ValidationError('This is not an XLSX workbook.')
            for i in infos:
                p = PurePosixPath(i.filename)
                if p.is_absolute() or '..' in p.parts or '\\' in i.filename or i.flag_bits & 1:
                    raise ValidationError('Unsafe or encrypted workbook archive.')
                if i.file_size and i.file_size / max(i.compress_size, 1) > 1000:
                    raise ValidationError('Workbook compression ratio exceeds the safety limit.')
    except (zipfile.BadZipFile, OSError) as e:
        raise ValidationError('Malformed XLSX workbook.') from e
