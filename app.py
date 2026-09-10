
python
from flask import Flask, render_template, request, redirect, url_for, Response
import sqlite3
import os
import csv
import io

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "students.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            course TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def index():
    query = request.args.get("q", "").strip()
    conn = get_db()

    if query:
        like = f"%{query}%"
        students = conn.execute(
            """SELECT * FROM students
               WHERE name LIKE ? OR email LIKE ? OR course LIKE ?
               ORDER BY id""",
            (like, like, like),
        ).fetchall()
    else:
        students = conn.execute("SELECT * FROM students ORDER BY id").fetchall()

    conn.close()
    return render_template("index.html", students=students, query=query)


@app.route("/export")
def export_csv():
    query = request.args.get("q", "").strip()
    conn = get_db()

    if query:
        like = f"%{query}%"
        students = conn.execute(
            """SELECT * FROM students
               WHERE name LIKE ? OR email LIKE ? OR course LIKE ?
               ORDER BY id""",
            (like, like, like),
        ).fetchall()
    else:
        students = conn.execute("SELECT * FROM students ORDER BY id").fetchall()

    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Name", "Age", "Email", "Phone", "Course"])
    for s in students:
        writer.writerow([s["id"], s["name"], s["age"], s["email"], s["phone"], s["course"]])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=students.csv"},
    )


@app.route("/add", methods=["POST"])
def add_student():
    name = request.form["name"].strip()
    age = request.form["age"].strip()
    email = request.form["email"].strip()
    phone = request.form["phone"].strip()
    course = request.form["course"].strip()

    if name and age and email and phone and course:
        conn = get_db()
        conn.execute(
            "INSERT INTO students (name, age, email, phone, course) VALUES (?, ?, ?, ?, ?)",
            (name, age, email, phone, course),
        )
        conn.commit()
        conn.close()

    return redirect(url_for("index"))


@app.route("/edit/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    conn = get_db()

    if request.method == "POST":
        name = request.form["name"].strip()
        age = request.form["age"].strip()
        email = request.form["email"].strip()
        phone = request.form["phone"].strip()
        course = request.form["course"].strip()

        conn.execute(
            "UPDATE students SET name=?, age=?, email=?, phone=?, course=? WHERE id=?",
            (name, age, email, phone, course, student_id),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    student = conn.execute(
        "SELECT * FROM students WHERE id=?", (student_id,)
    ).fetchone()
    conn.close()

    if student is None:
        return redirect(url_for("index"))

    return render_template("edit.html", student=student)


@app.route("/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    conn = get_db()
    conn.execute("DELETE FROM students WHERE id=?", (student_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


init_db()

if __name__ == "__main__":
    
    app.run(debug=True)




