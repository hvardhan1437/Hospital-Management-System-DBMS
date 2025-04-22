import sqlite3
from db_setup import create_connection

# Create a new department (by Manager/Admin)
def create_department(department_name, department_head=None):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # If a department head is provided, check if the doctor exists
            if department_head:
                cursor.execute("SELECT * FROM Doctor WHERE Doctor_ID = ?", (department_head,))
                doctor = cursor.fetchone()
                if doctor is None:
                    print("Doctor not found. Cannot assign as department head.")
                    return

            # Insert new department with optional head
            cursor.execute('''
                INSERT INTO Department (Department_Name, Department_Head)
                VALUES (?, ?)
            ''', (department_name, department_head))
            conn.commit()
            print("Department created successfully!")
        except sqlite3.Error as e:
            print(f"An error occurred while creating department: {e}")
        finally:
            conn.close()  # Ensure connection is closed
    else:
        print("Error: Unable to connect to the database.")

# View department details
def view_department(department_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Fetch department details
            cursor.execute("SELECT * FROM Department WHERE Department_ID = ?", (department_id,))
            department = cursor.fetchone()

            if department:
                print(f"Department Details:\nID: {department[0]}, Name: {department[1]}, Head Doctor ID: {department[2]}")
            else:
                print("Department not found.")
        except sqlite3.Error as e:
            print(f"An error occurred while fetching department details: {e}")
        finally:
            conn.close()  # Ensure connection is closed
    else:
        print("Error: Unable to connect to the database.")

# Assign a doctor as the head of the department (by Manager/Admin)
def assign_department_head(department_id, doctor_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Check if the department exists
            cursor.execute("SELECT * FROM Department WHERE Department_ID = ?", (department_id,))
            department = cursor.fetchone()

            if department is None:
                print("Department not found.")
                return

            # Check if the doctor exists
            cursor.execute("SELECT * FROM Doctor WHERE Doctor_ID = ?", (doctor_id,))
            doctor = cursor.fetchone()

            if doctor is None:
                print("Doctor not found. Cannot assign as department head.")
                return

            # Assign the doctor as the department head
            cursor.execute('''
                UPDATE Department
                SET Department_Head = ?
                WHERE Department_ID = ?
            ''', (doctor_id, department_id))
            conn.commit()

            if cursor.rowcount > 0:
                print("Doctor assigned as department head successfully!")
            else:
                print("Failed to assign department head.")
        except sqlite3.Error as e:
            print(f"An error occurred while assigning department head: {e}")
        finally:
            conn.close()  # Ensure connection is closed
    else:
        print("Error: Unable to connect to the database.")

# View all departments (optional)
def view_all_departments():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Fetch all departments
            cursor.execute("SELECT * FROM Department")
            departments = cursor.fetchall()

            if departments:
                print("All Departments:")
                for department in departments:
                    print(f"ID: {department[0]}, Name: {department[1]}, Head Doctor ID: {department[2]}")
            else:
                print("No departments found.")
        except sqlite3.Error as e:
            print(f"An error occurred while fetching all departments: {e}")
        finally:
            conn.close()  # Ensure connection is closed
    else:
        print("Error: Unable to connect to the database.")
