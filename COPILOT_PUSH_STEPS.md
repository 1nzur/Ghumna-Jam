# Copilot Push Steps

Project folder:

```text
C:\Users\LEGION\Documents\Codex\2026-05-23\doctype-html-html-lang-en-head
```

This project contains:

- `index.html` and `script.js` for the frontend
- `app.py` for the Flask backend
- `schema.sql` for the MySQL database schema
- `requirements.txt` for Python dependencies
- `.env.example` for sample database environment variables

Do not commit `.env`.

## Goal

Push this whole folder to the connected GitHub account.

## Preferred VS Code Way

1. Open this folder in VS Code.
2. Open the Source Control tab.
3. Stage all files.
4. Commit with this message:

```text
Create trek booking app with Flask and MySQL
```

5. Click Publish Branch or Sync Changes.

## Terminal Commands

Only use these if GitHub repo remote is already correct:

```bash
git status
git add .
git commit -m "Create trek booking app with Flask and MySQL"
git branch -M main
git push -u origin main
```

If the remote is wrong, set it to the user's actual GitHub repository URL:

```bash
git remote remove origin
git remote add origin https://github.com/USERNAME/REPOSITORY.git
git push -u origin main
```
