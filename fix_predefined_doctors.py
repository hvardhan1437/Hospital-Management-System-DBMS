import sqlite3
from hashlib import sha256

def create_connection():
    return sqlite3.connect('hospital_management.db')

def hash_password(password):
    return sha256(password.encode()).hexdigest()

def create_user(username, password, role):
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO User (Username, Password, Role)
                VALUES (?, ?, ?)
            ''', (username, hash_password(password), role))
            conn.commit()
            return cursor.lastrowid  # Return the new User_ID
        except sqlite3.Error as e:
            print(f"Error creating user: {e}")
        finally:
            conn.close()

def update_doctor_user_id(doctor_id, user_id):
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE Doctor
                SET User_ID = ?
                WHERE Doctor_ID = ?
            ''', (user_id, doctor_id))
            conn.commit()
            print(f"Doctor ID {doctor_id} updated with User ID {user_id}")
        except sqlite3.Error as e:
            print(f"Error updating doctor: {e}")
        finally:
            conn.close()

def fix_predefined_doctors():
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT Doctor_ID, Name FROM Doctor WHERE User_ID IS NULL')
            doctors = cursor.fetchall()
            for doctor_id, name in doctors:
                username = f'doctor{name.lower().replace(" ", "_")}'
                password = 'defaultpassword'
                user_id = create_user(username, password, 'Doctor')
                if user_id:
                    update_doctor_user_id(doctor_id, user_id)
        except sqlite3.Error as e:
            print(f"Error fetching doctors: {e}")
        finally:
            conn.close()

# Run the script
fix_predefined_doctors()
