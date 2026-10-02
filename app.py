from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)

# Secret key for login session
app.secret_key = "student_attendance_secret_key"


# =========================
# DATABASE CONNECTION
# =========================

def get_db_connection():
    conn = sqlite3.connect("attendance.db")
    conn.row_factory = sqlite3.Row
    return conn


# =========================
# INITIALIZE DATABASE
# =========================

def init_db():

    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            present INTEGER NOT NULL,
            total INTEGER NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        # Admin login details
        if username == "admin" and password == "admin123":

            session["admin"] = True

            return redirect("/")

        else:

            return render_template(
                "login.html",
                error="Invalid username or password"
            )

    return render_template("login.html")


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.pop("admin", None)

    return redirect("/login")


# =========================
# DASHBOARD
# =========================

@app.route("/")
def home():

    # Login check
    if "admin" not in session:
        return redirect("/login")

    search = request.args.get("search", "")
    filter_type = request.args.get("filter", "all")

    conn = get_db_connection()

    students = conn.execute(
        "SELECT * FROM students WHERE name LIKE ?",
        ("%" + search + "%",)
    ).fetchall()

    conn.close()

    # Attendance filter
    if filter_type == "above":

        students = [
            student for student in students
            if student["total"] > 0
            and (student["present"] / student["total"]) * 100 >= 75
        ]

    elif filter_type == "below":

        students = [
            student for student in students
            if student["total"] > 0
            and (student["present"] / student["total"]) * 100 < 75
        ]

    total_students = len(students)

    # Average attendance
    if total_students > 0:

        average_attendance = sum(
            (student["present"] / student["total"]) * 100
            for student in students
            if student["total"] > 0
        ) / total_students

    else:

        average_attendance = 0

    # Students with attendance >= 75%
    present_students = sum(
        1
        for student in students
        if student["total"] > 0
        and (student["present"] / student["total"]) * 100 >= 75
    )

    return render_template(
        "index.html",
        students=students,
        total_students=total_students,
        present_students=present_students,
        average_attendance=average_attendance,
        search=search,
        filter_type=filter_type
    )


# =========================
# ADD STUDENT
# =========================

@app.route("/add", methods=["POST"])
def add_student():

    if "admin" not in session:
        return redirect("/login")

    name = request.form["name"]
    present = int(request.form["present"])
    total = int(request.form["total"])

    if present > total:
        return "Present days cannot be greater than total days."

    if total <= 0:
        return "Total days must be greater than 0."

    conn = get_db_connection()

    conn.execute(
        """
        INSERT INTO students (name, present, total)
        VALUES (?, ?, ?)
        """,
        (name, present, total)
    )

    conn.commit()
    conn.close()

    return redirect("/")


# =========================
# EDIT STUDENT
# =========================

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_student(id):

    if "admin" not in session:
        return redirect("/login")

    conn = get_db_connection()

    if request.method == "POST":

        name = request.form["name"]
        present = int(request.form["present"])
        total = int(request.form["total"])

        if present > total:
            conn.close()
            return "Present days cannot be greater than total days."

        if total <= 0:
            conn.close()
            return "Total days must be greater than 0."

        conn.execute(
            """
            UPDATE students
            SET name = ?, present = ?, total = ?
            WHERE id = ?
            """,
            (name, present, total, id)
        )

        conn.commit()
        conn.close()

        return redirect("/")

    student = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (id,)
    ).fetchone()

    conn.close()

    return render_template(
        "edit.html",
        student=student
    )


# =========================
# DELETE STUDENT
# =========================

@app.route("/delete/<int:id>")
def delete_student(id):

    if "admin" not in session:
        return redirect("/login")

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM students WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


# =========================
# INITIALIZE DATABASE
# =========================

init_db()


# =========================
# RUN APP
# =========================

if __name__ == "__main__":
    app.run(debug=True)