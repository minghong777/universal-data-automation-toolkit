# Publish this project to GitHub: beginner walkthrough

**Project boundary:** this project has its own local Git repository on branch `main`. The intended GitHub repository is `https://github.com/minghong777/universal-data-automation-toolkit`, created publicly by its owner. Local preparation may already include `origin` and an initial commit; inspect the commands below before repeating setup. A local commit does not mean any code has been pushed.

No push is authorized by this document. Obtain the owner's explicit confirmation before uploading code. The project originally sat inside a larger workspace; work inside this project directory only.

Preparing files does not publish them. `git add` stages local changes; `git commit` creates a local snapshot; `git push` uploads snapshots to GitHub. GitHub repository visibility is a separate setting.

## 1. Open the correct directory

On the original computer:

```bash
cd ~/ai-workspace/universal-data-automation-toolkit
pwd
git rev-parse --show-toplevel
git status --short
git remote -v
```

The Git root must be **the project folder**, not `ai-workspace`. Stop if the Git root includes other projects. `git remote -v` should either print nothing before setup or show only the intended repository above. On another computer, substitute the directory containing this project.

For a fresh copy that does not have its own `.git` directory, initialize it once:

```bash
git init -b main
```

Do not copy the parent workspace's `.git` directory. No research projects, account settings, personal files or old workspace history belong in this repository.

## 2. Run checks and inspect the candidate files

```bash
.venv/bin/python -m pytest -q
.venv/bin/python scripts/release_check.py
git status --short --untracked-files=all
git add --dry-run .
```

Review names as well as content. Only fictional files under `samples/` are intended for publication. `private_data/`, `.env*`, virtual environments, local artifacts and secrets are ignored. A `.gitignore` rule does not protect secrets already committed; inspect staged content every time. The scanner is a heuristic aid, not a guarantee.

## 3. Set the identity used on commits

Use your own public-facing name and a GitHub-provided **noreply email** if you do not want your personal email in public history. Find the exact noreply address in GitHub **Settings → Emails**. Replace the placeholders below; do not type credentials into commands or commit messages.

```bash
git config --local user.name "YOUR_PUBLIC_NAME"
git config --local user.email "YOUR_GITHUB_NOREPLY_EMAIL"
```

These settings apply only to this project. They do not sign in to GitHub.

## 4. Stage and commit locally

```bash
git add .
git diff --cached --stat
git diff --cached --name-only
git diff --cached --check
git diff --cached
```

The last command may open a pager; press **q** to exit. Do not commit if you see client records, `.env`, tokens, private paths, notification receipts, unrelated projects, or an unwanted email address.

If a file was staged by mistake before the first commit, unstage it without deleting the working file:

```bash
# Replace PRIVATE_FILE with the exact relative path; do not include real secrets here.
git rm --cached -- PRIVATE_FILE
```

Update `.gitignore` if needed, inspect again, then:

```bash
git commit -m "Initial release: reusable Python data automation toolkit"
git log -1 --format=fuller
git status --short
```

This is still entirely local. Read the author email in the log before proceeding.

## 5. Stop for explicit publication approval

Before any upload, decide:

- Which GitHub account will own the repository?
- Is the repository name `universal-data-automation-toolkit` acceptable?
- Have you reviewed the staged/committed content and AGPL license?
- Do you approve pushing this exact project? Do you also approve public visibility?

A private upload still sends the files to GitHub and requires your approval. Do not run the following sections until you approve those actions. If asking an assistant to perform them, explicitly give that approval and the intended GitHub account/repository.

## Existing public repository: this project's next step

The owner has already created `minghong777/universal-data-automation-toolkit` as a public repository. Do not create another repository or change visibility unnecessarily. Recheck that `origin` matches exactly and inspect remote refs before the first push:

```bash
git remote -v
git ls-remote --symref origin
```

The preparation check found no remote branches or tags. Recheck after approval because the remote can change. If remote content appears, fetch and inspect it before proceeding; do not overwrite it or use force push.

After the owner explicitly approves pushing to this **public** destination, authenticate and run:

