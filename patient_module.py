import sqlite3
from db_setup import create_connection
from appointment_module import create_appointment, view_appointments_for_patient
from prescription_module import view_prescriptions_for_patient

# Create a new patient (only accessible by Managers)
def create_patient(name, address, contact_number, dob, gender, medical_history, user_id):
    # Ensure user_id is of the correct type (integer)
    if not isinstance(user_id, int):
        print("Error: Invalid user_id. It must be an integer.")
        return
    
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Insert the patient details into the table, ensuring user_id is used correctly
            cursor.execute('''
                INSERT INTO Patient (Name, Address, Contact_Number, Date_of_Birth, Gender, Medical_History, User_ID)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, address, contact_number, dob, gender, medical_history, user_id))

            conn.commit()
            print("Patient created successfully!")
        except sqlite3.Error as e:
            print(f"An error occurred while creating patient: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")

def patient_exists(patient_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Patient WHERE Patient_ID = ?", (patient_id,))
            return cursor.fetchone() is not None
        except sqlite3.Error as e:
            print(f"An error occurred while checking patient existence: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")
    return False
# View lab tests for a patient

def view_lab_tests_for_patient(patient_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT Lab_Test.Test_Name, Doctor.Name AS Doctor_Name, Lab_Test.Test_Date, Lab_Test.Result
                FROM Lab_Test
                JOIN Doctor ON Lab_Test.Doctor_ID = Doctor.Doctor_ID
                WHERE Lab_Test.Patient_ID = ?
            ''', (patient_id,))
            lab_tests = cursor.fetchall()

            if lab_tests:
                print("Your Lab Tests:")
                for test in lab_tests:
                    # Display only the single lab technician
                    print(f"Test: {test[0]}, Doctor: {test[1]}, Lab Technician: Predefined Technician, Date: {test[2]}, Result: {test[3]}")
            else:
                print("No lab tests found.")
        except sqlite3.Error as e:
            print(f"An error occurred while fetching lab tests: {e}")
        finally:
            conn.close()

