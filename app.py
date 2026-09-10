
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
