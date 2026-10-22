# Update and verify the Streamlit Community Cloud app

Owner-provided app URL: **https://minghong-data-toolkit.streamlit.app**.

The owner approved and pushed the two-mode update. After a full Community Cloud reboot, hosted sample/upload and session tests passed on 2026-10-22. A GitHub commit alone is not proof of a healthy deployment; repeat the live checklist for future releases.

## Before approving publication

Read [PRIVACY.md](PRIVACY.md): public uploads reach the server, sessions are logically separated rather than process-isolated, dependencies may create cleaned temporary resources, and no confidential-data service or immediate secure erasure is promised. Use non-sensitive test files only.

The update offers both **Try with sample data** and **Upload your own files** in all four workflows. Uploads default to enabled. No secrets, API keys or new package dependencies are needed. `TOOLKIT_ALLOW_UPLOADS=false` is an optional server-environment kill switch, not a required setting or a Streamlit secrets key.

## How the update reaches Community Cloud

1. Review the local tests, screenshots, privacy risks and commit summary.
2. Explicitly approve pushing the reviewed commit to `minghong777/universal-data-automation-toolkit`, branch `main`.
3. Push normally, without force. GitHub Actions should pass tests and the release-file check.
4. In Community Cloud, verify the existing app is configured for that repository, branch `main`, and entrypoint `app.py`. Keep Python **3.12** to match validation; dependencies are supplied by root `requirements.txt`.
5. Community Cloud normally updates when code is pushed to its configured branch. Check build/app logs and the visible UI; if the old version persists, use the app's **Manage app → Reboot app** control.
6. Verify the live URL with the checklist below before calling the update deployed. GitHub CI success is not cloud runtime verification.

Official guidance: [updating a Community Cloud app](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app), [deployment and Python settings](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy), and [rebooting](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app/reboot-your-app).

## Live verification checklist

Use only the committed fictional files, never private client files:

- Open each workflow and confirm both source-mode options are visible.
- Clean & merge: upload January CSV + February XLSX; preview originals; obtain four cleaned rows; download CSV and Excel.
- Convert files: upload customers JSON and an XLSX; check original/export previews and downloads. Reject nested JSON and malformed CSV clearly.
- Extract PDF: preview the original invoice's first page, inspect text/table, download TXT/CSV/Excel/table ZIP. Select or upload the scanned PDF and confirm the OCR warning.
- Organize files: preview originals and rename rules, confirm the new destinations, download ZIP and verify its contents.
- Open two independent browser profiles/contexts; upload same-named files with distinct fictional markers. Each output should contain only its own marker. Clear one session and confirm the other remains unchanged.
- Remove an uploaded PDF and confirm previous results disappear. Change a ZIP naming rule and confirm download approval resets.
- Confirm downloads work in the deployed browser/CSP. Inline data URIs avoid shared server media URLs, but provider/browser behavior must be tested in the actual environment.
- Review logs for errors without publishing cookies, credentials or uploaded contents.

## Repeatable browser checks

With optional Playwright dependencies installed:

```bash
.venv/bin/python scripts/browser_smoke.py --url https://minghong-data-toolkit.streamlit.app
.venv/bin/python scripts/browser_smoke.py --uploads --url https://minghong-data-toolkit.streamlit.app
.venv/bin/python scripts/browser_sessions.py --url https://minghong-data-toolkit.streamlit.app
```

Run these **after each approved update is pushed and deployed**. The scripts handle both the local app page and Community Cloud’s iframe wrapper. The scripts are not evidence of cloud success merely because they pass locally. They save reports/downloads to ignored `artifacts/` and can overwrite curated screenshots with the tested fictional view.

## If creating another deployment

Sign in at https://share.streamlit.io/, select the intended GitHub repository, branch `main`, entrypoint `app.py`, and Python 3.12. No credentials are required by this application. Review app visibility independently of repository visibility. Do not create a competing app when simply updating the owner's existing deployment.

Cloud resources are finite, and local disk is not durable application storage. Do not promise continuous uptime or production capacity. The committed configuration does not force a loopback address; local commands explicitly bind `127.0.0.1`. The optional browser tooling is not a production dependency. No OCR engine is installed.

## Current verification status

The app above passed the sample and real-upload smoke checks plus two-context session tests on 2026-10-22. Initial loading failed at the new PDF-preview import until the owner performed a full **Reboot app**; an ordinary page rerun did not fix it. If a future update imports new helpers and fails during hot reload, inspect logs and perform a full reboot before making further code changes. Verify the app again afterward.
