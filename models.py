from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Student(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    roll_number: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False, index=True
    )
    college_reg_no: Mapped[str | None] = mapped_column(String(50), nullable=True)
    department: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    specialization: Mapped[str | None] = mapped_column(String(60), nullable=True)
    year: Mapped[int] = mapped_column(nullable=False, index=True)
    semester: Mapped[int] = mapped_column(nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(254), nullable=False)
    mobile: Mapped[str | None] = mapped_column(String(20), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(30), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
