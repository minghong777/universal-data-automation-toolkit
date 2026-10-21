# Fictional demonstration data

All business names, customer names, identifiers, dates and amounts are synthetic. These files are designed to be public portfolio assets; they contain no real customer records or credentials.

| Input | Purpose |
|---|---|
| `sales_january.csv` | Four rows including one duplicate and one empty row; whitespace and leading-zero order IDs |
| `sales_february.xlsx` | Two compatible sales rows; one missing region |
| `customers.json` | Flat, consistent JSON customer records for conversion |
| `fictional_invoice.pdf` | One text-based invoice page with a bordered three-column table |
| `scanned_invoice.pdf` | Raster-only version to demonstrate the no-text/OCR warning |
| `unsupported_nested.json` | Intentional unsupported JSON example |
| `malformed.csv` | Intentional inconsistent-column example |

`output/` contains cleaned/converted spreadsheets, extraction summaries, text and ZIP bundles produced by the real modules. Rebuild with `python generate_samples.py` from the repository root. This overwrites predefined fictional fixtures only.

Do not put real client files in `samples/`: these directories are intentionally included in Git. Use ignored `private_data/` for private local inputs and inspect every staged file before publishing. Fictional fixtures are not evidence of work for real clients.
