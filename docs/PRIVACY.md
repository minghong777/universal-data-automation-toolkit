# Public uploads: privacy, session handling and remaining risks

## Intended use

This is a public portfolio demonstration for **non-sensitive test files**, not a confidential document-processing service. Visitors may use fictional samples or their own supported files. Uploaded contents travel to the machine hosting Streamlit, including Community Cloud when hosted there.

## How sessions are separated

- Each browser connection has its own Streamlit session state and uploader widgets. There is no module-level upload/result registry and no `st.cache_data` or `st.cache_resource` containing user files.
- The only application-owned retained document result is the current PDF result/preview, in that session's state. It is replaced on file changes and discarded when the document is removed, the input mode changes, the workflow changes, or the session is cleared.
- File controls use a session-specific random namespace. Clearing a session rotates that namespace and drops the session's widget/result references; it does not clear another visitor's state.
- CSV/XLSX/TXT/ZIP downloads and the PDF page image are embedded as inline data URIs in the current session's UI. The application does not register user-generated output in Streamlit's shared media-file store, create static public output URLs, or write shared export files.
- Two independent browser-context tests use the same input filename with different fictional contents, verify distinct outputs/downloads, and check that clearing one session does not affect the other.

These are application-level separation measures, **not** per-visitor process/container isolation or protection against a compromised host, a parser vulnerability, malicious browser extensions, stolen sessions or an authorized recipient sharing their own output. A data URI contains the output itself; a user who copies it can disclose the content. Do not promise a formal tenant-security guarantee based only on these tests.

## Storage and cleanup

Application code does not intentionally save uploads, extracted text or generated client outputs to a database or shared output directory. Uploaded bytes, DataFrames, previews and output bytes exist in server/session memory while in use. Inline download payloads also exist in the receiving browser.

OpenPyXL uses securely named temporary worksheet files internally while streaming Excel exports. The app explicitly cleans those resources after successful and failed saves, with regression tests. A process crash, filesystem failure or platform failure can still interrupt cleanup. No guaranteed zero-disk processing or secure disk erasure is claimed.

**Clear my session** resets the app's references and file controls. Streamlit retains ownership of its upload buffers, session transport and internal lifecycle; garbage collection/disconnection cleanup is not an immediate secure RAM wipe. The app cannot erase already downloaded files, browser caches/history, developer tools, operating-system swap, platform backups or provider logs. Navigation changes intentionally reset current uploads to avoid retaining previous workflows' data.

The application's source does not log uploaded contents or deliberately call third-party services with them. This is not a guarantee about all hosting-provider behavior, telemetry, access logs or crash diagnostics. Review the provider's policies before using actual client data.

## Limits and residual risks before publication

1. **Untrusted parsers:** PDF and workbook parsing uses third-party/native code. File-type, archive, page and row checks reduce mistakes but do not sandbox malware or patch unknown vulnerabilities.
2. **Denial of service:** limits are 10 MiB per file, 30 MiB per batch, 30 files, 100,000 tabular rows, 200 columns, 100 PDF pages and 2 million extracted text characters. Limits do not provide a hard per-user CPU/RAM quota; concurrent visitors or complex compressed files can exhaust shared resources.
3. **Download overhead:** each output is capped at 30 MiB. Inline base64 increases browser/server message size and memory use by roughly one third before other copies. Large exports should be split rather than treated as production-scale jobs.
4. **No client authentication:** the application has no user accounts, access audit, entitlement model or enterprise retention controls. Public visitors should upload fictional or otherwise non-sensitive material only.
5. **User-controlled originals:** source files are never modified. ZIP members are renamed copies, not local filesystem moves; archives are not unpacked. The organizer can contain any opaque file type, so recipients should still treat downloaded contents with care.
6. **Business limitations:** PDF/OCR accuracy, styles/formula preservation, schema compatibility and cleanup behavior are documented in the README. No missing facts are invented.
7. **Licensing:** AGPL source licensing and PyMuPDF's licensing model still apply to hosting and client derivatives.

For confidential client work, use a separately scoped authenticated deployment with process isolation, resource quotas, retention policies, monitoring and an independent security review. Owners can set `TOOLKIT_ALLOW_UPLOADS=false` in the server environment as a kill switch, leaving sample mode available. It defaults to `true`; no environment setting is needed for both public modes.

## Verification scope

Unit/AppTest coverage and real-browser tests validate designed data flow, session separation and cleanup for fictional fixtures. They are not a penetration test or a compliance certificate. Cloud verification must be performed against the deployed revision, not inferred from local tests. See `VALIDATION.md` and `DEPLOYMENT.md`.
