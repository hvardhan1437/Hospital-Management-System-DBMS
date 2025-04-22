import sqlite3
from db_setup import create_connection

# Helper functions to avoid repetition
def patient_exists(patient_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Patient WHERE Patient_ID = ?", (patient_id,))
            return cursor.fetchone() is not None
        finally:
            conn.close()

def doctor_exists(doctor_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Doctor WHERE Doctor_ID = ?", (doctor_id,))
            return cursor.fetchone() is not None
        finally:
            conn.close()

# Display available doctors with their departments
def display_doctors_with_departments():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT Doctor.Doctor_ID, Doctor.Name, Department.Department_Name 
                FROM Doctor 
                JOIN Department ON Doctor.Department_ID = Department.Department_ID
            ''')
            doctors = cursor.fetchall()

            if doctors:
                print("Available Doctors:")
                for doctor in doctors:
                    print(f"Doctor ID: {doctor[0]}, Name: {doctor[1]}, Department: {doctor[2]}")
            else:
                print("No doctors available.")
        except sqlite3.Error as e:
            print(f"An error occurred while fetching doctors: {e}")
        finally:
            conn.close()

# Modified create_appointment to show doctors and departments first
def create_appointment(patient_id, doctor_id, appointment_date, reason):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Check if the patient exists before creating the appointment
            cursor.execute("SELECT * FROM Patient WHERE Patient_ID = ?", (patient_id,))
            patient = cursor.fetchone()

            if not patient:
                print("Patient not found. Cannot create appointment.")
                return

            # Check if the doctor exists before creating the appointment
            cursor.execute("SELECT * FROM Doctor WHERE Doctor_ID = ?", (doctor_id,))
            doctor = cursor.fetchone()

            if not doctor:
                print("Doctor not found. Cannot create appointment.")
                return

            # Insert the appointment into the Appointment table
            cursor.execute('''
                INSERT INTO Appointment (Patient_ID, Doctor_ID, Appointment_Date, Reason)
                VALUES (?, ?, ?, ?)
            ''', (patient_id, doctor_id, appointment_date, reason))

            conn.commit()
            print("Appointment created successfully!")
        except sqlite3.Error as e:
            print(f"An error occurred while creating the appointment: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")

# View appointments for a specific patient
def view_appointments_for_patient(user_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Fetch the patient ID using the user ID
            cursor.execute("SELECT Patient_ID FROM Patient WHERE User_ID = ?", (user_id,))
            patient = cursor.fetchone()
            
            if not patient:
                print("Patient not found.")
                conn.close()
                return
            
            patient_id = patient[0]  # Get the patient ID

            # Fetch appointments for the patient
            cursor.execute('''
                SELECT Appointment.Appointment_ID, Doctor.Name, Appointment.Appointment_Date, Appointment.Reason
                FROM Appointment
                JOIN Doctor ON Appointment.Doctor_ID = Doctor.Doctor_ID
                WHERE Appointment.Patient_ID = ?
            ''', (patient_id,))
            appointments = cursor.fetchall()

            if appointments:
                print("Your Appointments:")
                for appointment in appointments:
                    print(f"Appointment ID: {appointment[0]}, Doctor: {appointment[1]}, Date: {appointment[2]}, Reason: {appointment[3]}")
            else:
                print("No appointments found.")
        except sqlite3.Error as e:
            print(f"An error occurred while fetching the appointments: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")

# View appointments for a specific doctor
def view_appointments_for_doctor(user_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Fetch the doctor ID using the user ID
            cursor.execute("SELECT Doctor_ID FROM Doctor WHERE User_ID = ?", (user_id,))
            doctor = cursor.fetchone()
            
            if not doctor:
                print("Doctor not found.")
                conn.close()
                return
            
            doctor_id = doctor[0]  # Get the doctor ID

            # Fetch appointments for the doctor
            cursor.execute('''
                SELECT Appointment.Appointment_ID, Patient.Name, Appointment.Appointment_Date, Appointment.Reason
                FROM Appointment
                JOIN Patient ON Appointment.Patient_ID = Patient.Patient_ID
                WHERE Appointment.Doctor_ID = ?
            ''', (doctor_id,))
            
            appointments = cursor.fetchall()
            
            if appointments:
                print("Your Appointments:")
                for appointment in appointments:
                    print(f"Appointment ID: {appointment[0]}, Patient: {appointment[1]}, Date: {appointment[2]}, Reason: {appointment[3]}")
            else:
                print("No appointments found.")
        except sqlite3.Error as e:
            print(f"An error occurred while fetching the appointments: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")

# Cancel an appointment (by Patient or Admin)
def cancel_appointment(appointment_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Appointment WHERE Appointment_ID = ?", (appointment_id,))
            appointment = cursor.fetchone()

            if appointment is None:
                print("Appointment not found.")
                return

            # Delete the appointment
            cursor.execute('''
                DELETE FROM Appointment WHERE Appointment_ID = ?
            ''', (appointment_id,))
            conn.commit()

            if cursor.rowcount > 0:
                print("Appointment cancelled successfully!")
            else:
                print("Failed to cancel appointment.")
        except sqlite3.Error as e:
            print(f"An error occurred while canceling the appointment: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")

# Reschedule an appointment (by Patient or Admin)
def reschedule_appointment(appointment_id, new_date):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Appointment WHERE Appointment_ID = ?", (appointment_id,))
            appointment = cursor.fetchone()

            if appointment is None:
                print("Appointment not found.")
                return

            # Reschedule the appointment
            cursor.execute('''
                UPDATE Appointment
                SET Appointment_Date = ?
                WHERE Appointment_ID = ?
            ''', (new_date, appointment_id))
            conn.commit()

            if cursor.rowcount > 0:
                print("Appointment rescheduled successfully!")
            else:
                print("Failed to reschedule appointment.")
        except sqlite3.Error as e:
            print(f"An error occurred while rescheduling the appointment: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")
