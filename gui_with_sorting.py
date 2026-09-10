import tkinter as tk
import sqlite3
from tkinter import messagebox
from tkinter import ttk
from openpyxl import Workbook


# ================= DATABASE =================

def connect_db():
    return sqlite3.connect("students.db")


# ================= MAIN WINDOW =================

window = tk.Tk()
window.title("Student Management System")
window.geometry("800x700")
window.resizable(False, False)

bg_color = "#f4f6f8"
button_color = "#2c3e50"
text_color = "#2c3e50"

window.configure(bg=bg_color)


# ================= FUNCTIONS =================

def get_dashboard_data():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT course) FROM students")
    total_courses = cursor.fetchone()[0]

    connection.close()

    return total_students, total_courses


def update_dashboard():
    total_students, total_courses = get_dashboard_data()

    total_students_label.config(text=str(total_students))
    total_courses_label.config(text=str(total_courses))



# ================= EXPORT TO EXCEL =================

def export_to_excel():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, name, age, email, phone, course FROM students"
    )

    students = cursor.fetchall()
    connection.close()

    if not students:
        messagebox.showwarning(
            "No Data",
            "There are no students to export."
        )
        return

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Students"

    headers = ["ID", "Name", "Age", "Email", "Phone", "Course"]
    worksheet.append(headers)

    for student in students:
        worksheet.append(student)

    # Make columns easier to read
    column_widths = {
        "A": 10,
        "B": 20,
        "C": 10,
        "D": 30,
        "E": 18,
        "F": 20
    }

    for column, width in column_widths.items():
        worksheet.column_dimensions[column].width = width

    file_name = "students.xlsx"
    workbook.save(file_name)

    messagebox.showinfo(
        "Export Successful",
        f"Student data exported successfully to:\\n{file_name}"
    )


# ================= ADD STUDENT =================

def add_student():
    name = name_entry.get().strip()
    age = age_entry.get().strip()
    email = email_entry.get().strip()
    phone = phone_entry.get().strip()
    course = course_entry.get().strip()

    if name == "" or age == "" or email == "" or phone == "" or course == "":
        messagebox.showwarning("Warning", "Please fill all fields.")
        return

    if not age.isdigit():
        messagebox.showwarning("Warning", "Age must contain only numbers.")
        return

    if not phone.isdigit():
        messagebox.showwarning("Warning", "Phone must contain only numbers.")
        return

    if "@" not in email:
        messagebox.showwarning("Warning", "Please enter a valid email.")
        return

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO students (name, age, email, phone, course)
        VALUES (?, ?, ?, ?, ?)
        """,
        (name, age, email, phone, course)
    )

    connection.commit()
    connection.close()

    messagebox.showinfo("Success", "Student added successfully.")

    clear_fields()
    update_dashboard()
    load_students()
    load_courses()


# ================= CLEAR FIELDS =================

def clear_fields():
    name_entry.delete(0, tk.END)
    age_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)
    phone_entry.delete(0, tk.END)
    course_entry.delete(0, tk.END)


# ================= LOAD STUDENTS =================

def load_students():
    for item in student_table.get_children():
        student_table.delete(item)

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, name, age, email, phone, course FROM students"
    )

    students = cursor.fetchall()

    connection.close()

    for student in students:
        student_table.insert("", tk.END, values=student)


# ================= SEARCH BY NAME =================

def search_by_name():
    search_text = search_name_entry.get().strip()

    for item in student_table.get_children():
        student_table.delete(item)

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, name, age, email, phone, course
        FROM students
        WHERE name LIKE ?
        """,
        ("%" + search_text + "%",)
    )

    students = cursor.fetchall()

    connection.close()

    for student in students:
        student_table.insert("", tk.END, values=student)


# ================= FILTER BY COURSE =================

def filter_by_course(event=None):
    selected_course = course_filter_combo.get()

    for item in student_table.get_children():
        student_table.delete(item)

    connection = connect_db()
    cursor = connection.cursor()

    if selected_course == "All Courses":
        cursor.execute(
            """
            SELECT id, name, age, email, phone, course
            FROM students
            """
        )
    else:
        cursor.execute(
            """
            SELECT id, name, age, email, phone, course
            FROM students
            WHERE course = ?
            """,
            (selected_course,)
        )

    students = cursor.fetchall()

    connection.close()

    for student in students:
        student_table.insert("", tk.END, values=student)


# ================= LOAD COURSES =================

