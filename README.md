# Student Registration and Department-Wise Management System

This is a small Flask website for collecting student registrations in one database. Students can submit a registration but cannot see any student list. A teacher signs in to a private dashboard to search, filter, view, and export records.

## Project files

```text
student-registration/
  app.py                    Flask routes, validation, admin pages, and CSV export
  config.py                 Environment settings and the editable department list
  models.py                 SQLAlchemy Student database model, including CSE specialization
  seed_data.py              Adds clearly fake demo records for local testing
  requirements.txt          Python packages with compatible pinned versions
  Procfile                  Gunicorn start command used by hosting services
  render.yaml               Render web service and PostgreSQL setup
  .env.example              Safe template for local environment settings
  .gitignore                Keeps secrets, database, and virtual environment out of Git
  README.md                 Setup, test, deployment, and presentation guide
  templates/                Jinja HTML pages
  static/style.css          Responsive page styling
```

The app creates the database tables the first time it starts. Local use defaults to `students.db` (SQLite). On Render, the `DATABASE_URL` setting selects PostgreSQL.
Use the **Dark** button in the header to switch between light and dark themes. Your choice is remembered in the current browser.

## Run locally on Windows 11

Open a PowerShell terminal in the project folder. If your virtual environment is not already active, activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks the activation script, allow scripts just for this terminal window, then activate the environment:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

Make your private local settings file and install the dependencies:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and set a long, random `SECRET_KEY`, plus an `ADMIN_USERNAME` and strong `ADMIN_PASSWORD`. Leave `DATABASE_URL` empty for the local SQLite database.

```powershell
pip install -r requirements.txt
python seed_data.py
python app.py
```

Open the registration page at <http://127.0.0.1:5000>. Open the teacher login at <http://127.0.0.1:5000/admin/login>. Sign in with the username and password you put in `.env`. The demo data is fake; delete it before real students register.

To start clean for real registrations, stop the app with `Ctrl+C`, remove the local `students.db` file, and start the app again. This permanently removes the local database records. Do not do this if you need to keep those records.

## Test the features

1. Submit one CSE student (choose a specialization) and one ECE student using different roll numbers.
2. Submit the same roll number again. The form should say **This roll number is already registered.** and should not add another student.
3. Open `/admin/login` and sign in with the credentials from `.env`.
4. Try a department card and department dropdown; filter by year and semester.
5. Search by a name and by a roll number. Try each sort option.
6. Open a student's record using **View**. Mobile details appear only on this page, not in the table.
7. Click **Export CSV** and open the downloaded CSV. The export includes all matching filtered/sorted rows, not just the current page.
8. Click **Log out**, then visit `/admin`. It should send you to the login page.
9. Open `/success` directly in a fresh browser session. It should return to the registration form rather than show a student's record.

## Push to GitHub

Create an empty repository on GitHub, then run these commands in the project directory (replace the URL with your own repository URL):

```powershell
git init
git add .
git commit -m "Build student registration system"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

**Never commit `.env` or the database file.** They are ignored by `.gitignore`. Check your staged files with `git status` before pushing.

## Deploy on Render

1. Create a PostgreSQL database in Render, or use the database described in `render.yaml` when creating the Blueprint.
2. Create a Render Web Service from your GitHub repository. Use Python as the runtime, `pip install -r requirements.txt` as the build command, and `gunicorn app:app` as the start command. The supplied `render.yaml` already describes these settings and connects the database.
3. In the Render service environment settings, set `SECRET_KEY` to a long unique random value, `ADMIN_USERNAME` to the teacher's chosen username, and `ADMIN_PASSWORD` to a strong unique password. The Blueprint marks the admin values as private inputs and generates a secret key.
4. Ensure `DATABASE_URL` is connected to the Render PostgreSQL database and `FLASK_DEBUG` is `false`. The app automatically changes Render's older `postgres://` URL prefix and explicitly uses the installed `psycopg2` driver.
5. Deploy, then open the service's public URL to reach the registration form. Add any initial sample data only in a suitable local/test environment; `seed_data.py` connects to whichever database `DATABASE_URL` selects.

Render free-tier availability, pricing, sleep behavior, and database expiry rules can change. Check Render's current pricing and PostgreSQL documentation before relying on a free service or storing important data.

## Share the links safely

Give students the public service URL for registration. Give Madam the same site's `/admin/login` URL and her credentials **only over a private channel**. Never post the admin link together with credentials in a public group. Do not share the `.env` file.

## Present the project to a teacher

### Two-minute demo script

1. “This is the public registration form. It validates student details, checks that the roll number is unique, and stores valid submissions in one database.”
2. Submit a sample student and point out that the confirmation contains only the name and roll number.
3. “Students cannot browse other records. The teacher uses a protected login to open this dashboard.”
4. Sign in, show department counts, search, filters, sorting, a student's full record, and the CSV download.
5. “The app uses CSRF protection, secure session-cookie settings, escaped templates, and a private admin session. Local development uses SQLite; deployment uses PostgreSQL.”

### Features and security points to mention

- Required fields, the CSE-only specialization, and department/year/semester combinations are checked on the server.
- Roll numbers are trimmed, saved uppercase, and unique; duplicate submissions are handled safely.
- Only the logged-in admin can view student records and export CSV.
- A student's success page shows only that student's own confirmation.
- Admin forms use CSRF tokens; same-origin referrers support secure form checks while preventing referrer details from being sent to other sites.
- The CSV export includes a UTF-8 BOM and neutralizes spreadsheet formula prefixes.
- Never put real secrets in source code or commit `.env` or a database containing student details.

## Troubleshooting

- **`python` is not recognized:** install Python 3 from the official Python website and select the option to add it to PATH, then reopen VS Code. Try `py` instead of `python` if the Python launcher is installed.
- **PowerShell script execution error:** use the process-only `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` command above. It applies only to the current terminal.
- **Port already in use:** stop the other local Flask process with `Ctrl+C`, or start this app on another port by changing `app.run(debug=config.FLASK_DEBUG)` at the bottom of `app.py` to include `port=5001`, then visit `http://127.0.0.1:5001`.
- **File saved as `app,py`:** in VS Code's Explorer, rename it to exactly `app.py` (a period before `py`, not a comma).
- **White dot on a VS Code tab:** that means the file has unsaved changes. Press `Ctrl+S` before running it.
- **Missing secret configuration:** copy `.env.example` to `.env`, fill in `SECRET_KEY`, `ADMIN_USERNAME`, and `ADMIN_PASSWORD`, and restart the app.
