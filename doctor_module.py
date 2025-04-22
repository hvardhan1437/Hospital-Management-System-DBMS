import sqlite3
from db_setup import create_connection
from prescription_module import add_prescription, view_prescriptions_for_patient

# Add a new doctor (by Manager/Admin)
# doctor_module.py

import sqlite3
from db_setup import create_connection

# Add a doctor to the database
def add_doctor(name, specialty, contact_number, department_id, user_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Print the user_id being used to ensure it matches the expected value
            print(f"Adding doctor with User_ID: {user_id}")

            # Check if the user exists in the User table before adding the doctor
            cursor.execute("SELECT * FROM User WHERE User_ID = ?", (user_id,))
            user = cursor.fetchone()
            if not user:
                print(f"Error: No user found with User_ID {user_id}. Cannot add doctor.")
                return
            
            cursor.execute('''
            INSERT INTO Doctor (Name, Specialty, Contact_Number, Department_ID, User_ID)
            VALUES (?, ?, ?, ?, ?)
            ''', (name, specialty, contact_number, department_id, user_id))

            conn.commit()
            print("Doctor added successfully!")
        except sqlite3.Error as e:
            print(f"An error occurred while adding doctor: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")

import sqlite3
from db_setup import create_connection

# Check if a doctor exists by ID
def doctor_exists(doctor_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Doctor WHERE Doctor_ID = ?", (doctor_id,))
            return cursor.fetchone() is not None
        except sqlite3.Error as e:
            print(f"An error occurred while checking doctor existence: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")
    return False

# View doctor details
def view_doctor(doctor_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Doctor WHERE Doctor_ID = ?", (doctor_id,))
            doctor = cursor.fetchone()
            if doctor:
                print(f"Doctor Details:\nID: {doctor[0]}, Name: {doctor[1]}, Specialty: {doctor[2]}, Contact: {doctor[3]}")
            else:
                print("Doctor not found.")
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")

def update_medical_history(patient_id, medical_history):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Patient WHERE Patient_ID = ?", (patient_id,))
            patient = cursor.fetchone()
            if patient:
                cursor.execute('''
                    UPDATE Patient
                    SET Medical_History = ?
                    WHERE Patient_ID = ?
                ''', (medical_history, patient_id))
                conn.commit()
                print("Medical history updated successfully!")
            else:
                print("Patient not found.")
        except sqlite3.Error as e:
            print(f"An error occurred while updating medical history: {e}")
        finally:
            conn.close()

# Assign a doctor to a department (by Manager/Admin)
def assign_doctor_to_department(doctor_id, department_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Check if the doctor exists
            cursor.execute("SELECT * FROM Doctor WHERE Doctor_ID = ?", (doctor_id,))
            doctor = cursor.fetchone()

            if doctor is None:
                print("Doctor not found.")
                return

            # Check if the department exists
            cursor.execute("SELECT * FROM Department WHERE Department_ID = ?", (department_id,))
            department = cursor.fetchone()

            if department is None:
                print("Department not found.")
                return

            # Assign the doctor to the department
            cursor.execute('''
                UPDATE Doctor
                SET Department_ID = ?
                WHERE Doctor_ID = ?
            ''', (department_id, doctor_id))
            conn.commit()

            if cursor.rowcount > 0:
                print("Doctor assigned to department successfully!")
            else:
                print("Failed to assign the doctor to department.")
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            conn.close()  # Ensure connection is closed
    else:
        print("Error: Unable to connect to the database.")

# View patients in a doctor's department (by Doctor)
def view_patients_in_department(doctor_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Get the department of the doctor
            cursor.execute("SELECT Department_ID FROM Doctor WHERE Doctor_ID = ?", (doctor_id,))
            department = cursor.fetchone()

            if department:
                department_id = department[0]

                # Retrieve all patients in this department
                cursor.execute('''
                    SELECT Patient.Name, Patient.Contact_Number, Patient.Medical_History
                    FROM Patient
                    JOIN Doctor ON Doctor.User_ID = Patient.User_ID
                    WHERE Doctor.Department_ID = ? AND Doctor.Doctor_ID = ?
                ''', (department_id, doctor_id))
                patients = cursor.fetchall()

                if patients:
                    print("Patients in your department:")
                    for patient in patients:
                        print(f"Name: {patient[0]}, Contact: {patient[1]}, Medical History: {patient[2]}")
                else:
                    print("No patients found in your department.")
            else:
                print("Department not found for the doctor.")
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            conn.close()  # Ensure connection is closed
    else:
        print("Error: Unable to connect to the database.")

# View all doctors (by Manager/Admin)
def view_all_doctors():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT Doctor_ID, Name, Specialty, Contact_Number, Department_ID
                FROM Doctor
            ''')
            doctors = cursor.fetchall()
            if doctors:
                print("All Doctors:")
                for doctor in doctors:
                    print(f"ID: {doctor[0]}, Name: {doctor[1]}, Specialty: {doctor[2]}, Contact: {doctor[3]}, Department_ID: {doctor[4]}")
            else:
                print("No doctors found.")
        except sqlite3.Error as e:
            print(f"An error occurred while fetching doctors: {e}")
        finally:
            conn.close()


# Delete a doctor (by Admin)
def delete_doctor(doctor_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Check if the doctor exists before deletion
            cursor.execute("SELECT * FROM Doctor WHERE Doctor_ID = ?", (doctor_id,))
            doctor = cursor.fetchone()

            if doctor is None:
                print("Doctor not found.")
                return

            # Fetch the associated User_ID for the doctor using the correct index
            user_id = doctor[5]  # Index 5 for User_ID in the Doctor table

            # Delete the doctor record
            cursor.execute("DELETE FROM Doctor WHERE Doctor_ID = ?", (doctor_id,))
            doctor_deleted = cursor.rowcount

            if doctor_deleted > 0:
                # Now delete the associated user from the User table
                cursor.execute("DELETE FROM User WHERE User_ID = ?", (user_id,))
                user_deleted = cursor.rowcount

                if user_deleted > 0:
                    print("Doctor and associated user deleted successfully!")
                else:
                    print("Error: Failed to delete the associated user.")
                    
                conn.commit()  # Commit the transaction to ensure the deletion is saved
            else:
                print("Failed to delete doctor.")
                
        except sqlite3.Error as e:
            print(f"An error occurred while deleting doctor: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")


def view_appointments_for_doctor(doctor_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT Appointment.Appointment_ID, Patient.Name, Appointment.Appointment_Date, Appointment.Reason
                FROM Appointment
                JOIN Patient ON Appointment.Patient_ID = Patient.Patient_ID
                WHERE Appointment.Doctor_ID = ?
            ''', (doctor_id,))
            appointments = cursor.fetchall()
            if appointments:
                print(f"Appointments for Doctor ID {doctor_id}:")
                for appointment in appointments:
                    print(f"Appointment ID: {appointment[0]}, Patient Name: {appointment[1]}, Date: {appointment[2]}, Reason: {appointment[3]}")
            else:
                print("No appointments found.")
        except sqlite3.Error as e:
            print(f"An error occurred while fetching appointments: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")
# doctor_functions.py or at the top of main.py if not modularized

def get_doctor_id_by_user_id(user_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Doctor_ID FROM Doctor WHERE User_ID = ?", (user_id,))
            result = cursor.fetchone()
            if result:
                return result[0]  # return Doctor_ID
            else:
                print("Error: No doctor found for this user ID.")
                return None
        except sqlite3.Error as e:
            print(f"An error occurred while fetching doctor ID: {e}")
            return None
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")
        return None
