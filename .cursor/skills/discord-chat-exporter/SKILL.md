---
name: discord-chat-exporter
description: Run and maintain the Discord chat export tool locally, including Python dependency setup, one-click bat startup, Discord Bot token setup, channel URL export, and precise datetime filtering. Use when the user asks to export Discord messages, fix local startup issues, add export features, or troubleshoot this project's exporter workflow.
---

# Discord Chat Exporter Workflow

## When to use

Use this skill when the user wants to:
- Export Discord forum/text channel chat logs.
- Filter export by start/end datetime (hour/minute precision).
- Run this project locally on Windows with bat scripts.
- Fix startup issues such as missing Python/pip/dependencies.
- Enhance export behavior in this codebase.

## Project anchors

- Backend: `app.py`
- Frontend page: `templates/index.html`
- Dependency list: `requirements.txt`
- One-click scripts: `启动.bat`, `首次安装.bat`, `安装Python.bat`, `更新并启动.bat`
- Export output dir: `exports/`

## Standard execution flow

1. **Check runtime**
   - Verify Python availability (`python --version`).
   - If missing, use local installer script (`安装Python.bat`) or install Python 3.7+.
   - Verify pip and install dependencies from `requirements.txt`.

2. **Start app**
   - Prefer `启动.bat` for daily run.
   - Confirm service is reachable at `http://localhost:5000`.

3. **Configure export inputs**
   - Ensure Bot Token is set in UI.
   - Accept one or multiple channel URLs (`https://discord.com/channels/<guild>/<channel>`), one per line.
   - Support datetime range (use `datetime-local` style input, e.g. `2026-03-02T14:30`).

4. **Run export and verify**
   - Start export and monitor status polling.
   - Verify output file is generated and downloadable.
   - Confirm expected format (`excel` / `txt` / `html`) and message counts.

## Implementation rules for feature changes

When implementing exporter enhancements:

1. **Frontend input consistency**
   - Keep time controls aligned with backend parser format.
   - For minute-level precision, use `input[type="datetime-local"]`.

2. **Backend parsing compatibility**
   - Parse preferred datetime format first (`%Y-%m-%dT%H:%M`).
   - Keep backward compatibility for date-only format (`%Y-%m-%d`).
   - For date-only end time, normalize to end-of-day (`23:59:59`).

3. **Filtering behavior**
   - Apply `date_from` / `date_to` consistently to both forum-thread messages and normal channel messages.
   - Keep sort order stable before export output.

4. **Non-breaking updates**
   - Preserve existing export formats and download route behavior.
   - Do not remove bat-based quick-start workflow.

## Troubleshooting checklist

1. **`python` not found**
   - Check whether Python exists but not in PATH.
   - Try absolute Python path if available.
   - Re-run `安装Python.bat` or reinstall with PATH enabled.

2. **`pip` missing**
   - Run `python -m ensurepip --default-pip`.
   - Then `python -m pip install -r requirements.txt`.

3. **App starts but UI unavailable**
   - Verify process output contains `Running on http://127.0.0.1:5000`.
   - Check local firewall/port conflicts.

4. **Export returns empty**
   - Validate Bot permission (`View Channel`, `Read Message History`).
   - Verify channel URLs and datetime range.
   - Check token validity and API errors.

## Response template for this skill

When assisting, structure output as:

1. What was fixed/changed.
2. Files touched.
3. How to run now (`启动.bat` first).
4. Quick verification steps.
5. Optional next step (e.g., package as exe, add logs, add retries).
