import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Add or edit department labels here; they are used by the registration and admin forms.
DEPARTMENTS = [
    "Computer Science Engineering (CSE)",
    "Electronics and Communication Engineering (ECE)",
    "Mechanical Engineering (ME)",
    "Civil Engineering (CE)",
    "Electrical Engineering (EE)",
    "Other",
]
CSE_SPECIALIZATIONS = [
    "Cyber Security",
    "Artificial Intelligence (AI)",
    "Machine Learning (ML)",
    "Data Science (DS)",
]

COLLECT_MOBILE = os.getenv("COLLECT_MOBILE", "true").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}
COLLECT_GENDER = os.getenv("COLLECT_GENDER", "true").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}
COLLECT_COLLEGE_REG = os.getenv("COLLECT_COLLEGE_REG", "true").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}

SECRET_KEY = os.getenv("SECRET_KEY", "").strip()
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "").strip()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
if not SECRET_KEY or not ADMIN_PASSWORD:
    raise RuntimeError(
        "SECRET_KEY and ADMIN_PASSWORD are required. Copy .env.example to .env "
        "and fill in those values before starting the app."
    )
if not ADMIN_USERNAME:
    raise RuntimeError("ADMIN_USERNAME is required. Set it in your .env file.")

database_url = os.getenv("DATABASE_URL", "").strip()
if database_url.startswith("postgres://"):
    database_url = "postgresql://" + database_url[len("postgres://") :]
DATABASE_URL = database_url or (
    "sqlite:///" + str(Path(__file__).resolve().parent / "students.db")
)

FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}
