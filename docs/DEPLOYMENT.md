# Deploy to Streamlit Community Cloud

This is a deployment guide, not evidence of a live deployment. Publishing code, changing visibility and creating an app require the owner's explicit approval. No API key is needed for this project.

## 1. Prepare the repository

Complete [PUBLISHING.md](PUBLISHING.md), test the code locally and review the exact files being uploaded. `app.py`, `requirements.txt`, `toolkit/`, `samples/` and `.streamlit/config.toml` must be present. Do not commit `.venv/`, `.env`, `.streamlit/secrets.toml`, private inputs or local notification/test artifacts.

The repository's `requirements.txt` pins direct dependencies. `requirements-lock.txt` is the complete locally verified snapshot; Community Cloud reads the standard `requirements.txt` automatically. Do not add conflicting environment files. The `pyproject.toml` holds project/test metadata, not a separate dependency environment. Select Python **3.12** to match validation. See [Streamlit dependency guidance](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies).

## 2. Create the app after approval

1. Sign in at [Streamlit Community Cloud](https://share.streamlit.io/) and connect the intended GitHub account. Review the permissions requested.
2. Choose **Create app** and the option to deploy an existing app.
3. Select the repository, branch **main**, and entrypoint **app.py**.
4. Choose an available app URL/subdomain if desired.
5. In **Advanced settings**, select Python **3.12**. No secrets are required. Do not enable `TOOLKIT_ALLOW_UPLOADS` on the public demo.
6. Review the settings and deploy. Inspect the build logs for missing dependencies or incompatible versions.
7. Open the resulting `*.streamlit.app` URL and verify all four sample workflows, downloads and warnings. Only then add the real URL to the README and Upwork entry.

The official [deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy) describes repository, branch, entrypoint and Python selection. Private repositories may require additional GitHub permissions; repo privacy and app visibility are separate settings. Review both rather than assuming a private repo makes the app private. [Permissions and platform limitations](https://docs.streamlit.io/deploy/streamlit-community-cloud/status).

## 3. Keep the portfolio demo sample-only

The code defaults to `TOOLKIT_ALLOW_UPLOADS=false`. Without explicitly setting the environment variable to `true`, the UI exposes only fictional fixtures and no upload controls. The app does not read this setting from Streamlit secrets. Leave it unset on Community Cloud.

This avoids inviting public visitors to upload confidential files and reduces exposure to untrusted parser inputs. It does not make the application a hardened multi-tenant service. Demonstrate personal/client uploads only in a separate, access-controlled deployment after a specific security review.

The committed config does not force a loopback server address; let Community Cloud manage server binding. For local work, explicitly use `--server.address 127.0.0.1`.

## 4. Privacy and operational limitations

- On a hosted application, uploaded data would be transferred to the cloud server. In-memory processing is not browser-only processing.
- No authentication, client accounts, audit trail, malware isolation or durable storage is implemented. Public sample-only use is the intended portfolio configuration.
- Community Cloud is a demonstration hosting environment with finite resources. Do not promise 24/7 uptime, fixed capacity or persistent local disk contents. Confirm current limits with the service before making client commitments.
- Multiple sessions can increase memory use even with per-file limits. Large PDFs and concurrent exports can still be expensive. Keep the demo on fictional samples.
- Never copy real credentials into code or commits. Future integrations should use Streamlit's [secrets management](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management), not a committed `secrets.toml`.
- Do not display stack traces, uploaded content or credentials in public logs. Check any new diagnostic code before deployment.
- No OCR is installed. Scanned PDFs need a separately scoped OCR workflow. Do not add Tesseract unless implementing and testing that feature.
- Review AGPL and PyMuPDF licensing before hosting a proprietary derivative. Preserve source availability and applicable notices for this open-source project.

## Troubleshooting and updates

- **Import error:** confirm Python 3.12 and root `requirements.txt`; inspect build logs. Do not add browser-test dependencies to the production environment.
- **Sample missing:** confirm `samples/input/` was committed. The hosted app does not need to regenerate samples at startup.
- **Upload controls absent:** expected in the public demo. Test uploads locally with the explicit opt-in command in the README.
- **PDF has no table:** inspect the original; table detection is best-effort. Never substitute invented rows.
- **Deployment fails:** retain logs privately, fix/test locally, then review and approve the next push. Do not repeatedly change dependency versions without recording what passed.

Deployment and final app visibility must still be verified in your own account. This preparation did not create an app, upload code or change remote settings.
