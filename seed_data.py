from app import app, db
from models import Student

# Delete these clearly fake sample records before real students register.
SAMPLE_STUDENTS = [
    ("Nikhil Sample", "CSETEST001", "CSE-TEST-001", "Computer Science Engineering (CSE)", 1, 1, "nikhil.test@example.com", "0000000001", "Male"),
    ("Aarav Demo", "CSETEST002", "CSE-TEST-002", "Computer Science Engineering (CSE)", 2, 3, "aarav.demo@example.com", "0000000002", "Other"),
    ("Mira Example", "CSETEST003", "CSE-TEST-003", "Computer Science Engineering (CSE)", 3, 5, "mira.example@example.com", "0000000003", "Female"),
    ("Bhavesh Sample", "ECETEST001", "ECE-TEST-001", "Electronics and Communication Engineering (ECE)", 1, 2, "bhavesh.test@example.com", "0000000004", "Male"),
    ("Diya Demo", "ECETEST002", "ECE-TEST-002", "Electronics and Communication Engineering (ECE)", 4, 7, "diya.demo@example.com", "0000000005", "Prefer not to say"),
    ("Kabir Example", "METEST001", "ME-TEST-001", "Mechanical Engineering (ME)", 2, 4, "kabir.example@example.com", "0000000006", "Male"),
    ("Anaya Sample", "METEST002", "ME-TEST-002", "Mechanical Engineering (ME)", 3, 6, "anaya.test@example.com", "0000000007", "Female"),
    ("Rohan Demo", "CETEST001", "CE-TEST-001", "Civil Engineering (CE)", 1, 1, "rohan.demo@example.com", "0000000008", "Other"),
    ("Isha Example", "CETEST002", "CE-TEST-002", "Civil Engineering (CE)", 4, 8, "isha.example@example.com", "0000000009", "Female"),
    ("Dev Sample", "EETEST001", "EE-TEST-001", "Electrical Engineering (EE)", 2, 3, "dev.test@example.com", "0000000010", "Prefer not to say"),
]

CSE_SPECIALIZATIONS = {
    "CSETEST001": "Cyber Security",
    "CSETEST002": "Artificial Intelligence (AI)",
    "CSETEST003": "Data Science (DS)",
}

with app.app_context():
    existing_roll_numbers = set(
        db.session.scalars(db.select(Student.roll_number)).all()
    )
    added = 0
    for full_name, roll_number, college_reg_no, department, year, semester, email, mobile, gender in SAMPLE_STUDENTS:
        if roll_number in existing_roll_numbers:
            continue
        db.session.add(
            Student(
                full_name=full_name,
                roll_number=roll_number,
                college_reg_no=college_reg_no,
                department=department,
                specialization=CSE_SPECIALIZATIONS.get(roll_number),
                year=year,
                semester=semester,
                email=email,
                mobile=mobile,
                gender=gender,
            )
        )
        existing_roll_numbers.add(roll_number)
        added += 1
    db.session.commit()
    print(f"Seed complete. Added {added} fake sample students.")
