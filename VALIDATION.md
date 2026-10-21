# Validation record

Verified locally on Ubuntu with Python 3.12.15 on 2026-10-21.

## Automated checks

Command: `.venv/bin/python -m pytest -q`

Result: **48 passed** (service tests plus five Streamlit AppTest workflows).

Coverage includes:

- Compatible/reordered merges, incompatible columns and normalization collisions.
- Whitespace/case cleanup, blank/duplicate removal, missing values, literal and numeric filters, and sorting.
- Leading-zero ID preservation and input DataFrame immutability.
- Valid CSV/XLSX/JSON; malformed CSV, unsupported/nested JSON, repeated JSON keys and invalid JSON constants.
- Literal XLSX formula storage and CSV formula protection for values and headers.
- Workbook archive traversal and compression-ratio limits, per-file limits and batch-count limits.
- ZIP byte preservation, collision detection, unsafe names, prefix rules and incomplete/tampered plans.
- Real text-based PDF table/text extraction, image-only OCR warnings, damaged/encrypted PDFs and page limits.
- XLSX text length limits with CSV fallback.
- Each Streamlit workspace loading without exceptions and each sample workflow producing previews.
- Default sample-only mode, explicit upload opt-in and the public scanned-PDF selector.
- Duplicate workbook archive members and XML entity defense with DefusedXML.

## Browser integration

Both modes were checked with headless Chrome using Playwright and the browser sandbox enabled:

- Default **sample-only mode**: all four workspaces, CSV/ZIP downloads, no upload controls, and the scanned-PDF sample warning. The latest curated images in `docs/screenshots/` match this mode.
- Explicit **trusted local upload mode**: actual fictional CSV/XLSX, JSON and PDF uploads; four output rows; CSV download; organizer confirmation/ZIP download; and the image-only PDF warning.

Commands (with a matching server running):

```bash
python scripts/browser_smoke.py
python scripts/browser_smoke.py --uploads --url http://127.0.0.1:8502
```

Transient reports are kept in ignored `artifacts/browser-validation.json` and `artifacts/browser-upload-validation.json`; downloads are also local/ignored. These are not required to run the app and are not included in the public repository. This is not a cross-browser, accessibility or cloud-hosting audit.

## Clean release-candidate copy

The Git candidate files were copied to a fresh temporary directory without `.venv/`, ignored artifacts or other workspace projects. Using the verified Python dependency environment, the complete suite again passed **48 tests with zero failures**. This confirms the fixtures/source needed by tests are included in the proposed release; it is not an independent clean dependency installation or a GitHub Actions run.

## Demonstration results

- CSV + XLSX: 6 rows → 4 rows; 1 blank and 1 duplicate removed; ID `001` preserved; 1 missing region retained.
- Fictional invoice: 1 page, 1 detected table, invoice identifier present in extracted text.
- Scanned invoice: no extracted text or fabricated table; warning shown.
- Organized ZIP: original content bytes retained in new filenames/folders.

## Scope of evidence

These checks use fictional, controlled files. They do not establish accuracy on all client PDFs, large-scale service reliability, antivirus protection, hosted multi-user isolation or business savings. The browser checks used a trusted local server with fictional files.

## Additional scale check

A 10,000-row, three-column XLSX export/import completed locally in approximately 0.62 seconds and preserved the leading-zero identifier `000000`. This is a local sample measurement, not a general performance guarantee.
