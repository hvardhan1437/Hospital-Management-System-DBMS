import sqlite3
from db_setup import create_connection

# Create a new manager (only accessible during signup)
def create_manager(name, contact_number, dob, user_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO Manager (Name, Contact_Number, Date_of_Birth, User_ID)
                VALUES (?, ?, ?, ?)
            ''', (name, contact_number, dob, user_id))

            conn.commit()
            print("Manager created successfully!")
        except sqlite3.Error as e:
            print(f"An error occurred while creating the manager: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")

# View manager details
def view_manager(user_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Manager WHERE User_ID = ?", (user_id,))
            manager = cursor.fetchone()

            if manager:
                print(f"Manager Details:\nID: {manager[0]}, Name: {manager[1]}, Contact: {manager[2]}, DOB: {manager[3]}")
            else:
                print("Manager not found.")
        except sqlite3.Error as e:
            print(f"An error occurred while fetching manager details: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")

# Update manager details
def update_manager(user_id, name=None, contact_number=None, dob=None):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Build the update query dynamically
            update_fields = []
            update_values = []

            if name:
                update_fields.append("Name = ?")
                update_values.append(name)
            if contact_number:
                update_fields.append("Contact_Number = ?")
                update_values.append(contact_number)
            if dob:
                update_fields.append("Date_of_Birth = ?")
                update_values.append(dob)

            if update_fields:
                update_values.append(user_id)
                query = f"UPDATE Manager SET {', '.join(update_fields)} WHERE User_ID = ?"
                cursor.execute(query, update_values)
                conn.commit()
                print("Manager details updated successfully!")
            else:
                print("No details provided to update.")
        except sqlite3.Error as e:
            print(f"An error occurred while updating manager details: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")