# View a patient's details (only for the logged-in patient)
def view_patient(patient_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Fetch the patient using the Patient_ID
            cursor.execute("SELECT * FROM Patient WHERE Patient_ID = ?", (patient_id,))
            patient = cursor.fetchone()

            if patient:
                print(f"Patient Details:\nID: {patient[0]}, Name: {patient[1]}, Address: {patient[2]}, Contact: {patient[3]}")
                print(f"DOB: {patient[4]}, Gender: {patient[5]}, Medical History: {patient[6]}")
            else:
                print("Patient not found.")
        except sqlite3.Error as e:
            print(f"An error occurred while fetching patient details: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")

# Update patient details (only for the logged-in patient)
def update_patient(user_id, name=None, address=None, contact_number=None, dob=None, gender=None):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Check if the patient exists
            cursor.execute("SELECT * FROM Patient WHERE User_ID = ?", (user_id,))
            patient = cursor.fetchone()

            if patient is None:
                print("Patient not found.")
                return

            # Build the update query dynamically
            update_fields = []
            update_values = []

            if name:
                update_fields.append("Name = ?")
                update_values.append(name)
            if address:
                update_fields.append("Address = ?")
                update_values.append(address)
            if contact_number:
                update_fields.append("Contact_Number = ?")
                update_values.append(contact_number)
            if dob:
                update_fields.append("Date_of_Birth = ?")
                update_values.append(dob)
            if gender:
                update_fields.append("Gender = ?")
                update_values.append(gender)

            if update_fields:
                update_values.append(user_id)
                query = f"UPDATE Patient SET {', '.join(update_fields)} WHERE User_ID = ?"
                cursor.execute(query, update_values)
                conn.commit()
                print("Patient updated successfully!")
            else:
                print("No details provided to update.")
        except sqlite3.Error as e:
            print(f"An error occurred while updating: {e}")
        finally:
            conn.close()  # Ensure connection is closed
    else:
        print("Error: Unable to connect to the database.")

# Update patient medical history (only accessible by doctors or nurses)
def update_medical_history(patient_id, medical_history):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Check if the patient exists before updating
            cursor.execute("SELECT * FROM Patient WHERE Patient_ID = ?", (patient_id,))
            patient = cursor.fetchone()

            if patient is None:
                print("Patient not found.")
                return

            cursor.execute('''
                UPDATE Patient SET Medical_History = ? WHERE Patient_ID = ?
            ''', (medical_history, patient_id))
            conn.commit()

            if cursor.rowcount > 0:
                print("Medical history updated successfully!")
            else:
                print("Failed to update medical history.")
        except sqlite3.Error as e:
            print(f"An error occurred while updating medical history: {e}")
        finally:
            conn.close()  # Ensure connection is closed
    else:
        print("Error: Unable to connect to the database.")

def view_my_prescriptions(user_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Fetch patient ID from User ID
            cursor.execute("SELECT Patient_ID FROM Patient WHERE User_ID = ?", (user_id,))
            patient = cursor.fetchone()

            if patient:
                patient_id = patient[0]
                # Call the function to view prescriptions for this patient
                view_prescriptions_for_patient(patient_id)
            else:
                print("No patient details found for this user.")
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            conn.close()

# Delete a patient (only accessible by authorized roles like Manager)


def delete_patient(patient_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Check if the patient exists before deletion
            cursor.execute("SELECT * FROM Patient WHERE Patient_ID = ?", (patient_id,))
            patient = cursor.fetchone()

            if patient is None:
                print("Patient not found.")
                return

            # Fetch the associated User_ID for the patient (make sure this is the correct column index)
            user_id = patient[7]  # Update if necessary

            # Check if the user associated with the patient exists before attempting to delete
            cursor.execute("SELECT * FROM User WHERE User_ID = ?", (user_id,))
            user = cursor.fetchone()

            if user:
                # Delete the patient record first
                cursor.execute("DELETE FROM Patient WHERE Patient_ID = ?", (patient_id,))
                patient_deleted = cursor.rowcount  # Check if the patient was successfully deleted

                if patient_deleted > 0:
                    conn.commit()  # Commit after patient deletion
                    print("Patient deleted successfully!")

                    # Now delete the associated user from the User table
                    cursor.execute("DELETE FROM User WHERE User_ID = ?", (user_id,))
                    user_deleted = cursor.rowcount  # Check if the user was successfully deleted

                    if user_deleted > 0:
                        conn.commit()  # Commit after user deletion
                        print("Associated user deleted successfully!")
                    else:
                        print("Error: Failed to delete the associated user.")
                else:
                    print("Error: Failed to delete patient.")
            else:
                # If no user found, still delete the patient
                cursor.execute("DELETE FROM Patient WHERE Patient_ID = ?", (patient_id,))
                conn.commit()  # Commit the patient deletion
                print(f"Patient deleted, but associated user (User_ID: {user_id}) not found in the database.")

        except sqlite3.Error as e:
            print(f"An error occurred while deleting patient: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")

# Patient Menu with booking and viewing appointments
def patient_menu(user_id):
    while True:
        print("**********Welcome to Hospital Management System**********")
        print("\nPatient Menu:")
        print("1. View My Details")
        print("2. Update My Details")
        print("3. Book an Appointment")
        print("4. View My Appointments")
        print("5. Back to Main Menu")

        choice = input("Enter choice: ")

        if choice == "1":
            view_patient(user_id)

        elif choice == "2":
            name = input("Enter new name (or press Enter to skip): ")
            address = input("Enter new address (or press Enter to skip): ")
            contact_number = input("Enter new contact number (or press Enter to skip): ")
            dob = input("Enter new date of birth (or press Enter to skip): ")
            gender = input("Enter new gender (or press Enter to skip): ")
            update_patient(user_id, name, address, contact_number, dob, gender)

        elif choice == "3":
            doctor_id = input("Enter the Doctor ID to book an appointment with: ")
            appointment_date = input("Enter the appointment date (YYYY-MM-DD): ")
            reason = input("Enter the reason for appointment: ")
            create_appointment(user_id, doctor_id, appointment_date, reason)

        elif choice == "4":
            view_appointments_for_patient(user_id)

        elif choice == "5":
            return  # Back to main menu

        else:
            print("Invalid choice. Try again.")
# View all patients (by Manager/Admin)
def view_all_patients():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Fetch all patient details
            cursor.execute("SELECT * FROM Patient")
            patients = cursor.fetchall()

            if patients:
                print("All Patients:")
                for patient in patients:
                    print(f"ID: {patient[0]}, Name: {patient[1]}, Address: {patient[2]}, Contact: {patient[3]}, DOB: {patient[4]}, Gender: {patient[5]}")
            else:
                print("No patients found.")
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            conn.close()  # Ensure connection is closed
    else:
        print("Error: Unable to connect to the database.")


def get_patient_id_by_user_id(user_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT Patient_ID FROM Patient
                WHERE User_ID = ?
            ''', (user_id,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                print("Error: No patient found for this user ID.")
                return None
        except sqlite3.Error as e:
            print(f"An error occurred while fetching patient ID: {e}")
            return None
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")
        return None