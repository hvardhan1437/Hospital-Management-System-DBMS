import sqlite3
# prescription_module.py
from db_setup import create_connection
import datetime
from pharmacy_module import view_available_medicines,medicine_exists
def add_prescription(doctor_id, patient_id, medicine_id, dosage, duration, instructions, prescription_date):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Add prescription with Medicine_ID instead of Medicine_Name
            cursor.execute('''
                INSERT INTO Prescription (Doctor_ID, Patient_ID, Medicine_ID, Dosage, Duration, Date, Instructions)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (doctor_id, patient_id, medicine_id, dosage, duration, prescription_date, instructions))

            conn.commit()
            print("Prescription added successfully!")
        except sqlite3.Error as e:
            print(f"An error occurred while adding prescription: {e}")
        finally:
            conn.close()



def view_prescriptions_for_patient(patient_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Updated query to join Medicine table
            cursor.execute('''
                SELECT Doctor.Name, Medicine.Medicine_Name, Prescription.Dosage, 
                       Prescription.Duration, Prescription.Date, Prescription.Instructions
                FROM Prescription
                JOIN Doctor ON Prescription.Doctor_ID = Doctor.Doctor_ID
                JOIN Medicine ON Prescription.Medicine_ID = Medicine.Medicine_ID
                WHERE Prescription.Patient_ID = ?
            ''', (patient_id,))
            
            prescriptions = cursor.fetchall()
            
            if prescriptions:
                print(f"Prescriptions for Patient ID {patient_id}:")
                for doctor_name, medicine_name, dosage, duration, date, instructions in prescriptions:
                    print(f"Doctor: {doctor_name}, Medicine: {medicine_name}, Dosage: {dosage}, Duration: {duration}, Date: {date}")
                    if instructions:
                        print(f"Instructions: {instructions}")
            else:
                print("No prescriptions found for this patient.")
        except sqlite3.Error as e:
            print(f"An error occurred while fetching prescriptions: {e}")
        finally:
            conn.close()



def prescription_exists(prescription_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM Prescription WHERE Prescription_ID = ?", (prescription_id,))
            return cursor.fetchone() is not None
        except sqlite3.Error as e:
            print(f"An error occurred while checking prescription existence: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")
    return False


# View available medicines in the pharmacy
def view_all_prescriptions():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT Prescription.Prescription_ID, Doctor.Name AS Doctor_Name, Patient.Name AS Patient_Name,
                       Prescription.Medicine_Name, Prescription.Dosage, Prescription.Duration, Prescription.Date, Prescription.Instructions
                FROM Prescription
                JOIN Doctor ON Prescription.Doctor_ID = Doctor.Doctor_ID
                JOIN Patient ON Prescription.Patient_ID = Patient.Patient_ID
            ''')
            prescriptions = cursor.fetchall()
            
            if prescriptions:
                print("Available Prescriptions:")
                for prescription in prescriptions:
                    print(f"ID: {prescription[0]}, Doctor: {prescription[1]}, Patient: {prescription[2]}, "
                          f"Medicine: {prescription[3]}, Dosage: {prescription[4]}, Duration: {prescription[5]}, "
                          f"Date: {prescription[6]}, Instructions: {prescription[7]}")
                return True
            else:
                print("No prescriptions available.")
                return False
        except sqlite3.Error as e:
            print(f"An error occurred while fetching prescriptions: {e}")
            return False
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")
        return False