def load_courses():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT DISTINCT course
        FROM students
        WHERE course IS NOT NULL
        AND course != ''
        ORDER BY course
        """
    )

    courses = [row[0] for row in cursor.fetchall()]

    connection.close()

    course_filter_combo["values"] = ["All Courses"] + courses

    course_filter_combo.set("All Courses")


# ================= REFRESH =================

def refresh_students():
    search_name_entry.delete(0, tk.END)

    course_filter_combo.set("All Courses")

    load_students()
    load_courses()
    update_dashboard()


# ================= SEARCH STUDENT BY ID =================

def search_student():
    student_id = search_id_entry.get().strip()

    if student_id == "":
        messagebox.showwarning("Warning", "Please enter Student ID.")
        return

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, name, age, email, phone, course
        FROM students
        WHERE id = ?
        """,
        (student_id,)
    )

    student = cursor.fetchone()

    connection.close()

    if student:
        result_label.config(
            text=f"""
ID: {student[0]}
Name: {student[1]}
Age: {student[2]}
Email: {student[3]}
Phone: {student[4]}
Course: {student[5]}
"""
        )
    else:
        result_label.config(text="Student not found.")


# ================= UPDATE STUDENT =================

def update_student():
    student_id = update_id_entry.get().strip()

    if student_id == "":
        messagebox.showwarning("Warning", "Please enter Student ID.")
        return

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT name, age, email, phone, course
        FROM students
        WHERE id = ?
        """,
        (student_id,)
    )

    student = cursor.fetchone()

    if not student:
        connection.close()
        messagebox.showerror("Error", "Student not found.")
        return

    name = update_name_entry.get().strip()
    age = update_age_entry.get().strip()
    email = update_email_entry.get().strip()
    phone = update_phone_entry.get().strip()
    course = update_course_entry.get().strip()

    if name == "" or age == "" or email == "" or phone == "" or course == "":
        connection.close()
        messagebox.showwarning("Warning", "Please fill all fields.")
        return

    if not age.isdigit():
        connection.close()
        messagebox.showwarning("Warning", "Age must contain only numbers.")
        return

    if not phone.isdigit():
        connection.close()
        messagebox.showwarning("Warning", "Phone must contain only numbers.")
        return

    if "@" not in email:
        connection.close()
        messagebox.showwarning("Warning", "Please enter a valid email.")
        return

    cursor.execute(
        """
        UPDATE students
        SET name = ?, age = ?, email = ?, phone = ?, course = ?
        WHERE id = ?
        """,
        (name, age, email, phone, course, student_id)
    )

    connection.commit()
    connection.close()

    messagebox.showinfo("Success", "Student updated successfully.")

    load_students()
    load_courses()
    update_dashboard()


# ================= DELETE STUDENT =================

def delete_student():
    student_id = delete_id_entry.get().strip()

    if student_id == "":
        messagebox.showwarning("Warning", "Please enter Student ID.")
        return

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT name FROM students WHERE id = ?",
        (student_id,)
    )

    student = cursor.fetchone()

    if not student:
        connection.close()
        messagebox.showerror("Error", "Student not found.")
        return

    answer = messagebox.askyesno(
        "Confirm Delete",
        f"Are you sure you want to delete {student[0]}?"
    )

    if answer:
        cursor.execute(
            "DELETE FROM students WHERE id = ?",
            (student_id,)
        )

        connection.commit()

        messagebox.showinfo(
            "Success",
            "Student deleted successfully."
        )

    connection.close()

    load_students()
    load_courses()
    update_dashboard()


# ================= EDIT SELECTED =================

def edit_selected():
    selected = student_table.selection()

    if not selected:
        messagebox.showwarning(
            "Warning",
            "Please select a student."
        )
        return

    values = student_table.item(selected[0], "values")

    update_id_entry.delete(0, tk.END)
    update_id_entry.insert(0, values[0])

    update_name_entry.delete(0, tk.END)
    update_name_entry.insert(0, values[1])

    update_age_entry.delete(0, tk.END)
    update_age_entry.insert(0, values[2])

    update_email_entry.delete(0, tk.END)
    update_email_entry.insert(0, values[3])

    update_phone_entry.delete(0, tk.END)
    update_phone_entry.insert(0, values[4])

    update_course_entry.delete(0, tk.END)
    update_course_entry.insert(0, values[5])


# ================= DELETE SELECTED =================

def delete_selected():
    selected = student_table.selection()

    if not selected:
        messagebox.showwarning(
            "Warning",
            "Please select a student."
        )
        return

    values = student_table.item(selected[0], "values")

    student_id = values[0]
    student_name = values[1]

    answer = messagebox.askyesno(
        "Confirm Delete",
        f"Are you sure you want to delete {student_name}?"
    )

    if answer:
        connection = connect_db()
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM students WHERE id = ?",
            (student_id,)
        )

        connection.commit()
        connection.close()

        messagebox.showinfo(
            "Success",
            "Student deleted successfully."
        )

        load_students()
        load_courses()
        update_dashboard()


# ================= LOGOUT =================

def logout():
    answer = messagebox.askyesno(
        "Logout",
        "Are you sure you want to logout?"
    )

    if answer:
        window.withdraw()
        login_window.deiconify()

        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)

        password_entry.config(show="*")
        show_password_button.config(text="Show")

        username_entry.focus()


# ================= LOGIN =================

def check_login():
    username = username_entry.get().strip()
    password = password_entry.get().strip()

    if username == "admin" and password == "1234":
        login_window.withdraw()
        window.deiconify()

        load_students()
        load_courses()
        update_dashboard()

    else:
        messagebox.showerror(
            "Login Failed",
            "Invalid username or password."
        )


def toggle_password():
    if password_entry.cget("show") == "*":
        password_entry.config(show="")
        show_password_button.config(text="Hide")
    else:
        password_entry.config(show="*")
        show_password_button.config(text="Show")


# ================= TITLE =================

title_label = tk.Label(
    window,
    text="Student Management System",
    font=("Arial", 24, "bold"),
    bg=bg_color,
    fg=text_color
)

title_label.pack(pady=15)


subtitle_label = tk.Label(
    window,
    text="Manage student records easily",
    font=("Arial", 11),
    bg=bg_color,
    fg="gray"
)

subtitle_label.pack()


# ================= DASHBOARD =================

dashboard_frame = tk.Frame(
    window,
    bg=bg_color
)

dashboard_frame.pack(pady=15)


student_card = tk.Frame(
    dashboard_frame,
    bg="white",
    width=250,
    height=80,
    bd=1,
    relief="solid"
)

student_card.pack(side="left", padx=10)

student_card.pack_propagate(False)


tk.Label(
    student_card,
    text="Total Students",
    font=("Arial", 11),
    bg="white"
).pack(pady=5)


total_students_label = tk.Label(
    student_card,
    text="0",
    font=("Arial", 22, "bold"),
    bg="white",
    fg=text_color
)

total_students_label.pack()


course_card = tk.Frame(
    dashboard_frame,
    bg="white",
    width=250,
    height=80,
    bd=1,
    relief="solid"
)

course_card.pack(side="left", padx=10)

course_card.pack_propagate(False)


tk.Label(
    course_card,
    text="Total Courses",
    font=("Arial", 11),
    bg="white"
).pack(pady=5)


total_courses_label = tk.Label(
    course_card,
    text="0",
    font=("Arial", 22, "bold"),
    bg="white",
    fg=text_color
)

total_courses_label.pack()


# ================= ADD STUDENT FRAME =================

add_frame = tk.LabelFrame(
    window,
    text="Add Student",
    font=("Arial", 11, "bold"),
    bg=bg_color,
    fg=text_color,
    padx=10,
    pady=10
)

add_frame.pack(fill="x", padx=20, pady=5)


tk.Label(
    add_frame,
    text="Name",
    bg=bg_color
).grid(row=0, column=0, padx=5, pady=5)

name_entry = tk.Entry(add_frame, width=18)
name_entry.grid(row=0, column=1, padx=5)


tk.Label(
    add_frame,
    text="Age",
    bg=bg_color
).grid(row=0, column=2, padx=5)

age_entry = tk.Entry(add_frame, width=10)
age_entry.grid(row=0, column=3, padx=5)


tk.Label(
    add_frame,
    text="Email",
    bg=bg_color
).grid(row=1, column=0, padx=5, pady=5)

email_entry = tk.Entry(add_frame, width=18)
email_entry.grid(row=1, column=1, padx=5)


tk.Label(
    add_frame,
    text="Phone",
    bg=bg_color
).grid(row=1, column=2, padx=5)

phone_entry = tk.Entry(add_frame, width=15)
phone_entry.grid(row=1, column=3, padx=5)


tk.Label(
    add_frame,
    text="Course",
    bg=bg_color
).grid(row=2, column=0, padx=5, pady=5)

course_entry = tk.Entry(add_frame, width=18)
course_entry.grid(row=2, column=1, padx=5)


tk.Button(
    add_frame,
    text="Add Student",
    bg=button_color,
    fg="white",
    width=15,
    command=add_student
).grid(row=2, column=3, padx=5, pady=5)


# ================= SEARCH & FILTER FRAME =================

search_filter_frame = tk.LabelFrame(
    window,
    text="Search & Filter",
    font=("Arial", 11, "bold"),
    bg=bg_color,
    fg=text_color,
    padx=10,
    pady=10
)

search_filter_frame.pack(fill="x", padx=20, pady=5)


# Search by Name

tk.Label(
    search_filter_frame,
    text="Search Name:",
    bg=bg_color
).grid(row=0, column=0, padx=5)


search_name_entry = tk.Entry(
    search_filter_frame,
    width=20
)

search_name_entry.grid(
    row=0,
    column=1,
    padx=5
)


tk.Button(
    search_filter_frame,
    text="Search",
    bg=button_color,
    fg="white",
    width=10,
    command=search_by_name
).grid(
    row=0,
    column=2,
    padx=5
)


# Course Filter

tk.Label(
    search_filter_frame,
    text="Course:",
    bg=bg_color
).grid(
    row=0,
    column=3,
    padx=5
)


course_filter_combo = ttk.Combobox(
    search_filter_frame,
    width=18,
    state="readonly"
)

course_filter_combo.grid(
    row=0,
    column=4,
    padx=5
)

course_filter_combo.bind(
    "<<ComboboxSelected>>",
    filter_by_course
)


# Refresh Button

tk.Button(
    search_filter_frame,
    text="Refresh",
    bg=button_color,
    fg="white",
    width=10,
    command=refresh_students
).grid(
    row=0,
    column=5,
    padx=5
)



# ================= SORT TABLE =================

def sort_table(column, reverse=False):
    data = [
        (student_table.set(item, column), item)
        for item in student_table.get_children("")
    ]

    if column in ("ID", "Age"):
        try:
            data.sort(key=lambda x: int(x[0]), reverse=reverse)
        except ValueError:
            data.sort(key=lambda x: x[0].lower(), reverse=reverse)
    else:
        data.sort(key=lambda x: x[0].lower(), reverse=reverse)

    for index, (value, item) in enumerate(data):
        student_table.move(item, "", index)

    student_table.heading(
        column,
        command=lambda: sort_table(column, not reverse)
    )


# ================= STUDENT TABLE =================

table_frame = tk.Frame(
    window,
    bg=bg_color
)

table_frame.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=5
)


columns = (
    "ID",
    "Name",
    "Age",
    "Email",
    "Phone",
    "Course"
)


student_table = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings",
    height=8
)


for column in columns:
    student_table.heading(
        column,
        text=column,
        command=lambda col=column: sort_table(col, False)
    )


student_table.column("ID", width=40)
student_table.column("Name", width=100)
student_table.column("Age", width=50)
student_table.column("Email", width=180)
student_table.column("Phone", width=110)
student_table.column("Course", width=120)


student_table.pack(
    side="left",
    fill="both",
    expand=True
)


scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=student_table.yview
)

scrollbar.pack(
    side="right",
    fill="y"
)


student_table.configure(
    yscrollcommand=scrollbar.set
)


# ================= TABLE BUTTONS =================

table_button_frame = tk.Frame(
    window,
    bg=bg_color
)

table_button_frame.pack(pady=5)


tk.Button(
    table_button_frame,
    text="Edit Selected",
    bg=button_color,
    fg="white",
    width=15,
    command=edit_selected
).pack(side="left", padx=5)


tk.Button(
    table_button_frame,
    text="Delete Selected",
    bg=button_color,
    fg="white",
    width=15,
    command=delete_selected
).pack(side="left", padx=5)


tk.Button(
    table_button_frame,
    text="Refresh",
    bg=button_color,
    fg="white",
    width=12,
    command=refresh_students
).pack(side="left", padx=5)


tk.Button(
    table_button_frame,
    text="Export to Excel",
    bg=button_color,
    fg="white",
    width=15,
    command=export_to_excel
).pack(side="left", padx=5)


# ================= SEARCH BY ID =================

search_frame = tk.LabelFrame(
    window,
    text="Search Student by ID",
    bg=bg_color,
    fg=text_color,
    font=("Arial", 10, "bold")
)

search_frame.pack(
    fill="x",
    padx=20,
    pady=5
)


search_id_entry = tk.Entry(
    search_frame,
    width=15
)

search_id_entry.pack(
    side="left",
    padx=10,
    pady=5
)


tk.Button(
    search_frame,
    text="Search",
    bg=button_color,
    fg="white",
    command=search_student
).pack(
    side="left",
    padx=5
)


result_label = tk.Label(
    search_frame,
    text="",
    bg=bg_color,
    justify="left"
)

result_label.pack(
    side="left",
    padx=20
)


# ================= UPDATE =================

update_frame = tk.LabelFrame(
    window,
    text="Update Student",
    bg=bg_color,
    fg=text_color,
    font=("Arial", 10, "bold")
)

update_frame.pack(
    fill="x",
    padx=20,
    pady=5
)


tk.Label(
    update_frame,
    text="ID",
    bg=bg_color
).grid(row=0, column=0, padx=5, pady=3)

update_id_entry = tk.Entry(
    update_frame,
    width=8
)

update_id_entry.grid(
    row=0,
    column=1,
    padx=5
)


tk.Label(
    update_frame,
    text="Name",
    bg=bg_color
).grid(row=0, column=2, padx=5)

update_name_entry = tk.Entry(
    update_frame,
    width=15
)

update_name_entry.grid(
    row=0,
    column=3,
    padx=5
)


tk.Label(
    update_frame,
    text="Age",
    bg=bg_color
).grid(row=0, column=4, padx=5)

update_age_entry = tk.Entry(
    update_frame,
    width=8
)

update_age_entry.grid(
    row=0,
    column=5,
    padx=5
)


tk.Label(
    update_frame,
    text="Email",
    bg=bg_color
).grid(row=1, column=0, padx=5)

update_email_entry = tk.Entry(
    update_frame,
    width=15
)

update_email_entry.grid(
    row=1,
    column=1,
    padx=5
)


tk.Label(
    update_frame,
    text="Phone",
    bg=bg_color
).grid(row=1, column=2, padx=5)

update_phone_entry = tk.Entry(
    update_frame,
    width=15
)

update_phone_entry.grid(
    row=1,
    column=3,
    padx=5
)


tk.Label(
    update_frame,
    text="Course",
    bg=bg_color
).grid(row=1, column=4, padx=5)

update_course_entry = tk.Entry(
    update_frame,
    width=12
)

update_course_entry.grid(
    row=1,
    column=5,
    padx=5
)


tk.Button(
    update_frame,
    text="Update",
    bg=button_color,
    fg="white",
    width=12,
    command=update_student
).grid(
    row=1,
    column=6,
    padx=10
)


# ================= DELETE =================

delete_frame = tk.Frame(
    window,
    bg=bg_color
)

delete_frame.pack(
    pady=5
)


tk.Label(
    delete_frame,
    text="Delete by ID:",
    bg=bg_color
).pack(side="left")


delete_id_entry = tk.Entry(
    delete_frame,
    width=10
)

delete_id_entry.pack(
    side="left",
    padx=5
)


tk.Button(
    delete_frame,
    text="Delete",
    bg=button_color,
    fg="white",
    width=10,
    command=delete_student
).pack(side="left", padx=5)


# ================= LOGOUT BUTTON =================

tk.Button(
    window,
    text="Logout",
    bg=button_color,
    fg="white",
    width=12,
    command=logout
).pack(pady=5)


# ================= LOGIN WINDOW =================

login_window = tk.Toplevel(window)

login_window.title("Login")
login_window.geometry("430x380")
login_window.resizable(False, False)

login_window.configure(bg=bg_color)


tk.Label(
    login_window,
    text="Student Management System",
    font=("Arial", 18, "bold"),
    bg=bg_color,
    fg=text_color
).pack(pady=30)


tk.Label(
    login_window,
    text="Username",
    font=("Arial", 11),
    bg=bg_color
).pack()


username_entry = tk.Entry(
    login_window,
    width=28
)

username_entry.pack(pady=8)


tk.Label(
    login_window,
    text="Password",
    font=("Arial", 11),
    bg=bg_color
).pack()


password_frame = tk.Frame(
    login_window,
    bg=bg_color
)

password_frame.pack(pady=8)


password_entry = tk.Entry(
    password_frame,
    width=20,
    show="*"
)

password_entry.pack(
    side="left"
)


show_password_button = tk.Button(
    password_frame,
    text="Show",
    width=7,
    command=toggle_password
)

show_password_button.pack(
    side="left",
    padx=5
)


tk.Button(
    login_window,
    text="Login",
    bg=button_color,
    fg="white",
    width=20,
    height=2,
    command=check_login
).pack(pady=20)


tk.Label(
    login_window,
    text="Username: admin\nPassword: 1234",
    bg=bg_color,
    fg="gray"
).pack()


# Press Enter to Login

password_entry.bind(
    "<Return>",
    lambda event: check_login()
)


# ================= START =================

window.withdraw()

username_entry.focus()

login_window.protocol(
    "WM_DELETE_WINDOW",
    window.destroy
)

login_window.mainloop()