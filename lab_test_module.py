import sqlite3
from db_setup import create_connection
from patient_module import patient_exists
from doctor_module import doctor_exists
from lab_technician_module import view_all_lab_technicians

# Assign a lab test to a patient
def assign_lab_test(test_name, patient_id=None, doctor_id=None, lab_technician_id=None, test_date=None):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Display available patients if patient_id is None
            if not patient_id:
                cursor.execute("SELECT Patient_ID, Name FROM Patient")
                patients = cursor.fetchall()
                if patients:
                    print("Available Patients:")
                    for patient in patients:
                        print(f"ID: {patient[0]}, Name: {patient[1]}")
                    # Prompt for Patient ID once
                    patient_id = int(input("Enter Patient ID: "))
                else:
                    print("No patients available.")
                    return

            # Check if the patient exists
            cursor.execute("SELECT * FROM Patient WHERE Patient_ID = ?", (patient_id,))
            if cursor.fetchone() is None:
                print("Error: Invalid Patient ID. Please ensure the patient exists.")
                return

            # Display available doctors if doctor_id is None
            if not doctor_id:
                cursor.execute("SELECT Doctor_ID, Name FROM Doctor")
                doctors = cursor.fetchall()
                if doctors:
                    print("Available Doctors:")
                    for doctor in doctors:
                        print(f"ID: {doctor[0]}, Name: {doctor[1]}")
                    # Prompt for Doctor ID once
                    doctor_id = int(input("Enter Doctor ID: "))
                else:
                    print("No doctors available.")
                    return

            # Check if the doctor exists
            cursor.execute("SELECT * FROM Doctor WHERE Doctor_ID = ?", (doctor_id,))
            if cursor.fetchone() is None:
                print("Error: Invalid Doctor ID. Please ensure the doctor exists.")
                return

            # Display available lab technicians if lab_technician_id is None
            if not lab_technician_id:
                cursor.execute("SELECT Lab_Technician_ID, Name FROM Lab_Technician")
                technicians = cursor.fetchall()
                if technicians:
                    print("Available Lab Technicians:")
                    for tech in technicians:
                        print(f"ID: {tech[0]}, Name: {tech[1]}")
                    # Prompt for Lab Technician ID once
                    lab_technician_id = int(input("Enter Lab Technician ID: "))
                else:
                    print("No lab technicians available.")
                    return

            # Check if the lab technician exists
            cursor.execute("SELECT * FROM Lab_Technician WHERE Lab_Technician_ID = ?", (lab_technician_id,))
            if cursor.fetchone() is None:
                print("Error: Invalid Lab Technician ID. Please ensure the technician exists.")
                return

            # Ensure test_date is provided
            if not test_date:
                test_date = input("Enter Test Date (YYYY-MM-DD): ")

            # Insert the lab test record
            cursor.execute('''
                INSERT INTO Lab_Test (Test_Name, Patient_ID, Doctor_ID, Lab_Technician_ID, Test_Date)
                VALUES (?, ?, ?, ?, ?)
            ''', (test_name, patient_id, doctor_id, lab_technician_id, test_date))
            conn.commit()
            print("Lab test assigned successfully!")

        except sqlite3.Error as e:
            print(f"An error occurred while assigning lab test: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")

# Record lab test results by Lab Technician
def record_lab_test_result(test_id, result):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE Lab_Test
                SET Result = ?
                WHERE Lab_Test_ID = ?
            ''', (result, test_id))
            conn.commit()
            print("Lab Test result recorded successfully!")
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            conn.close()

# View lab tests assigned to a patient
def view_lab_tests_for_patient(patient_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT Lab_Test.Test_Name, Doctor.Name AS Doctor_Name, Lab_Test.Test_Date, Lab_Test.Result
                FROM Lab_Test
                LEFT JOIN Doctor ON Lab_Test.Doctor_ID = Doctor.Doctor_ID
                WHERE Lab_Test.Patient_ID = ?
            ''', (patient_id,))
            lab_tests = cursor.fetchall()

            if lab_tests:
                print("Your Lab Tests:")
                for test in lab_tests:
                    # Display the lab test details
                    print(f"Test: {test[0]}, Doctor: {test[1]}, Date: {test[2]}, Result: {test[3] if test[3] else 'Pending'}")
            else:
                print("No lab tests found.")
        except sqlite3.Error as e:
            print(f"An error occurred while fetching lab tests: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")
