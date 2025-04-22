import sqlite3
import hashlib
from db_setup import create_connection

# Hashing the password using SHA-256 (no salt)
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Signup function
def signup(username, password, role):
    # Ensure valid roles are entered
    valid_roles = ["Patient", "Doctor", "Manager", "Nurse", "Lab Technician", "Hospital Staff"]
    
    if role not in valid_roles:
        print(f"Invalid role. Please choose from: {', '.join(valid_roles)}")
        return None  # Return None to signify failure

    # Optional: Enforce password length and strength
    if len(password) < 8:
        print("Password too short! Please enter at least 8 characters.")
        return None

    try:
        conn = create_connection()
        if conn:
            cursor = conn.cursor()

            # Hash the password using SHA-256
            hashed_password = hash_password(password)

            # Check if the username already exists in the User table
            cursor.execute("SELECT User_ID, Role FROM User WHERE Username = ?", (username,))
            existing_user = cursor.fetchone()

            if existing_user:
                existing_role = existing_user[1]
                print(f"Error: Username '{username}' is already taken by a {existing_role}. Please choose a different username.")
                return None

            # Insert user into the User table with the hashed password
            cursor.execute("""
                INSERT INTO User (Username, Password, Role)
                VALUES (?, ?, ?)
            """, (username, hashed_password, role))

            conn.commit()
            user_id = cursor.lastrowid  # Get the User_ID of the newly inserted user
            print(f"User '{username}' signed up successfully as {role} with User_ID: {user_id}.")

            return user_id  # Return User_ID after successful signup

        else:
            print("Error: Unable to connect to the database.")
            return None  # Return None on database connection error
    
    except sqlite3.IntegrityError:
        print("Error: Username already exists. Please choose a different username.")
        return None  # Return None if signup fails due to duplicate username
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None  # Return None on any other database error
    finally:
        if conn:
            conn.close()  # Ensure the connection is closed

# Delete user from User table (by User_ID)
def delete_user(user_id):
    try:
        conn = create_connection()
        if conn:
            cursor = conn.cursor()

            # Delete the user from the User table
            cursor.execute("DELETE FROM User WHERE User_ID = ?", (user_id,))
            conn.commit()

            if cursor.rowcount > 0:
                print("User deleted successfully from User table!")
            else:
                print("User not found in User table.")

        else:
            print("Error: Unable to connect to the database.")
    
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

# Login function
def login(username, password):
    try:
        conn = create_connection()
        if conn:
            cursor = conn.cursor()

            # Check if user exists
            cursor.execute("SELECT User_ID, Password, Role FROM User WHERE Username = ?", (username,))
            result = cursor.fetchone()

            if result:
                user_id, stored_password, role = result
                # Hash the input password and compare it with the stored hashed password
                if hash_password(password) == stored_password:
                    print(f"Login successful! Welcome, {username}. You are logged in as {role}.")
                    return user_id, role  # Return User_ID and role for further role-based access
                else:
                    print("Invalid password. Please try again.")
                    return None  # Return None for invalid password
            else:
                print("Username not found. Please try again.")
                return None  # Return None if username not found

        else:
            print("Error: Unable to connect to the database.")
            return None  # Return None if there’s a connection issue
    
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None  # Return None on any other database error
    finally:
        if conn:
            conn.close()  # Ensure the connection is closed
