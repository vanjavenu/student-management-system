
import sqlite3


def add_student():
    name = input("Enter student name: ")
    age = int(input("Enter student age: "))
    email = input("Enter student email: ")
    phone = input("Enter student phone: ")
    course = input("Enter student course: ")

    connection = sqlite3.connect("students.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO students (name, age, email, phone, course)
        VALUES (?, ?, ?, ?, ?)
    """, (name, age, email, phone, course))

    connection.commit()
    connection.close()

    print("Student added successfully!")


def view_students():
    connection = sqlite3.connect("students.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    connection.close()

    print("\n--- Student List ---")

    for student in students:
        print(student)


def search_student():
    student_id = input("Enter student ID: ")

    connection = sqlite3.connect("students.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    )

    student = cursor.fetchone()

    connection.close()

    if student:
        print("\n--- Student Found ---")
        print("ID:", student[0])
        print("Name:", student[1])
        print("Age:", student[2])
        print("Email:", student[3])
        print("Phone:", student[4])
        print("Course:", student[5])
    else:
        print("Student not found.")


def update_student():
    student_id = input("Enter student ID to update: ")

    name = input("Enter new name: ")
    age = int(input("Enter new age: "))
    email = input("Enter new email: ")
    phone = input("Enter new phone: ")
    course = input("Enter new course: ")

    connection = sqlite3.connect("students.db")
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE students
        SET name = ?, age = ?, email = ?, phone = ?, course = ?
        WHERE id = ?
    """, (name, age, email, phone, course, student_id))

    connection.commit()

    if cursor.rowcount > 0:
        print("Student updated successfully!")
    else:
        print("Student not found.")

    connection.close()


def delete_student():
    student_id = input("Enter student ID to delete: ")

    connection = sqlite3.connect("students.db")
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM students WHERE id = ?",
        (student_id,)
    )

    connection.commit()

    if cursor.rowcount > 0:
        print("Student deleted successfully!")
    else:
        print("Student not found.")

    connection.close()


while True:
    print("\n===== Student Management System =====")
    print("1. Add Student")
    print("2. View Students")
    print("3. Search Student")
    print("4. Update Student")
    print("5. Delete Student")
    print("6. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        add_student()

    elif choice == "2":
        view_students()

    elif choice == "3":
        search_student()

    elif choice == "4":
        update_student()

    elif choice == "5":
        delete_student()

    elif choice == "6":
        print("Thank you for using Student Management System!")
        break

    else:
        print("Invalid choice. Please try again.")