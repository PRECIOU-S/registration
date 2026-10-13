import csv
import hmac
import io
import re
from datetime import datetime, timezone
from functools import wraps

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from sqlalchemy import func, inspect, select
from sqlalchemy.exc import IntegrityError
from flask_wtf.csrf import CSRFProtect

import config
from models import Student, db

csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=config.SECRET_KEY,
        SQLALCHEMY_DATABASE_URI=config.DATABASE_URL,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=not config.FLASK_DEBUG,
    )
    app.config["DEPARTMENTS"] = config.DEPARTMENTS
    app.config["COLLECT_MOBILE"] = config.COLLECT_MOBILE
    app.config["COLLECT_GENDER"] = config.COLLECT_GENDER
    app.config["COLLECT_COLLEGE_REG"] = config.COLLECT_COLLEGE_REG

    db.init_app(app)
    csrf.init_app(app)

    @app.after_request
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "same-origin"
        return response

    def render_registration(errors=None):
        return render_template(
            "register.html",
            errors=errors or {},
            departments=config.DEPARTMENTS,
            cse_specializations=config.CSE_SPECIALIZATIONS,
            cse_department="Computer Science Engineering (CSE)",
            collect_mobile=config.COLLECT_MOBILE,
            collect_gender=config.COLLECT_GENDER,
            collect_college_reg=config.COLLECT_COLLEGE_REG,
            genders=("Male", "Female", "Other", "Prefer not to say"),
        )

    @app.route("/", methods=["GET", "POST"])
    def register():
        if request.method == "GET":
            return render_registration()

        form = request.form
        errors = {}

        full_name = form.get("full_name", "").strip()
        roll_number = form.get("roll_number", "").strip().upper()
        college_reg_no = (
            form.get("college_reg_no", "").strip()
            if config.COLLECT_COLLEGE_REG
            else ""
        )
        department = form.get("department", "").strip()
        specialization = (
            form.get("specialization", "").strip()
            if department == "Computer Science Engineering (CSE)"
            else ""
        )
        year_text = form.get("year", "").strip()
        semester_text = form.get("semester", "").strip()
        email = form.get("email", "").strip()
        mobile = form.get("mobile", "").strip() if config.COLLECT_MOBILE else ""
        gender = form.get("gender", "").strip() if config.COLLECT_GENDER else ""

        if not full_name:
            errors["full_name"] = "Please enter your full name."
        elif len(full_name) > 100:
            errors["full_name"] = "Full name must be 100 characters or fewer."

        if not roll_number:
            errors["roll_number"] = "Please enter your university roll number."
        elif len(roll_number) > 30:
            errors["roll_number"] = "Roll number must be 30 characters or fewer."
        elif not re.fullmatch(r"[A-Z0-9]+", roll_number, flags=re.ASCII):
            errors["roll_number"] = "Use letters and digits only for the roll number."
        elif db.session.scalar(
            select(Student.id).where(Student.roll_number == roll_number)
        ):
            errors["roll_number"] = "This roll number is already registered."

        if len(college_reg_no) > 50:
            errors["college_reg_no"] = (
                "College registration number must be 50 characters or fewer."
            )

        if department not in config.DEPARTMENTS:
            errors["department"] = "Please choose a department from the list."

        if department == "Computer Science Engineering (CSE)":
            if specialization not in config.CSE_SPECIALIZATIONS:
                errors["specialization"] = "Please choose your CSE specialization."
        else:
            specialization = ""

        year = None
        if year_text not in {"1", "2", "3", "4"}:
            errors["year"] = "Please choose a year from 1 to 4."
        else:
            year = int(year_text)

        semester = None
        if semester_text not in {str(value) for value in range(1, 9)}:
            errors["semester"] = "Please choose a semester from 1 to 8."
        else:
            semester = int(semester_text)

        if year is not None and semester is not None:
            expected_semesters = {2 * year - 1, 2 * year}
            if semester not in expected_semesters:
                errors["semester"] = (
                    f"Year {year} students must select semester "
                    f"{2 * year - 1} or {2 * year}."
                )

        if (
            not email
            or len(email) > 254
            or not re.fullmatch(
                r"[^@\s]+@[^@\s]+\.[^@\s]+", email, flags=re.ASCII
            )
        ):
            errors["email"] = "Enter a valid email address."

        if mobile and not re.fullmatch(r"[0-9]{10}", mobile, flags=re.ASCII):
            errors["mobile"] = "Mobile number must contain exactly 10 digits."
        elif len(mobile) > 20:
            errors["mobile"] = "Mobile number must be 20 characters or fewer."

        allowed_genders = {"", "Male", "Female", "Other", "Prefer not to say"}
        if gender not in allowed_genders:
            errors["gender"] = "Please choose a gender from the list."

        if errors:
            return render_registration(errors), 400

        student = Student(
            full_name=full_name,
            roll_number=roll_number,
            college_reg_no=college_reg_no or None,
            department=department,
            specialization=specialization or None,
            year=year,
            semester=semester,
            email=email,
            mobile=mobile or None,
            gender=gender or None,
        )
        db.session.add(student)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return render_registration(
                {"roll_number": "This roll number is already registered."}
            ), 400

        session["registration_confirmation"] = {
            "full_name": student.full_name,
            "roll_number": student.roll_number,
        }
        return redirect(url_for("success"))

    @app.get("/success")
    def success():
        confirmation = session.pop("registration_confirmation", None)
        if not confirmation:
            return redirect(url_for("register"))
        return render_template("success.html", confirmation=confirmation)

    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        if session.get("admin_logged_in"):
            return redirect(url_for("admin_dashboard"))

        error = None
        if request.method == "POST":
            username = request.form.get("username", "")
            password = request.form.get("password", "")
            valid_username = hmac.compare_digest(username, config.ADMIN_USERNAME)
            valid_password = hmac.compare_digest(password, config.ADMIN_PASSWORD)
            if valid_username and valid_password:
                session.clear()
                session["admin_logged_in"] = True
                return redirect(url_for("admin_dashboard"))
            error = "Invalid username or password"
        return render_template("admin_login.html", error=error)

    def admin_required(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not session.get("admin_logged_in"):
                return redirect(url_for("admin_login"))
            return view(*args, **kwargs)

        return wrapped

    @app.get("/admin/logout")
    @admin_required
    def admin_logout():
        session.clear()
        flash("You have been logged out.")
        return redirect(url_for("admin_login"))

    def filtered_student_query():
        query = select(Student)
        filters = {}

        department = request.args.get("department", "")
        if department in config.DEPARTMENTS:
            query = query.where(Student.department == department)
            filters["department"] = department

        year_text = request.args.get("year", "")
        if year_text in {"1", "2", "3", "4"}:
            query = query.where(Student.year == int(year_text))
            filters["year"] = year_text

        semester_text = request.args.get("semester", "")
        if semester_text in {str(value) for value in range(1, 9)}:
            query = query.where(Student.semester == int(semester_text))
            filters["semester"] = semester_text

        search = request.args.get("search", "").strip()[:100]
        if search:
            pattern = f"%{search}%"
            query = query.where(
                func.lower(Student.full_name).like(func.lower(pattern))
                | func.lower(Student.roll_number).like(func.lower(pattern))
            )
            filters["search"] = search

        sort = request.args.get("sort", "newest")
        orderings = {
            "name_asc": (Student.full_name.asc(), Student.id.asc()),
            "name_desc": (Student.full_name.desc(), Student.id.desc()),
            "roll_number": (Student.roll_number.asc(),),
            "newest": (Student.created_at.desc(), Student.id.desc()),
        }
        if sort not in orderings:
            sort = "newest"
        query = query.order_by(*orderings[sort])
        filters["sort"] = sort
        return query, filters

    def department_counts():
        count_rows = db.session.execute(
            select(Student.department, func.count(Student.id)).group_by(
                Student.department
            )
        ).all()
        counts = {department: 0 for department in config.DEPARTMENTS}
        counts.update({department: count for department, count in count_rows})
        return counts

    @app.get("/admin")
    @admin_required
    def admin_dashboard():
        query, filters = filtered_student_query()
        total = db.session.scalar(select(func.count(Student.id))) or 0
        filtered_total = db.session.scalar(
            select(func.count()).select_from(query.order_by(None).subquery())
        )
        page = request.args.get("page", "1")
        requested_page = (
            int(page) if page.isascii() and page.isdigit() and len(page) <= 9 else 1
        )
        page_number = max(requested_page, 1)
        per_page = 25
        page_count = max((filtered_total + per_page - 1) // per_page, 1)
        page_number = min(page_number, page_count)
        students = db.session.scalars(
            query.offset((page_number - 1) * per_page).limit(per_page)
        ).all()

        return render_template(
            "admin_dashboard.html",
            students=students,
            total=total,
            filtered_total=filtered_total,
            counts=department_counts(),
            departments=config.DEPARTMENTS,
            filters=filters,
            selected_department=filters.get("department"),
            page=page_number,
            page_count=page_count,
            per_page=per_page,
            export_url=url_for("admin_export", **filters),
            previous_url=(
                url_for("admin_dashboard", **filters, page=page_number - 1)
                if page_number > 1
                else None
            ),
            next_url=(
                url_for("admin_dashboard", **filters, page=page_number + 1)
                if page_number < page_count
                else None
            ),
        )

    @app.get("/admin/student/<int:student_id>")
    @admin_required
    def admin_student(student_id):
        student = db.session.get(Student, student_id)
        if student is None:
            abort(404)
        return render_template("admin_student.html", student=student)

    def csv_safe(value):
        text = "" if value is None else str(value)
        if text.startswith(("=", "+", "-", "@")):
            return "'" + text
        return text

    @app.get("/admin/export.csv")
    @admin_required
    def admin_export():
        query, _ = filtered_student_query()
        students = db.session.scalars(query).all()
        output = io.StringIO(newline="")
        writer = csv.writer(output)
        writer.writerow(
            [
                "Name",
                "Roll Number",
                "College Reg No",
                "Department",
                "Year",
                "Semester",
                "Specialization",
                "Email",
                "Mobile",
                "Gender",
                "Registered On",
            ]
        )
        for student in students:
            registered_at = student.created_at
            if registered_at.tzinfo is None:
                registered_at = registered_at.replace(tzinfo=timezone.utc)
            else:
                registered_at = registered_at.astimezone(timezone.utc)
            writer.writerow(
                csv_safe(value)
                for value in (
                    student.full_name,
                    student.roll_number,
                    student.college_reg_no,
                    student.department,
                    student.year,
                    student.semester,
                    student.specialization,
                    student.email,
                    student.mobile,
                    student.gender,
                    registered_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
                )
            )
        data = io.BytesIO(output.getvalue().encode("utf-8-sig"))
        filename_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        department = request.args.get("department", "")
        department_match = (
            re.search(r"\(([A-Z]+)\)$", department)
            if department in config.DEPARTMENTS
            else None
        )
        department_code = (
            department_match.group(1)
            if department_match
            else "OTHER"
            if department == "Other"
            else "ALL"
        )
        return send_file(
            data,
            mimetype="text/csv; charset=utf-8",
            as_attachment=True,
            download_name=f"students_{department_code}_{filename_date}.csv",
        )

    with app.app_context():
        db.create_all()
        student_columns = {
            column["name"] for column in inspect(db.engine).get_columns(Student.__tablename__)
        }
        if "specialization" not in student_columns:
            table_name = db.engine.dialect.identifier_preparer.quote(
                Student.__tablename__
            )
            with db.engine.begin() as connection:
                connection.exec_driver_sql(
                    f"ALTER TABLE {table_name} ADD COLUMN specialization VARCHAR(60)"
                )

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=config.FLASK_DEBUG)
