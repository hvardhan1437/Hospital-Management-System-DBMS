import sqlite3
from db_setup import create_connection

# Add a new room
def add_room(room_number, room_type):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Check if the room number already exists
            cursor.execute("SELECT Room_ID FROM Room WHERE Room_Number = ?", (room_number,))
            existing_room = cursor.fetchone()

            if existing_room:
                print("Error: Room number already exists. Please choose a different room number.")
                return

            # Insert room into Room table
            cursor.execute('''
                INSERT INTO Room (Room_Number, Room_Type, Is_Assigned)
                VALUES (?, ?, 0)
            ''', (room_number, room_type))

            conn.commit()
            print("Room added successfully!")
        except sqlite3.Error as e:
            print(f"An error occurred while adding room: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")

# Assign a room to a patient
from datetime import datetime

def assign_room(patient_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Check if the patient exists
            cursor.execute('''
                SELECT Name FROM Patient WHERE Patient_ID = ?
            ''', (patient_id,))
            patient = cursor.fetchone()

            if not patient:
                print("Invalid Patient ID. No such patient exists.")
                return

            print(f"Assigning a room for Patient ID: {patient_id}, Name: {patient[0]}")

            # Fetch available rooms
            cursor.execute('''
                SELECT Room_ID, Room_Number, Room_Type FROM Room WHERE Is_Assigned = 0
            ''')
            available_rooms = cursor.fetchall()

            if available_rooms:
                print("Available Rooms:")
                for room in available_rooms:
                    print(f"Room ID: {room[0]}, Number: {room[1]}, Type: {room[2]}")

                # Prompt for room ID with validation
                while True:
                    try:
                        room_id = int(input("Enter Room ID to assign to the patient: "))
                        # Validate if the entered room_id exists in the available_rooms list
                        if any(room[0] == room_id for room in available_rooms):
                            break
                        else:
                            print("Invalid Room ID. Please choose a valid room from the list above.")
                    except ValueError:
                        print("Invalid input. Please enter a numeric Room ID.")

                # Prompt for admission date and validate the format
                while True:
                    admission_date = input("Enter admission date (YYYY-MM-DD): ")
                    if validate_date(admission_date):
                        break

                # Assign the room to the patient
                cursor.execute('''
                    INSERT INTO Patient_Room (Patient_ID, Room_ID, Admission_Date)
                    VALUES (?, ?, ?)
                ''', (patient_id, room_id, admission_date))

                # Mark room as assigned
                cursor.execute('''
                    UPDATE Room SET Is_Assigned = 1 WHERE Room_ID = ?
                ''', (room_id,))
                conn.commit()
                print("Room assigned to the patient successfully!")
            else:
                print("No available rooms.")
        except sqlite3.Error as e:
            print(f"An error occurred while assigning room: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")

def validate_date(date_text):
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        print("Invalid date format. Please enter in YYYY-MM-DD format.")
        return False

# Release a room when a patient no longer needs it
def release_room(patient_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Get the current room of the patient where the discharge date is not set
            cursor.execute('''
                SELECT Room.Room_ID, Room.Room_Number, Patient_Room.Discharge_Date 
                FROM Room
                JOIN Patient_Room ON Room.Room_ID = Patient_Room.Room_ID
                WHERE Patient_Room.Patient_ID = ? AND Patient_Room.Discharge_Date IS NULL
            ''', (patient_id,))
            room = cursor.fetchone()

            if room:
                discharge_date = input("Enter discharge date (YYYY-MM-DD): ")

                # Validate the discharge date format
                if not validate_date(discharge_date):
                    return

                # Update the discharge date in Patient_Room table
                cursor.execute('''
                    UPDATE Patient_Room SET Discharge_Date = ? WHERE Patient_ID = ? AND Room_ID = ?
                ''', (discharge_date, patient_id, room[0]))

                # Mark the room as unassigned
                cursor.execute('''
                    UPDATE Room SET Is_Assigned = 0 WHERE Room_ID = ?
                ''', (room[0],))

                conn.commit()
                print(f"Room {room[1]} released successfully!")
            else:
                print("This patient is not currently assigned to any room or the room has already been released.")
        except sqlite3.Error as e:
            print(f"An error occurred while releasing the room: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")



# View all available rooms
def view_available_rooms():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT Room_Number, Room_Type FROM Room WHERE Is_Assigned = 0
            ''')
            available_rooms = cursor.fetchall()

            if available_rooms:
                print("Available Rooms:")
                for room in available_rooms:
                    print(f"Room Number: {room[0]}, Type: {room[1]}")
            else:
                print("No available rooms.")
        except sqlite3.Error as e:
            print(f"An error occurred while fetching available rooms: {e}")
        finally:
            conn.close()

# View assigned rooms
def view_assigned_rooms():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT Patient.Patient_ID, Patient.Name, Room.Room_Number, Room.Room_Type
                FROM Patient
                JOIN Patient_Room ON Patient.Patient_ID = Patient_Room.Patient_ID
                JOIN Room ON Room.Room_Number = Patient_Room.Room_ID
            ''')
            assigned_rooms = cursor.fetchall()

            if assigned_rooms:
                print("Assigned Rooms:")
                for patient_id, patient_name, room_number, room_type in assigned_rooms:
                    print(f"Patient ID: {patient_id}, Name: {patient_name}, Room: {room_number} ({room_type})")
            else:
                print("No rooms are currently assigned.")
        except sqlite3.Error as e:
            print(f"An error occurred while fetching assigned rooms: {e}")
        finally:
            conn.close()

def view_room_assignments():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT Patient.Patient_ID, Patient.Name, Room.Room_Number, Room.Room_Type, 
                       Patient_Room.Admission_Date, Patient_Room.Discharge_Date
                FROM Patient
                JOIN Patient_Room ON Patient.Patient_ID = Patient_Room.Patient_ID
                JOIN Room ON Room.Room_ID = Patient_Room.Room_ID
            ''')
            assignments = cursor.fetchall()

            if assignments:
                print("Room Assignments:")
                for patient_id, patient_name, room_number, room_type, admission_date, discharge_date in assignments:
                    print(f"Patient ID: {patient_id}, Name: {patient_name}, Room: {room_number} ({room_type}), "
                          f"Admission: {admission_date}, Discharge: {discharge_date if discharge_date else 'N/A'}")
            else:
                print("No room assignments found.")
        except sqlite3.Error as e:
            print(f"An error occurred while fetching room assignments: {e}")
        finally:
            conn.close()
