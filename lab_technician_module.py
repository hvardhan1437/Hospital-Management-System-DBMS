import sqlite3
from db_setup import create_connection

# Add a new lab technician
def add_lab_technician(name, contact_number):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO Lab_Technician (Name, Contact_Number)
                VALUES (?, ?)
            ''', (name, contact_number))
            conn.commit()
            print("Lab Technician added successfully!")
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            conn.close()
# Assign a lab test to a lab technician
def assign_lab_test(test_name, patient_id, doctor_id, lab_technician_id, test_date):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO Lab_Test (Test_Name, Patient_ID, Doctor_ID, Lab_Technician_ID, Test_Date)
                VALUES (?, ?, ?, ?, ?)
            ''', (test_name, patient_id, doctor_id, lab_technician_id, test_date))
            conn.commit()
            print("Lab test assigned successfully!")
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            conn.close()
    else:
        print("Failed to assign lab test due to connection issues.")

# View all lab technicians
def view_all_lab_technicians():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Lab_Technician")
            technicians = cursor.fetchall()

            if technicians:
                print("Lab Technicians:")
                for tech in technicians:
                    print(f"ID: {tech[0]}, Name: {tech[1]}, Contact: {tech[2]}")
            else:
                print("No lab technicians found.")
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            conn.close()
