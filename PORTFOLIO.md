# Python Data Automation Toolkit | Excel, CSV, JSON & PDF Workflows

## Concise English description

**Suggested Upwork entry:**

I built a Python data automation toolkit for cleaning and merging spreadsheets, converting CSV/Excel/JSON, extracting text-based PDF content, and organizing files with preview-first ZIP exports. The Streamlit interface includes fictional demos, before-and-after previews, validation messages and reusable processing modules. Automated tests cover core workflows and safety checks. This is an independent portfolio project using synthetic data.

**Expanded project description:**

I built a reusable Python application that turns repetitive file-processing tasks into clear, repeatable workflows. It combines spreadsheet cleaning and merging, validated format conversion, text-based PDF extraction, and preview-based batch file organization in a Streamlit interface. Users can inspect results before downloading outputs, while original uploads remain unchanged. The public portfolio mode uses fictional samples only; trusted local uploads require an explicit opt-in. This independent portfolio demonstration uses fictional datasets and includes automated tests, setup instructions, and documented limitations.

## Key features

- Merge compatible Excel/CSV exports, clean whitespace, remove duplicate/empty rows, and report missing values.
- Inspect before/after previews, filter records and sort results.
- Convert CSV, selected Excel worksheets, and compatible flat JSON to reusable CSV/XLSX outputs.
- Extract PDF text and detected tables; explicitly flag pages that may need OCR.
- Preview batch renames and extension/prefix-based folders, then download a new ZIP.
- Validate malformed inputs, limit resource use and reject unsafe paths and naming collisions.
- Protect exported spreadsheets from formula-like uploaded text.
- Reuse UI-independent service modules for future client workflows.

## Technologies

Python 3.11+ (tested on 3.12), Streamlit, Pandas, OpenPyXL, PyMuPDF, DefusedXML, Pytest, standard-library ZIP/JSON/CSV and in-memory streams. No paid API required.

## Suggested screenshots

1. Overview: four workflows and a clear value proposition.
2. Clean & merge: six input rows become four, with before/after previews and modification metrics.
3. Missing-value report: one missing region visibly retained instead of invented.
4. PDF extraction: fictional invoice text and detected table, plus a separate scanned-PDF warning.
5. Organizer: original → destination preview and ZIP download after confirmation.

Use fictional sample data in every image. Do not show real customer files, credentials or private paths.

## 60-second demonstration script

**0–8 seconds:** “This Python toolkit automates common spreadsheet and file tasks, with clear previews and reusable processing modules.”

**8–25 seconds:** Open Clean & merge with its fictional sample. “Here I combine a CSV and an Excel export. Six rows become four after trimming text and removing one duplicate and one blank row. IDs retain their leading zeros. Missing information stays visible.” Download the cleaned Excel file.

**25–35 seconds:** Open Convert files with its sample. “Structured JSON records can become a spreadsheet. Invalid or nested structures produce explicit errors.”

**35–47 seconds:** Open Extract PDF with its sample. “I extract existing text and detected tables from this fictional invoice. Scanned pages are flagged for OCR; the app never fabricates missing data.”

**47–57 seconds:** Open Organize files with its sample. “I preview numbered filenames and extension folders before downloading a ZIP. Originals remain unchanged.”

**57–60 seconds:** “The project includes automated tests and documentation so these workflows can be adapted to a client's process.”

## Honest scope

This is a self-directed working sample, not paid client work. It demonstrates automation engineering, not guaranteed business savings, perfect PDF recognition, or unrestricted format support. Exact delivery scope and acceptance examples should be agreed before a client project. PyMuPDF's licensing must be reviewed before closed-source delivery.

## Captured demonstration images

The browser validation produces actual screenshots, not visual mockups:

- `docs/screenshots/01-overview.png`
- `docs/screenshots/02-clean-merge.png`
- `docs/screenshots/03-convert.png`
- `docs/screenshots/04-pdf.png`
- `docs/screenshots/05-organizer.png`
- `docs/screenshots/06-ocr-warning.png`
