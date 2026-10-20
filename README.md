# JobSwipe

Responsive Django and PostgreSQL job discovery and recruitment application. Candidates discover jobs, save listings, and express interest. Employers manage a company workspace, review candidates, and chat after accepting an interest.

## Features

- Email/password candidate accounts, profiles, preferences, and optional resumes.
- Preference-ranked job feed, search filters, job details, bookmarks, swipe history, and activity summary.
- Employer registration and a dedicated company login.
- Company verification controlled through Django Admin.
- Company job posting after verification.
- Candidate interest review with pending, accepted, and rejected states.
- Private persistent conversation and messaging after acceptance only.
- Permission checks so candidates and active members of the relevant company can access the conversation.
- Protected resume download endpoint for authorized company members reviewing a candidate who expressed interest.
- PostgreSQL configuration through environment variables.

## Setup

1. Create and activate a Python virtual environment.
2. Install dependencies: `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and set a strong secret key and your PostgreSQL settings.
4. Create the PostgreSQL database and user configured in `.env`.
5. Back up any existing database before applying migrations.
6. Run:

```bash
python manage.py check
python manage.py showmigrations accounts jobs
python manage.py migrate --plan
python manage.py migrate
python manage.py createsuperuser
python manage.py test accounts jobs
python manage.py runserver
```

Open `/accounts/register/` for candidates, `/accounts/employer/register/` to register a company, `/accounts/login/` for candidate login, `/accounts/employer/login/` for company login, or `/admin/` for administration.

Example PostgreSQL setup (choose a strong password):

```sql
CREATE USER job_swipe_user WITH PASSWORD 'replace-with-a-strong-password';
CREATE DATABASE job_swipe OWNER job_swipe_user;
```

## Company approval and recruiting flow

Company registration creates a company with verification disabled. An administrator should check the company identity and website, then mark it verified in Django Admin. Only verified companies can publish jobs. Administrators can add company employee memberships in the Company Memberships section. Set each employee account role to Employer and ensure its membership is active; only active members can review interest and access the relevant company's conversations.

When a candidate clicks Interested, the existing swipe record is given a pending review status. A company member can accept or reject the interest. Acceptance creates a conversation; rejection does not. Existing historical swipe records migrate to `not_applicable` so old interests are not automatically presented as new pending requests.

Chat uses regular Django requests and PostgreSQL persistence; messages are saved when sent. It does not require a paid WebSocket service.

## Safe schema updates

The new migrations add the account role, company memberships, interest review fields, conversations, and messages. They do not delete existing tables. Keep your `.env`, database, and migration history. Before migrating an existing installation, back up the database and inspect `python manage.py migrate --plan`. Do not delete migrations, reset the database, or use `--fake` to bypass a schema problem. If the migration state and actual database schema disagree, investigate that mismatch first.

## Security and production notes

Keep `.env` private and never commit credentials. Resume validation checks file extension and size, not file contents. Resume downloads are served through an authenticated view, but production media storage and web-server configuration must also prevent direct public access to uploaded files. Consider file-content inspection and malware scanning. Before public deployment, configure `DEBUG=False`, a strong production secret, allowed hosts, HTTPS, secure cookies, static-file serving, database backups, logging, and monitoring. Run `python manage.py check --deploy` with production settings.

External job API imports are not configured in this version; integrate only a provider whose API and listing-display terms authorize your intended use.

## Logout behavior

- Candidate logout redirects to `/accounts/login/`.
- Employer/company logout redirects to `/accounts/employer/login/`.
- Logout is a POST-only action protected by Django's CSRF middleware.

