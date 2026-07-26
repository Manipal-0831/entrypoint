# EntryPoint

A job board dedicated to one thing: IT jobs for freshers. Anyone with an
account can browse and search listings, save the ones they like, discuss
them in comments — and just as importantly, post a job lead they've come
across themselves (a link, a screenshot of a WhatsApp/flyer post, or both),
not just employers. Built to demonstrate a complete path from code to a
live, CI/CD-deployed product.

**Why this instead of a generic job board?** General boards bury entry-level
roles under years of experienced listings. EntryPoint only allows fresher,
0-1 year, or internship postings — and search filters are built around that,
so a fresh graduate never has to wade through senior roles. It's also
crowd-sourced: anyone (a senior, a recruiter, a friend) can share a lead they
heard about, similar in spirit to how fresher job alerts already circulate
informally in WhatsApp/Telegram groups — just organized and searchable.

## Features

- Single account type: every logged-in user can browse, search, post, save,
  and comment — no separate employer/seeker signup flow to get in the way
- **Explicit fresher search**: keyword (title/skills/company), location, job
  type, and a fresher-level filter (Fresher (0 yrs) / 0-1 yrs / Internship)
- Post a job with title, company, location, description, required skills,
  an optional external link (to apply or view the original posting), and an
  optional image URL (e.g. a screenshot of the source post)
- Save ("bookmark") jobs — instant, no reload, powered by `fetch()`
- Comment on a listing to ask questions or share tips — same instant pattern
- Owners can close/reopen their own listings
- Personal dashboard: jobs you've posted + jobs you've saved
- Pagination on the search results

## Tech stack

| Layer      | Choice                                            | Why |
|------------|----------------------------------------------------|-----|
| Backend    | Python, Flask (application factory + blueprints)   | Matches the requested stack |
| Database   | MySQL in production, SQLite for local dev          | Same SQLAlchemy models work against both — just swap `DATABASE_URL` |
| ORM        | Flask-SQLAlchemy                                    | No hand-written SQL required |
| Auth       | Flask-Login + Flask-Bcrypt                          | Session-based auth, hashed passwords |
| Frontend   | Jinja2 templates + hand-written CSS + vanilla JS    | No build step — deploys as-is |
| Deployment | Vercel (Python/Flask runtime)                       | Flask deploys to Vercel with zero config |
| CI/CD      | GitHub Actions                                      | Lints and tests every push/PR, deploys `main` to Vercel automatically |

## Project structure

```
entrypoint/
├── app/
│   ├── __init__.py        # application factory
│   ├── config.py          # env-driven configuration (fresher levels, job types)
│   ├── extensions.py      # db, login_manager, bcrypt instances
│   ├── models.py          # User, Job, SavedJob, Comment
│   ├── auth/routes.py     # register, login, logout
│   ├── main/routes.py     # search/feed, job detail, post/edit job, dashboard
│   ├── api/routes.py      # JSON endpoints: save, comment, close listing
│   ├── templates/         # Jinja2 templates
│   └── static/            # CSS + JS (no build step)
├── tests/                 # pytest suite
├── wsgi.py                # entrypoint Vercel/gunicorn/flask run load
├── requirements.txt        # production dependencies
├── requirements-dev.txt    # + pytest, flake8
└── .github/workflows/ci-cd.yml
```

## Running locally

```bash
git clone <your-repo-url>
cd entrypoint
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

cp .env.example .env               # then edit .env if needed
export FLASK_APP=wsgi.py           # Windows (PowerShell): $env:FLASK_APP="wsgi.py"
flask run
```

Visit `http://127.0.0.1:5000`. With no `DATABASE_URL` set, it uses a local
`entrypoint.db` SQLite file created automatically on first run.

### Using MySQL locally instead of SQLite

```bash
# in .env
DATABASE_URL=mysql+pymysql://<user>:<password>@127.0.0.1:3306/entrypoint
```

Create the `entrypoint` database first (`CREATE DATABASE entrypoint;`); the
app creates its own tables on startup.

## Running tests

```bash
pytest -v
flake8 app tests wsgi.py --max-line-length=110
```

Tests run against an isolated in-memory SQLite database.

## CI/CD pipeline

`.github/workflows/ci-cd.yml` runs on every push and pull request against
`main`:

1. **test job** — installs dependencies, runs `flake8`, then `pytest`.
2. **deploy job** — runs only after `test` passes, and only on a push to
   `main`. Installs the Vercel CLI and runs the standard
   `vercel pull` → `vercel build --prod` → `vercel deploy --prebuilt --prod`
   sequence, so the same artifact that was linted and tested is what gets
   deployed.

### One-time setup to make the deploy job work

1. Install the Vercel CLI locally and run `vercel link` inside this project
   once, logging into your Vercel account when prompted. This creates a
   local `.vercel/project.json` with your org and project IDs (already
   excluded from git via `.gitignore`).
2. Note `orgId` and `projectId` from that file.
3. In your Vercel account, create a personal token
   (Vercel dashboard → Settings → Tokens).
4. In your GitHub repo: **Settings → Secrets and variables → Actions**, add
   three repository secrets: `VERCEL_TOKEN`, `VERCEL_ORG_ID`,
   `VERCEL_PROJECT_ID`.
5. In the Vercel project's dashboard, add the environment variables it
   needs at runtime (**Settings → Environment Variables**): `SECRET_KEY`
   (any long random string) and `DATABASE_URL` (your production MySQL
   connection string, see below).
6. If the Vercel project also has its native GitHub integration connected,
   disconnect it (or leave the build command empty) so only this Action
   deploys — otherwise both would try to deploy the same push.

From that point on, every push to `main` that passes tests deploys
automatically.

## Deploying to Vercel (what the pipeline does for you)

Vercel's Python runtime auto-detects Flask from `requirements.txt` and looks
for an `app` object in `wsgi.py` (already set up here) — no `vercel.json`
needed.

Because Vercel Functions are stateless/ephemeral, the database must be an
always-on server reachable over the network — a local SQLite file won't
persist. Any hosted MySQL works; a few free-tier options: Aiven, Railway,
Clever Cloud, or PlanetScale. Set the connection string as `DATABASE_URL` in
the Vercel project's environment variables, in the same
`mysql+pymysql://user:password@host:3306/dbname` format used locally.

## API reference

All endpoints below require an authenticated session.

| Method | Path                          | Body                | Returns |
|--------|-------------------------------|----------------------|---------|
| POST   | `/api/jobs/<id>/save`          | –                    | `{saved, save_count}` |
| POST   | `/api/jobs/<id>/comments`       | `{"body": "..."}`   | `{id, body, name, comment_count}` |
| POST   | `/api/jobs/<id>/toggle`         | –                    | `{is_active}` (owner only) |

## Known limitations / next steps

- No CSRF token on the JSON API endpoints yet (fine for a same-origin
  fetch-based UI, but would need `Flask-WTF` CSRF tokens before treating
  this as a public API).
- Images and resumes are linked by URL rather than uploaded — file uploads
  would need object storage (e.g. S3-compatible) since Vercel Functions
  don't persist local disk writes.
- No rate limiting on posting/commenting yet.
- No moderation/reporting flow for spammy or fake listings.
- No email verification or password reset flow.
