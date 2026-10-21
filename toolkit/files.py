"""Preview virtual file operations; write only new in-memory ZIP archives."""
from dataclasses import dataclass
from io import BytesIO
from pathlib import PurePosixPath
import zipfile
from .safety import ValidationError, safe_name, validate_batch

@dataclass(frozen=True)
class FileOperation:
    index: int
    original: str
    destination: str
    size: int

def plan_files(files, prefix='', find='', replace='', numbered=False, organize='none', rules_text=''):
    validate_batch(files)
    if organize not in {'none','extension','prefix rules'}:raise ValidationError('Unknown organization mode.')
    for value in (prefix,find,replace):
        if any(c in value for c in '/\\') or any(ord(c)<32 for c in value):raise ValidationError('Rename fields cannot contain paths or control characters.')
    rules=[]
    if organize=='prefix rules':
        for line in rules_text.splitlines():
            if not line.strip():continue
            if '=' not in line:raise ValidationError('Use one prefix=folder rule per line.')
            key,folder=[s.strip() for s in line.split('=',1)]
            if not key:raise ValidationError('Rule prefix cannot be empty.')
            safe_name(folder);rules.append((key,folder))
    used=set();operations=[]
    for i,(name,data) in enumerate(files):
        renamed=prefix+(name.replace(find,replace) if find else name)
        if numbered:renamed=f'{i+1:03d}_'+renamed
        safe_name(renamed)
        folder=''
        if organize=='extension':folder=PurePosixPath(renamed).suffix.lower().lstrip('.') or 'no_extension'
        elif organize=='prefix rules':folder=next((v for k,v in rules if name.startswith(k)),'other')
        if folder:safe_name(folder)
        candidate=f'{folder}/{renamed}' if folder else renamed
        if candidate.casefold() in used:
            raise ValidationError('Renaming creates duplicate destinations. Enable numbering or change the rules.')
        used.add(candidate.casefold());operations.append(FileOperation(i,name,candidate,len(data)))
    return operations

def build_zip(files, operations):
    validate_batch(files)
    if len(operations)!=len(files) or {op.index for op in operations}!=set(range(len(files))):
        raise ValidationError('File plan is incomplete.')
    seen=set();buf=BytesIO()
    with zipfile.ZipFile(buf,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for op in operations:
            p=PurePosixPath(op.destination)
            if p.is_absolute() or any(x in {'','.', '..'} for x in op.destination.split('/')):
                raise ValidationError('Unsafe archive destination.')
            for part in op.destination.split('/'):safe_name(part)
            if op.destination.casefold() in seen:raise ValidationError('Duplicate ZIP destination.')
            seen.add(op.destination.casefold())
            name,data=files[op.index]
            if name!=op.original or len(data)!=op.size:raise ValidationError('Files changed after preview; regenerate the plan.')
            z.writestr(op.destination,data)
    return buf.getvalue()

def zip_outputs(outputs):
    files=list(outputs.items())
    return build_zip(files,plan_files(files))
