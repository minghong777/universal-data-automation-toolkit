# Validation record — public two-mode update

Verified locally on Ubuntu with Python 3.12.15 on 2026-10-22. The owner-approved two-mode revision `fd81e81` was pushed to GitHub; GitHub Actions passed and the hosted app was verified after a full reboot.

## Automated checks

Command: `.venv/bin/python -m pytest -q`

Result: **63 passed, zero failures**.

Coverage includes:

- CSV/XLSX/JSON imports, malformed files, unsupported nested JSON, duplicate JSON keys and invalid constants.
- Merge compatibility/alignment, header collisions, whitespace/case cleanup, blank/duplicate removal, missing values, numeric/literal filtering and sorting.
- Original DataFrame immutability and leading-zero identifiers.
- Formula-safe CSV/Excel exports, control-character and Excel text-length validation.
- Workbook archive traversal, duplicate members, compression limits and DefusedXML entity rejection.
- Upload size/count limits, safe names, ZIP destination validation, collisions and original byte preservation.
- Real text/table PDF extraction, image-only warnings, encrypted/broken PDFs and page limits.
- Both modes in every applicable workspace, owner upload kill switch, original/result previews and scanned-PDF sample selection.
- Two independent AppTest sessions with separate PDF state; clear/navigation/source changes removing session-owned caches.
- Session-owned cache factories, failed replacement removing the previous document and random widget namespace rotation.
- Inline download bytes, HTML escaping, format/size restrictions and absence of shared user-data cache/media-download calls.
- OpenPyXL temporary-resource cleanup after successful exports and simulated save failure.
- Sample regeneration in a temporary test directory rather than mutation of committed fixtures.

## Real-browser verification

The scripts use headless Chrome with its sandbox enabled and fictional files only.

```bash
python scripts/browser_smoke.py --url http://127.0.0.1:8504
python scripts/browser_smoke.py --uploads --url http://127.0.0.1:8504
python scripts/browser_sessions.py --url http://127.0.0.1:8504
```

The smoke checks cover all four workspaces, real fictional uploads, sample mode, downloaded CSV/ZIP bytes, PDF extraction and OCR warnings. Curated screenshots are in `docs/screenshots/`.

The separate session test creates two independent browser contexts and checks:

1. Same filename, different fictional content, distinct correct outputs.
2. Actual downloads matching each session's inline data URI, without a shared media URL.
3. Clear one session; its previous download disappears while the other's result remains intact.
4. Replace a valid file with malformed CSV or unsupported JSON; no old result remains available.
5. ZIP contents match original input bytes; changed rename options reset confirmation.
6. Remove an uploaded PDF via its visible Remove control; the previous extraction/download disappears.

Ignored local reports live in `artifacts/browser-validation.json`, `artifacts/browser-upload-validation.json` and `artifacts/browser-session-validation.json`. These artifacts are not client storage and are not published.

## Streamlit Community Cloud status

Owner-provided URL: https://minghong-data-toolkit.streamlit.app.

**Hosted checks passed on 2026-10-22**, after the owner rebooted the app:

- All four workflows in sample mode and real fictional-file upload mode.
- CSV/TXT/XLSX controls and actual CSV/ZIP downloads; scanned-PDF warning.
- Two independent browser sessions with the same filename but different contents and distinct outputs.
- Clear one session without affecting the other; reject malformed replacement uploads without leaving old outputs.
- Preserve original ZIP member bytes, reset rename confirmation, and remove stale PDF results when its file is removed.

The initial hot update produced an ImportError while importing the new PDF preview function. A full Community Cloud reboot resolved it. The browser scripts now handle Community Cloud's iframe wrapper and wait for the clear-session rerender before selecting a new input mode. These tests use non-sensitive fictional data and do not establish confidential-data security or unlimited hosting capacity. New releases should repeat the live checklist.

## Demonstration expectations

- January CSV + February XLSX: six input rows become four, one duplicate and one blank removed, `001` preserved and one missing region retained.
- Fictional invoice: one page and one detected table, with original first-page visual preview.
- Scanned invoice: no fabricated text/table; explicit OCR warning.
- Organizer: new names/folders in a ZIP, originals unchanged.

## Scope

These checks demonstrate application-level session separation and the tested workflows, not process/container isolation, universal PDF accuracy, a penetration test, antivirus protection, guaranteed RAM erasure, hosted multi-user capacity or regulatory compliance. Inline data URIs belong to the receiving UI but can be copied by their recipient. See `docs/PRIVACY.md` for remaining risks.
