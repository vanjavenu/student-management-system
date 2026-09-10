
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)


def create_database():
    connection = sqlite3.connect("students.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            course TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


@app.route("/")
def home():
    create_database()

    connection = sqlite3.connect("students.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name, age, email, phone, course
        FROM students
    """)

    students = cursor.fetchall()

    connection.close()

    return render_template("index.html", students=students)


@app.route("/add", methods=["POST"])
def add_student():

    name = request.form["name"]
    age = request.form["age"]
    email = request.form["email"]
    phone = request.form["phone"]
    course = request.form["course"]

    connection = sqlite3.connect("students.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO students
        (name, age, email, phone, course)
        VALUES (?, ?, ?, ?, ?)
    """, (name, age, email, phone, course))

    connection.commit()
    connection.close()

    return redirect(url_for("home"))


@app.route("/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):

    connection = sqlite3.connect("students.db")
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM students WHERE id = ?",
        (student_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("home"))


@app.route("/edit/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):

    connection = sqlite3.connect("students.db")
    cursor = connection.cursor()

    if request.method == "POST":

        name = request.form["name"]
        age = request.form["age"]
        email = request.form["email"]
        phone = request.form["phone"]
        course = request.form["course"]

        cursor.execute("""
            UPDATE students
            SET name = ?,
                age = ?,
                email = ?,
                phone = ?,
                course = ?
            WHERE id = ?
        """, (name, age, email, phone, course, student_id))

        connection.commit()
        connection.close()

        return redirect(url_for("home"))

    cursor.execute("""
        SELECT id, name, age, email, phone, course
        FROM students
        WHERE id = ?
    """, (student_id,))

    student = cursor.fetchone()

    connection.close()

    return render_template("edit.html", student=student)


if __name__ == "__main__":
    app.run(debug=True)