```bash
# If GitHub CLI is installed, sign in using its browser flow.
gh auth login
gh auth setup-git
gh auth status

# Upload the already reviewed local commit only after confirmation.
git push -u origin main
```

If `gh` is not installed, install it from the official link below or use an existing SSH/Git credential manager setup. GitHub HTTPS does not accept an ordinary account password for Git pushes. Never paste a personal access token into chat, source code, the remote URL or a shell command. A public read check does not establish authenticated write permission.

After a successful push, compare local and remote commit IDs and inspect the required paths on GitHub:

```bash
git rev-parse HEAD
git ls-remote origin refs/heads/main
git ls-tree --name-only HEAD
```

Required contents: README, `app.py`, `toolkit/`, `samples/`, `tests/`, `PORTFOLIO.md`, `docs/` and dependency files. Check the Actions test result as well. This verification must follow an actual successful push; it has not been claimed in advance.

The remaining sections describe a private-first alternative for a **different, new repository**. Skip them for the owner's already-created public repository unless the owner chooses that alternative.

## 6. Create and push a PRIVATE repository after approval

The following route uses GitHub CLI for authentication and repository creation, then ordinary Git to push. Install GitHub CLI if necessary using its [official installation instructions](https://github.com/cli/cli#installation).

```bash
gh auth login
gh auth setup-git
gh auth status
```

Choose GitHub.com and HTTPS in the login flow, and sign in through the browser. Do not share passwords or tokens in chat. Inspect which account `gh auth status` selected.

Replace `YOUR_GITHUB_USERNAME` below:

```bash
gh repo create YOUR_GITHUB_USERNAME/universal-data-automation-toolkit \
  --private \
  --description "Reusable Python toolkit for spreadsheet cleaning, format conversion, PDF extraction, and file organization." \
  --source=. \
  --remote=origin

git remote -v
git push -u origin main
```

`gh repo create` creates a remote repository. `git push` uploads the local commit. Creating it without `--push` keeps those actions distinct so you can inspect the remote address first. Confirm the uploaded files on GitHub, including the README, samples and screenshots. Check the repository is still **Private**.

### Alternative: create it on the GitHub website

Create a new **Private** repository named `universal-data-automation-toolkit`. Leave the README, `.gitignore` and license initialization boxes unchecked because this project already has them. Then:

```bash
gh auth login
gh auth setup-git
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/universal-data-automation-toolkit.git
git remote -v
git push -u origin main
```

Choose one creation route, not both. If `origin` already exists, inspect it before changing anything. Do not use `--force` to solve an unexpected history conflict.

## 7. Make it PUBLIC only after a separate confirmation

Review the private repository first. Then explicitly confirm public release. You can change visibility in GitHub **Settings → General → Danger Zone → Change repository visibility**, following GitHub's confirmation dialog.

Or, after explicit approval, run:

```bash
gh repo edit YOUR_GITHUB_USERNAME/universal-data-automation-toolkit \
  --visibility public \
  --accept-visibility-change-consequences
```

Public visibility makes repository content and commit history available to others. The acknowledgement flag is significant; do not run it casually. This guide does not authorize anyone else to execute it for you.

## 8. Finish the portfolio presentation

- Add repository description and relevant topics: `python`, `streamlit`, `data-cleaning`, `excel`, `csv`, `pdf`, `automation`.
- Confirm screenshot links render in the README and use the short description in `PORTFOLIO.md` for Upwork.
- Deploy the sample-only app only when ready; follow [DEPLOYMENT.md](DEPLOYMENT.md).
- Add an actual live demo URL only after opening and testing it. Never publish a placeholder as if it were working.
- For later updates, inspect `git diff`, run checks, commit, and only then perform an approved `git push`. Avoid `git add .` outside the project directory.

Official references: [GitHub's local-project publishing guide](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github?platform=linux), [GitHub CLI repository creation](https://cli.github.com/manual/gh_repo_create), and [GitHub CLI visibility changes](https://cli.github.com/manual/gh_repo_edit).
