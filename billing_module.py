import sqlite3
from db_setup import create_connection
import sqlite3
from db_setup import create_connection
from pharmacy_module import check_medicine_availability
from patient_module import get_patient_id_by_user_id
# Function to update the payment status of a bill
def update_payment_status(bill_id, new_status):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Check if the bill exists
            cursor.execute("SELECT * FROM Billing WHERE Bill_ID = ?", (bill_id,))
            bill = cursor.fetchone()
            
            if not bill:
                print("Bill not found.")
                return
            
            # Update the payment status of the bill
            cursor.execute('''
                UPDATE Billing
                SET Payment_Status = ?
                WHERE Bill_ID = ?
            ''', (new_status, bill_id))
            conn.commit()

            print("Payment status updated successfully!")
        except sqlite3.Error as e:
            print(f"An error occurred while updating payment status: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")

# Create a new bill for a patient
def create_bill(patient_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Check if there are any prescriptions for this patient
            cursor.execute('''
                SELECT Prescription_ID FROM Prescription
                WHERE Patient_ID = ?
            ''', (patient_id,))
            prescriptions = cursor.fetchall()

            if not prescriptions:
                print(f"No prescriptions found for Patient ID {patient_id}. Cannot generate a bill.")
                return

            # Retrieve prescription-related total from pharmacy transactions
            cursor.execute('''
                SELECT SUM(M.Price * PT.Quantity) AS Total_Amount
                FROM Medicine M
                JOIN Pharmacy_Transaction PT ON M.Medicine_ID = PT.Medicine_ID
                WHERE PT.Prescription_ID IN (
                    SELECT Prescription_ID FROM Prescription WHERE Patient_ID = ?
                )
            ''', (patient_id,))
            total_amount = cursor.fetchone()[0] or 0  # default to 0 if no transactions found

            if total_amount == 0:
                print("No pharmacy transactions available for billing.")
                return

            # Insert bill if valid amount is found
            cursor.execute('''
                INSERT INTO Billing (Patient_ID, Amount, Payment_Status, Billing_Date)
                VALUES (?, ?, 'Unpaid', CURRENT_DATE)
            ''', (patient_id, total_amount))
            
            conn.commit()
            print(f"Bill of ${total_amount:.2f} generated successfully for Patient ID {patient_id}.")

        except sqlite3.Error as e:
            print(f"An error occurred while generating the bill: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")


# View all bills
def view_bills(patient_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT Bill_ID, Amount, Payment_Status, Billing_Date
                FROM Billing
                WHERE Patient_ID = ?
            ''', (patient_id,))
            bills = cursor.fetchall()
            if bills:
                print(f"Bills for Patient ID {patient_id}:")
                for bill in bills:
                    print(f"Bill ID: {bill[0]}, Amount: {bill[1]}, Status: {bill[2]}, Date: {bill[3]}")
            else:
                print(f"No bills found for Patient ID {patient_id}.")
        except sqlite3.Error as e:
            print(f"An error occurred while fetching bills: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")


def display_all_patients():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Patient_ID, Name FROM Patient")
            patients = cursor.fetchall()
            if patients:
                print("Available Patients:")
                for patient in patients:
                    print(f"ID: {patient[0]}, Name: {patient[1]}")
                return True  # Return True if patients exist
            else:
                print("No patients available.")
                return False  # Return False if no patients are available
        except sqlite3.Error as e:
            print(f"An error occurred while retrieving patients: {e}")
            return False
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")
        return False


# Mark a bill as paid
def mark_bill_as_paid(bill_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Update the payment status to 'Paid'
            cursor.execute('''
                UPDATE Billing
                SET Payment_Status = 'Paid'
                WHERE Bill_ID = ?
            ''', (bill_id,))

            conn.commit()

            if cursor.rowcount > 0:
                print("Bill marked as paid successfully!")
            else:
                print("Bill not found.")
        except sqlite3.Error as e:
            print(f"An error occurred while marking the bill as paid: {e}")
        finally:
            conn.close()
def view_my_bills(user_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Fetch the Patient ID using the User ID
            cursor.execute("SELECT Patient_ID FROM Patient WHERE User_ID = ?", (user_id,))
            patient = cursor.fetchone()

            if patient:
                patient_id = patient[0]
                # Retrieve bills for the patient
                cursor.execute('''
                    SELECT Bill_ID, Amount, Payment_Status, Billing_Date
                    FROM Billing
                    WHERE Patient_ID = ?
                ''', (patient_id,))
                bills = cursor.fetchall()

                if bills:
                    print("Your Bills:")
                    for bill in bills:
                        print(f"Bill ID: {bill[0]}, Amount: {bill[1]}, Status: {bill[2]}, Date: {bill[3]}")
                else:
                    print("No bills found.")
            else:
                print("Patient details not found.")
        except sqlite3.Error as e:
            print(f"An error occurred while fetching bills: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")

def check_medicine_availability_by_id(medicine_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Medicine_ID, Medicine_Name, Quantity, Price FROM Medicine WHERE Medicine_ID = ?", (medicine_id,))
            medicine = cursor.fetchone()
            if medicine and medicine[2] > 0:  # Ensure quantity is greater than 0
                return medicine
            else:
                return None
        except sqlite3.Error as e:
            print(f"An error occurred while checking medicine availability: {e}")
            return None
        finally:
            conn.close()

def generate_bill(patient_id, prescription_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Fetch the Medicine_ID from the Prescription
            cursor.execute('''
                SELECT Medicine_ID, Dosage 
                FROM Prescription 
                WHERE Prescription_ID = ?
            ''', (prescription_id,))
            prescription = cursor.fetchone()

            if not prescription:
                print("No prescription found with the given ID.")
                return

            medicine_id, dosage = prescription

            # Check medicine availability
            medicine = check_medicine_availability_by_id(medicine_id)

            if medicine:
                _, medicine_name, available_quantity, price = medicine

                # Calculate total price based on dosage or quantity needed (customizable)
                total_price = price  # Adjust calculation if necessary based on dosage/quantity

                while True:
                    try:
                        amount = float(input("Enter Bill Amount (numeric value only): "))
                        break
                    except ValueError:
                        print("Error: Please enter a valid numeric amount (e.g., 100.5).")

                # Insert the bill into the Billing table
                cursor.execute('''
                    INSERT INTO Billing (Patient_ID, Amount, Payment_Status, Billing_Date)
                    VALUES (?, ?, 'Unpaid', CURRENT_DATE)
                ''', (patient_id, amount))

                conn.commit()
                print("Bill generated successfully!")
            else:
                print("Cannot generate bill as medicine is not available.")

        except sqlite3.Error as e:
            print(f"An error occurred while generating the bill: {e}")
        finally:
            conn.close()


def view_and_pay_bills(user_id):
    patient_id = get_patient_id_by_user_id(user_id)
    if patient_id is None:
        print("Error: Patient not found.")
        return
    
    bills = view_bills(patient_id)
    if not bills:
        print("No bills to pay.")
        return
    
    bill_id = input("Enter Bill ID to pay: ")
    if not bill_exists(bill_id, patient_id):
        print("Error: Invalid Bill ID.")
        return
    
    confirm = input("Confirm payment for Bill ID {}? (yes/no): ".format(bill_id))
    if confirm.lower() == 'yes':
        update_payment_status(bill_id, "Paid")
        print("Bill paid successfully!")
    else:
        print("Payment cancelled.")

def update_payment_status(bill_id, new_status):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE Billing
                SET Payment_Status = ?
                WHERE Bill_ID = ?
            ''', (new_status, bill_id))
            conn.commit()
            print(f"Payment status updated to {new_status} for Bill ID {bill_id}.")
        except sqlite3.Error as e:
            print(f"An error occurred while updating payment status: {e}")
        finally:
            conn.close()
def pay_bill(patient_id):
    bill_id = input("Enter Bill ID to pay: ")
    if not bill_exists(bill_id, patient_id):
        print("Error: Invalid Bill ID.")
        return

    confirm = input(f"Confirm payment for Bill ID {bill_id}? (yes/no): ").lower()
    if confirm == 'yes':
        update_payment_status(bill_id, "Paid")
        print("Bill paid successfully!")
    else:
        print("Payment cancelled.")
def bill_exists(bill_id, patient_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM Billing
                WHERE Bill_ID = ? AND Patient_ID = ?
            ''', (bill_id, patient_id))
            return cursor.fetchone() is not None
        except sqlite3.Error as e:
            print(f"An error occurred while checking bill existence: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")
    return False
