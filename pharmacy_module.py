import sqlite3
from db_setup import create_connection

# Add a new medicine to the pharmacy stock
def add_medicine(medicine_name, medicine_type, quantity, price):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Insert medicine into the Medicine table
            cursor.execute('''
                INSERT INTO Medicine (Medicine_Name, Medicine_Type, Quantity, Price)
                VALUES (?, ?, ?, ?)
            ''', (medicine_name, medicine_type, quantity, price))

            conn.commit()
            print("Medicine added successfully!")
        except sqlite3.Error as e:
            print(f"An error occurred while adding medicine: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")

def medicine_exists(medicine_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Query to check if the medicine exists and has stock
            cursor.execute("SELECT Quantity FROM Medicine WHERE Medicine_ID = ?", (medicine_id,))
            medicine = cursor.fetchone()

            if medicine is None:
                print("Error: Invalid Medicine ID.")
                return False
            elif medicine[0] <= 0:
                print("Selected medicine is out of stock.")
                return False
            else:
                return True  # Medicine exists and is in stock

        except sqlite3.Error as e:
            print(f"An error occurred while checking medicine: {e}")
            return False
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")
        return False


# Dispense medicines to a patient based on a prescription
def dispense_medicine(prescription_id, medicine_id, quantity):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Fetch available quantity and price of the selected medicine
            cursor.execute("SELECT Quantity, Price FROM Medicine WHERE Medicine_ID = ?", (medicine_id,))
            medicine = cursor.fetchone()

            if medicine:
                available_quantity, price_per_unit = medicine

                # Check if requested quantity is available
                if available_quantity >= quantity:
                    total_price = price_per_unit * quantity
                    new_quantity = available_quantity - quantity

                    # Update the inventory for the medicine
                    cursor.execute("UPDATE Medicine SET Quantity = ? WHERE Medicine_ID = ?", (new_quantity, medicine_id))

                    # Record the transaction in Pharmacy_Transaction
                    cursor.execute('''
                        INSERT INTO Pharmacy_Transaction (Prescription_ID, Medicine_ID, Quantity, Total_Price, Transaction_Date)
                        VALUES (?, ?, ?, ?, datetime('now'))
                    ''', (prescription_id, medicine_id, quantity, total_price))

                    conn.commit()
                    print(f"Medicine dispensed successfully! Total Price: ${total_price:.2f}")
                else:
                    print("Error: Insufficient stock for the selected medicine.")
            else:
                print("Error: Medicine not found.")
                
        except sqlite3.Error as e:
            print(f"An error occurred while dispensing medicine: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")


def view_available_medicines():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Medicine_ID, Medicine_Name, Medicine_Type, Quantity, Price FROM Medicine")
            medicines = cursor.fetchall()

            if medicines:
                print("Available Medicines:")
                for med in medicines:
                    print(f"ID: {med[0]}, Name: {med[1]}, Type: {med[2]}, Quantity: {med[3]}, Price: {med[4]}")
                return True  # Medicines found
            else:
                print("No medicines available in the inventory.")
                return False  # No medicines found
        except sqlite3.Error as e:
            print(f"An error occurred while retrieving medicines: {e}")
            return False
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")
        return False

# View all pharmacy transactions
def view_pharmacy_transactions(patient_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Fetch all transactions for the specified patient
            cursor.execute('''
                SELECT Pharmacy_Transaction.Transaction_ID, Medicine.Medicine_Name, Pharmacy_Transaction.Quantity, Pharmacy_Transaction.Total_Price, Pharmacy_Transaction.Transaction_Date
                FROM Pharmacy_Transaction
                JOIN Prescription ON Pharmacy_Transaction.Prescription_ID = Prescription.Prescription_ID
                JOIN Medicine ON Pharmacy_Transaction.Medicine_ID = Medicine.Medicine_ID
                WHERE Prescription.Patient_ID = ?
            ''', (patient_id,))
            transactions = cursor.fetchall()

            if transactions:
                print(f"Pharmacy Transactions for Patient ID {patient_id}:")
                for transaction in transactions:
                    print(f"Transaction ID: {transaction[0]}, Medicine: {transaction[1]}, Quantity: {transaction[2]}, Total Price: {transaction[3]}, Date: {transaction[4]}")
            else:
                print("No pharmacy transactions found for this patient.")
        except sqlite3.Error as e:
            print(f"An error occurred while fetching pharmacy transactions: {e}")
        finally:
            conn.close()

def check_medicine_availability(medicine_name):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT Medicine_ID, Medicine_Name, Quantity, Price 
                FROM Medicine 
                WHERE Medicine_Name = ?
            ''', (medicine_name,))
            medicine = cursor.fetchone()

            if medicine:
                print(f"Medicine Available: ID: {medicine[0]}, Name: {medicine[1]}, Quantity: {medicine[2]}, Price: {medicine[3]}")
                return medicine
            else:
                print("Medicine not available.")
                return None
        except sqlite3.Error as e:
            print(f"An error occurred while checking medicine availability: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")
