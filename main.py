import sqlite3
from user_auth import signup, login
from patient_module import create_patient, view_patient, update_patient, delete_patient, view_all_patients,view_my_prescriptions
from doctor_module import add_doctor, view_doctor, delete_doctor, view_all_doctors, update_medical_history, view_patients_in_department,get_doctor_id_by_user_id
from department_module import create_department, view_department, assign_department_head, view_all_departments
from appointment_module import create_appointment, view_appointments_for_patient, view_appointments_for_doctor
from manager_module import create_manager, view_manager, update_manager
from db_setup import create_connection, create_all_tables
from lab_technician_module import add_lab_technician, view_all_lab_technicians
from lab_test_module import assign_lab_test, view_lab_tests_for_patient, record_lab_test_result
from room_module import add_room, assign_room, release_room, view_available_rooms, view_assigned_rooms,view_room_assignments
from prescription_module import add_prescription, view_prescriptions_for_patient,prescription_exists,view_all_prescriptions,view_prescriptions_for_patient
from pharmacy_module import add_medicine,dispense_medicine,view_pharmacy_transactions,view_available_medicines,medicine_exists
from billing_module import update_payment_status, view_bills, create_bill,display_all_patients,view_my_bills,generate_bill,view_and_pay_bills,pay_bill

def get_patient_id_by_user_id(user_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Patient_ID FROM Patient WHERE User_ID = ?", (user_id,))
            result = cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            print(f"An error occurred while fetching patient ID: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")
    return None


# Delete the user from the User table after deleting the patient or doctor
def delete_user(user_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM User WHERE User_ID = ?", (user_id,))
            conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while deleting user: {e}")
        finally:
            conn.close()
def doctor_menu(user_id): 
    doctor_id = get_doctor_id_by_user_id(user_id)
    if doctor_id is None:
        return
     
    while True:
        print("\nDoctor Menu:")
        print("1. Update Patient Medical History")
        print("2. View My Appointments")
        print("3. Assign Lab Test to Patient")
        print("4. View Lab Results for Patient")
        print("5. Add Prescription for Patient")
        print("6. View Prescriptions for Patient")
        print("7. View Patient Details")
        print("8. Back to Main Menu")

        choice = input("Enter choice: ")

        if choice == "1":
            if not display_all_patients():
                return
            patient_id = input("Enter Patient ID: ")
            medical_history = input("Enter new medical history: ")
            update_medical_history(patient_id, medical_history)

        elif choice == "2":
            
            view_appointments_for_doctor(user_id)

        elif choice == "3":
            test_name = input("Enter Lab Test Name: ")
            if not display_all_patients():
                return
            patient_id = input("Enter Patient ID: ")

            
            technician_id = 1 
            print(f"Lab Test will be assigned to the predefined technician (ID: {technician_id}).")

            test_date = input("Enter test date (YYYY-MM-DD): ")
            
            assign_lab_test(test_name, patient_id, doctor_id, test_date)

        elif choice == "4":
            if not display_all_patients():
                return
            patient_id = input("Enter Patient ID to view lab results: ")
            view_lab_tests_for_patient(patient_id)

        elif choice == "5":
            if not display_all_patients():
                return
            
            patient_id = input("Enter Patient ID: ")
            if not patient_exists(patient_id):
                print("Error: Invalid Patient ID. Please select a valid patient.")
                return

            print("Available Medicines:")
            medicines_available = view_available_medicines()

            if not medicines_available:
                print("No medicines available in the inventory. Returning to Doctor Menu.")
                continue

            medicine_id = input("Enter Medicine ID: ")
            if not medicine_exists(medicine_id):
                print("Error: Invalid Medicine ID. Please select a valid medicine.")
                continue

            while True:
                try:
                    dosage = input("Enter Dosage (numeric only): ")
                    int(dosage)
                    break
                except ValueError:
                    print("Error: Dosage must be a numeric value.")
            duration = input("Enter Duration: ")
            instructions = input("Enter any instructions (optional): ")
            prescription_date = input("Enter the prescription date (YYYY-MM-DD): ")

            
            add_prescription(doctor_id, patient_id, medicine_id, dosage, duration, instructions, prescription_date)

        elif choice == "6":
            if not display_all_patients():
                return
            patient_id = input("Enter Patient ID to view prescriptions: ")
            view_prescriptions_for_patient(patient_id)

        elif choice == "7":
            if not display_all_patients():
                return
            patient_id = input("Enter Patient ID to view details: ")
            view_patient(patient_id)

        elif choice == "8":
            break

        else:
            print("Invalid choice, try again.")

# Modified delete_doctor to also remove from User table
def delete_doctor_and_user(doctor_id):
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

            # Fetch the associated User_ID for the doctor
            user_id = doctor[4]  # Assuming User_ID is the fifth column in the Doctor table

            # Delete the doctor from the Doctor table
            cursor.execute("DELETE FROM Doctor WHERE Doctor_ID = ?", (doctor_id,))
            conn.commit()

            # Now delete the associated user from the User table
            cursor.execute("DELETE FROM User WHERE User_ID = ?", (user_id,))
            conn.commit()

            if cursor.rowcount > 0:
                print("Doctor and associated user deleted successfully!")
            else:
                print("Doctor deleted, but associated user not found.")
        except sqlite3.Error as e:
            print(f"An error occurred while deleting doctor: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")


# Display available departments and doctors for appointment booking
def display_departments_and_doctors():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()

            cursor.execute('''
                SELECT Department.Department_ID, Department.Department_Name, Doctor.Doctor_ID, Doctor.Name
                FROM Department
                LEFT JOIN Doctor ON Department.Department_ID = Doctor.Department_ID
            ''')
            results = cursor.fetchall()

            if results:
                print("Available Departments and Doctors:")
                for department_id, department_name, doctor_id, doctor_name in results:
                    if doctor_id:
                        print(f"Department: {department_name} (ID: {department_id}) - Doctor: {doctor_name} (ID: {doctor_id})")
                    else:
                        print(f"Department: {department_name} (ID: {department_id}) - No Doctors Assigned")
            else:
                print("No departments or doctors found.")
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            conn.close()


# Function to reset the database (delete all records from tables)
def reset_database():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = OFF;")
            cursor.execute("DELETE FROM Appointment")
            cursor.execute("DELETE FROM Patient")
            cursor.execute("DELETE FROM Doctor")
            cursor.execute("DELETE FROM Department")
            cursor.execute("DELETE FROM User")
            cursor.execute("DELETE FROM Billing")
            cursor.execute("DELETE FROM Pharmacy_Transaction")
            cursor.execute("DELETE FROM Medicine")
            cursor.execute("DELETE FROM Prescription")
            conn.commit()
            cursor.execute("PRAGMA foreign_keys = ON;")
            print("Database reset successfully! All records have been deleted.")
        except sqlite3.Error as e:
            print(f"An error occurred while resetting the database: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")


# Function to check if patient details exist for a user
def check_and_create_patient_details(user_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Patient WHERE User_ID = ?", (user_id,))
            patient = cursor.fetchone()
            conn.close()

            if patient is None:
                print("Please enter your patient details:")
                name = input("Enter name: ")
                address = input("Enter address: ")
                contact_number = input("Enter contact number: ")
                dob = input("Enter date of birth (YYYY-MM-DD): ")
                gender = input("Enter gender: ")
                medical_history = input("Enter medical history: ")
                create_patient(name, address, contact_number, dob, gender, medical_history, user_id)
            else:
                print("Patient details already exist.")
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
    else:
        print("Error: Unable to connect to the database.")

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
    return False

# Function to check if a patient exists by patient_id
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
    return False
# Book an appointment by displaying departments and doctors
def book_appointment(patient_id):
    # Display departments and doctors first
    display_departments_and_doctors()

    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Validate Department ID
            department_id = input("Enter Department ID: ")
            cursor.execute("SELECT Department_ID FROM Department WHERE Department_ID = ?", (department_id,))
            department = cursor.fetchone()

            if not department:
                print("Error: Invalid Department ID.")
                conn.close()
                return  # Exit the function if Department ID is invalid

            # Validate Doctor ID and check if the doctor is in the selected department
            doctor_id = input("Enter Doctor ID from the selected department: ")
            cursor.execute("SELECT Doctor_ID FROM Doctor WHERE Doctor_ID = ? AND Department_ID = ?", (doctor_id, department_id))
            doctor = cursor.fetchone()

            if not doctor:
                print("Error: Invalid Doctor ID or Doctor does not belong to the selected department.")
                conn.close()
                return  # Exit the function if Doctor ID is invalid or not in the department

            # Validate if the patient exists
            if not patient_exists(patient_id):
                print("Error: Patient not found. Cannot create appointment.")
                conn.close()
                return

            # If all validations pass, proceed to gather remaining information
            appointment_date = input("Enter appointment date (YYYY-MM-DD): ")
            reason = input("Enter reason for appointment: ")

            # Create the appointment using the provided doctor ID and patient ID
            create_appointment(patient_id, doctor_id, appointment_date, reason)
        except sqlite3.Error as e:
            print(f"An error occurred while booking the appointment: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")

# Menu for Patient
def patient_menu(user_id):
    while True:
        print("\nPatient Menu:")
        print("1. View My Details")
        print("2. Update My Details")
        print("3. View My Appointments")
        print("4. Book Appointment")
        print("5. View My Bills")
        print("6. Pay My Bills")
        print("7. View My Lab Tests")
        print("8. View My Prescriptions")
        print("9. Back to Main Menu")

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
            view_appointments_for_patient(user_id)

        elif choice == "4":
            # Retrieve the Patient_ID from the Patient table using the User_ID
            conn = create_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT Patient_ID FROM Patient WHERE User_ID = ?", (user_id,))
                patient = cursor.fetchone()
                if patient:
                    patient_id = patient[0]  # Get the Patient_ID
                    book_appointment(patient_id)  # Now pass the correct Patient_ID
                else:
                    print("Error: Patient not found.")
                conn.close()
        elif choice == "5":
            patient_id = get_patient_id_by_user_id(user_id)
            if patient_id is not None:
                view_bills(patient_id)

        elif choice=="6":
            patient_id = get_patient_id_by_user_id(user_id)
            if patient_id is not None:
                view_bills(patient_id)
                pay_bill(patient_id)


        elif choice == "7":
            patient_id = get_patient_id_by_user_id(user_id)
            if patient_id:
                view_lab_tests_for_patient(patient_id)
            else:
                print("Error: Unable to find your patient details.")

        elif choice == "8":
            view_prescriptions_for_patient(user_id)

        elif choice == "9":
            return  # Back to main menu

        else:
            print("Invalid choice. Try again.")

# Function to check if doctor details exist for a user
def check_and_create_doctor_details(doctor_user_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Doctor WHERE User_ID = ?", (doctor_user_id,))
            doctor = cursor.fetchone()

            if doctor is None:
                print("Please enter your doctor details:")
                name = input("Enter name: ")
                specialty = input("Enter specialty: ")
                contact_number = input("Enter contact number: ")

                print("\nAvailable Departments:")
                view_all_departments()  # Display the list of departments for selection
                department_id = input("Enter department ID: ")

                add_doctor(name, specialty, contact_number, department_id, doctor_user_id)
                print("Doctor details added successfully!")
            else:
                print("Doctor details already exist.")
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")

# Menu for Doctor
# Menu for Doctor
def manager_menu(user_id):
    while True:
        print("\nManager Menu:")
        print("1. Create Patient")
        print("2. Delete Patient")
        print("3. Create Doctor")
        print("4. Delete Doctor")
        print("5. View Doctor Details")
        print("6. Manage Departments")
        print("7. View Patient Details")
        print("8. Book Appointment for Patient")
        print("9. View All Doctors")
        print("10. View All Patients")
        print("11. View My Details")
        print("12. Update My Details")
        print("13. Assign Lab Test")
        print("14. View All Lab Technicians")
        print("15. Add Room")
        print("16. Assign Room to Patient")
        print("17. View Available Rooms")
        print("18. View Assigned Rooms")
        print("19. Release Room")
        print("20. View Room Assignments")
        print("21. Add New Medicine")
        print("22. View Available Medicines")
        print("23. Dispense Medicine")
        print("24. View Pharmacy Transactions")
        print("25. Create Bill for Patient")  
        print("26. View Patient Bills")
        print("27. Update Payment Status")
        print("28. Back to Main Menu")

        choice = input("Enter choice: ")

        if choice == "1":
            username = input("Enter new patient's username: ")
            password = input("Enter new patient's password: ")
            user_id = signup(username, password, "Patient")

            if user_id:
                name = input("Enter patient's name: ")
                address = input("Enter patient's address: ")
                contact_number = input("Enter patient's contact number: ")
                dob = input("Enter patient's date of birth (YYYY-MM-DD): ")
                gender = input("Enter patient's gender: ")
                medical_history = input("Enter patient's medical history: ")
                create_patient(name, address, contact_number, dob, gender, medical_history, user_id)

        elif choice == "2":
            patient_id = input("Enter Patient ID to delete: ")
            delete_patient(patient_id)

        elif choice == "3":
            username = input("Enter new doctor's username: ")
            password = input("Enter new doctor's password: ")
            user_id = signup(username, password, "Doctor")

            if user_id:
                name = input("Enter doctor's name: ")
                specialty = input("Enter doctor's specialty: ")
                contact_number = input("Enter doctor's contact number: ")

                print("\nAvailable Departments:")
                view_all_departments()

                department_id = input("Enter department ID for the doctor: ")
                add_doctor(name, specialty, contact_number, department_id, user_id)

        elif choice == "4":
            doctor_id = input("Enter Doctor ID to delete: ")
            delete_doctor_and_user(doctor_id)

        elif choice == "5":
            doctor_id = input("Enter Doctor ID to view details: ")
            view_doctor(doctor_id)

        elif choice == "6":
            print("\nManage Departments:")
            print("1. Create Department")
            print("2. View Department")
            print("3. Assign Department Head")
            print("4. View All Departments")
            dept_choice = input("Enter choice: ")

            if dept_choice == "1":
                department_name = input("Enter Department Name: ")
                create_department(department_name)
            elif dept_choice == "2":
                department_id = input("Enter Department ID: ")
                view_department(department_id)
            elif dept_choice == "3":
                department_id = input("Enter Department ID: ")
                doctor_id = input("Enter Doctor ID to assign as head: ")
                assign_department_head(department_id, doctor_id)
            elif dept_choice == "4":
                view_all_departments()
            else:
                print("Invalid choice.")

        elif choice == "7":
            patient_id = input("Enter Patient ID to view details: ")
            view_patient(patient_id)

        elif choice == "8":
            display_departments_and_doctors()
            patient_id = input("Enter Patient ID: ")
            department_id = input("Select Department ID: ")
            doctor_id = input("Enter Doctor ID: ")
            appointment_date = input("Enter appointment date (YYYY-MM-DD): ")
            reason = input("Enter reason for appointment: ")
            create_appointment(patient_id, doctor_id, appointment_date, reason)

        elif choice == "9":
            view_all_doctors()

        elif choice == "10":
            view_all_patients()

        elif choice == "11":
            view_manager(user_id)

        elif choice == "12":
            name = input("Enter new name (or press Enter to skip): ")
            contact_number = input("Enter new contact number (or press Enter to skip): ")
            dob = input("Enter new date of birth (or press Enter to skip): ")
            update_manager(user_id, name, contact_number, dob)

        elif choice == "13":
            test_name = input("Enter Test Name: ")
            assign_lab_test(test_name)

        elif choice == "14":
            print("Only one predefined lab technician exists in the system.")

        elif choice == "15":
            room_number = input("Enter Room Number: ")
            room_type = input("Enter Room Type (ICU/General/Private): ")
            add_room(room_number, room_type)

        elif choice == "16":
            patient_id = input("Enter Patient ID to assign a room: ")
            assign_room(patient_id)

        elif choice == "17":
            view_available_rooms()

        elif choice == "18":
            view_assigned_rooms()

        elif choice == "19":
            patient_id = input("Enter Patient ID to release their room: ")
            release_room(patient_id)

        elif choice == "20":
            view_room_assignments()

        elif choice == "21":
            medicine_name = input("Enter medicine name: ")
            medicine_type = input("Enter medicine type: ")

            # Validate quantity input
            while True:
                try:
                    quantity = int(input("Enter quantity (numeric value only): "))
                    break
                except ValueError:
                    print("Error: Please enter a valid numeric quantity (e.g., 500).")

            # Validate price input
            while True:
                try:
                    price = float(input("Enter price (numeric value only, e.g., 10.5): "))
                    break
                except ValueError:
                    print("Error: Please enter a valid numeric price (e.g., 10 or 10.5).")

            add_medicine(medicine_name, medicine_type, quantity, price)

        elif choice == "22":
            view_available_medicines()

        elif choice == "23":
            print("Available Prescriptions:")

            if not view_all_prescriptions():
                print("No prescriptions found. Returning to menu.")
                continue
    
            
            prescription_id = input("Enter Prescription ID: ")

            if not prescription_exists(prescription_id): 
                print("Error: Prescription ID not found. Please enter a valid prescription ID.")
                continue

            print("Available Medicines:")
            if not view_available_medicines():
                print("No medicines available in the inventory. Returning to menu.")
                continue

            medicine_id = input("Enter Medicine ID: ")

            if not medicine_exists(medicine_id):
                print("Error: Medicine ID not found. Please enter a valid medicine ID.")
                continue

            try:
                quantity = int(input("Enter quantity: "))
            except ValueError:
                print("Error: Please enter a valid numeric quantity.")
                continue
            try:
                dispense_medicine(prescription_id, medicine_id, quantity)
            except sqlite3.Error as e:
                print(f"An error occurred while dispensing medicine: {e}")

            
        elif choice == "24":
            display_all_patients()
            patient_id = input("Enter Patient ID to view pharmacy transactions: ")
            view_pharmacy_transactions(patient_id)

        elif choice == "25":

            if not display_all_patients():
                return
            
            patient_id = input("Enter Patient ID: ")

            if not patient_exists(patient_id):
                print("Error: Invalid Patient ID. Please select a valid patient.")
                return
            
            print("Available Prescriptions for All Patients:")
            if not view_all_prescriptions():
                print("No prescriptions found for billing.")
                return
            
            try:
                prescription_id = int(input("Enter Prescription ID to generate bill: "))
                if not prescription_exists(prescription_id):
                    print("Error: Invalid Prescription ID. Please select a valid prescription.")
                    return
            except ValueError:
                print("Error: Please enter a valid numeric Prescription ID.")
                return
            
            generate_bill(patient_id, prescription_id)


            
        elif choice == "26":
            if not display_all_patients():
                return
            patient_id = input("Enter Patient ID to view bills: ")
            view_bills(patient_id)

        elif choice == "27":
            bill_id = input("Enter Bill ID to update: ")
            new_status = input("Enter new payment status (Paid/Unpaid): ")
            update_payment_status(bill_id, new_status)

        elif choice == "28":
            break

        else:
            print("Invalid choice, try again.")
# Main function to handle login and direct users to their respective menus
def main():
    print("Welcome to the Hospital Management System!")

    while True:
        print("\n1. Signup")
        print("2. Login")
        print("3. Reset Database")
        print("4. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            username = input("Enter username: ")
            password = input("Enter password: ")
            role = input("Enter role (Patient/Doctor/Manager): ")
            user_id = signup(username, password, role)

            if user_id and role == "Patient":
                check_and_create_patient_details(user_id)
            elif user_id and role == "Manager":
                name = input("Enter your name: ")
                contact_number = input("Enter contact number: ")
                dob = input("Enter date of birth (YYYY-MM-DD): ")
                create_manager(name, contact_number, dob, user_id)

        elif choice == "2":
            username = input("Enter username: ")
            password = input("Enter password: ")
            result = login(username, password)

            if result:
                user_id, role = result
                print(f"Logged in as {role} (User ID: {user_id})")

                if role == "Patient":
                    check_and_create_patient_details(user_id)
                    patient_menu(user_id)
                elif role == "Doctor":
                    check_and_create_doctor_details(user_id)
                    doctor_menu(user_id)
                elif role == "Manager":
                    manager_menu(user_id)
                else:
                    print(f"Role {role} not supported for this menu.")

        elif choice == "3":
            reset_database()
            

        elif choice == "4":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
