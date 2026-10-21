"""Review Git candidate files without staging or printing sensitive matched values.

This is a heuristic release aid, not a comprehensive secret scanner or audit.
Ignored files, previous Git history and image pixels are outside its scope.
"""
from pathlib import Path
from io import BytesIO
import json
import re
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    'private_key': re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    'github_token': re.compile(rb'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})'),
    'aws_access_key': re.compile(rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b'),
    'openai_style_key': re.compile(rb'\bsk-(?:proj-)?[A-Za-z0-9_-]{32,}'),
    'credential_assignment': re.compile(rb'''(?i)(?:api[_-]?key|access[_-]?token|api[_-]?secret|password)\s*[=:]\s*["'][A-Za-z0-9_+/.=-]{20,}["']'''),
    'personal_home_path': re.compile(rb'/home/[A-Za-z0-9_.-]+/|/Users/[A-Za-z0-9_.-]+/'),
}

def scan_blob(label, data, findings, depth=0):
    for kind,pattern in PATTERNS.items():
        if pattern.search(data):findings.append({'file':label,'finding':kind})
    if data.startswith(b'PK\x03\x04'):
        if depth>=3:
            findings.append({'file':label,'finding':'archive_depth_exceeds_review_limit'});return
        try:
            with zipfile.ZipFile(BytesIO(data)) as archive:
                members=archive.infolist()
                if len(members)>2000 or sum(i.file_size for i in members)>60*1024*1024:
                    findings.append({'file':label,'finding':'archive_exceeds_review_limit'});return
                for member in members:
                    if not member.is_dir():scan_blob(label+'::'+member.filename,archive.read(member),findings,depth+1)
        except (zipfile.BadZipFile,RuntimeError,OSError):
            findings.append({'file':label,'finding':'unreadable_archive'})

def run():
    root=subprocess.run(['git','rev-parse','--show-toplevel'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip()
    if Path(root).resolve()!=ROOT:
        raise SystemExit('Stop: initialize a separate Git repository inside this project before reviewing it.')
    output=subprocess.run(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT,capture_output=True,check=True).stdout
    names=sorted(set(n.decode('utf-8') for n in output.split(b'\0') if n))
    findings=[]
    for name in names:
        path=ROOT/name
        if path.is_symlink():
            findings.append({'file':name,'finding':'symlink_requires_manual_review'});continue
        if not path.is_file():continue
        if any(p in {'private','private_data','client_data','customer_data','uploads','.venv','artifacts'} for p in path.relative_to(ROOT).parts):
            findings.append({'file':name,'finding':'private_or_runtime_path_in_release'})
        if path.stat().st_size>10*1024*1024:
            findings.append({'file':name,'finding':'large_file_requires_manual_review'});continue
        scan_blob(name,path.read_bytes(),findings)
    report={'candidate_files':len(names),'findings':findings,
            'scope':'Current Git candidate text/bytes and bounded ZIP members; no history or visual image audit.'}
    print(json.dumps(report,indent=2))
    return 1 if findings else 0

if __name__=='__main__':sys.exit(run())
