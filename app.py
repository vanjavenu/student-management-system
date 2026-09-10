
from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

def create_database():
    connection = sqlite3.connect("students.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            email TEXT,
            phone TEXT,
            course TEXT
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


if __name__ == "__main__":
    app.run(debug=True)