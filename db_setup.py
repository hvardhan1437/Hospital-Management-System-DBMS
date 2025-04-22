import sqlite3

# Connect to SQLite database
def create_connection():
    try:
        conn = sqlite3.connect('hospital_management.db', timeout=10)  
        conn.execute('PRAGMA foreign_keys = ON')  
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to the database: {e}")
        return None
def create_medicine_table():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Medicine (
                    Medicine_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Medicine_Name TEXT NOT NULL,
                    Medicine_Type TEXT,
                    Quantity INTEGER NOT NULL,
                    Price REAL NOT NULL
                );
            ''')
            conn.commit()
            print("Medicine table created successfully!")
        except sqlite3.Error as e:
            print(f"An error occurred while creating the Medicine table: {e}")
        finally:
            conn.close()
    else:
        print("Failed to create the Medicine table due to connection issues.")


def create_pharmacy_transaction_table():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Pharmacy_Transaction (
                    Transaction_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Prescription_ID INTEGER,
                    Medicine_ID INTEGER,
                    Quantity INTEGER NOT NULL,
                    Total_Price REAL NOT NULL,
                    Transaction_Date TEXT,
                    FOREIGN KEY (Prescription_ID) REFERENCES Prescription(Prescription_ID) ON DELETE CASCADE,
                    FOREIGN KEY (Medicine_ID) REFERENCES Medicine(Medicine_ID) ON DELETE CASCADE
                );
            ''')
            conn.commit()
            print("Pharmacy Transaction table created successfully!")
        except sqlite3.Error as e:
            print(f"An error occurred while creating the Pharmacy Transaction table: {e}")
        finally:
            conn.close()
    else:
        print("Failed to create the Pharmacy Transaction table due to connection issues.")

# Create the User table
def create_user_table():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS User (
                User_ID INTEGER PRIMARY KEY,
                Username TEXT NOT NULL UNIQUE,
                Password TEXT NOT NULL,
                Role TEXT NOT NULL
            );
            ''')
            conn.commit()
            print("User table created successfully!")
        except sqlite3.Error as e:
            print(f"Error creating User table: {e}")
        finally:
            conn.close()

# Create the Doctor table with predefined doctors
def create_doctor_table():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS Doctor (
                Doctor_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Name TEXT NOT NULL,
                Specialty TEXT NOT NULL,
                Contact_Number TEXT,
                Department_ID INTEGER,
                User_ID INTEGER,
                FOREIGN KEY (User_ID) REFERENCES User(User_ID) ON DELETE CASCADE
            );
            ''')

            # Check if predefined users exist in the User table
            cursor.execute("SELECT COUNT(*) FROM User WHERE Role = 'Doctor'")
            doctor_user_count = cursor.fetchone()[0]

            if doctor_user_count < 8:
                # Insert predefined users for doctors if they don't exist
                predefined_users = [
                    ('doc1', 'hashed_password1', 'Doctor'),
                    ('doc2', 'hashed_password2', 'Doctor'),
                    ('doc3', 'hashed_password3', 'Doctor'),
                    ('doc4', 'hashed_password4', 'Doctor'),
                    ('doc5', 'hashed_password5', 'Doctor'),
                    ('doc6', 'hashed_password6', 'Doctor'),
                    ('doc7', 'hashed_password7', 'Doctor'),
                    ('doc8', 'hashed_password8', 'Doctor')
                ]

                user_ids = []

                for user in predefined_users:
                    cursor.execute("INSERT INTO User (Username, Password, Role) VALUES (?, ?, ?)", user)
                    user_ids.append(cursor.lastrowid)

                # Predefined doctors with valid User_IDs
                predefined_doctors = [
                    ("Dr. Smith", "Cardiology", "1234567890", 1, user_ids[0]),
                    ("Dr. Johnson", "Neurology", "1234567891", 2, user_ids[1]),
                    ("Dr. Williams", "Oncology", "1234567892", 3, user_ids[2]),
                    ("Dr. Brown", "Pediatrics", "1234567893", 4, user_ids[3]),
                    ("Dr. Jones", "Orthopedics", "1234567894", 5, user_ids[4]),
                    ("Dr. Garcia", "Dermatology", "1234567895", 6, user_ids[5]),
                    ("Dr. Martinez", "General Surgery", "1234567896", 7, user_ids[6]),
                    ("Dr. Davis", "Gastroenterology", "1234567897", 8, user_ids[7])
                ]

                cursor.executemany('''
                INSERT INTO Doctor (Name, Specialty, Contact_Number, Department_ID, User_ID)
                VALUES (?, ?, ?, ?, ?)
                ''', predefined_doctors)

            conn.commit()
            print("Doctor table created with predefined doctors successfully!")
        except sqlite3.Error as e:
            print(f"Error creating Doctor table: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")


def create_department_table():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS Department (
                Department_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Department_Name TEXT NOT NULL,
                Department_Head INTEGER,
                FOREIGN KEY (Department_Head) REFERENCES Doctor(Doctor_ID) ON DELETE SET NULL
            );
            ''')

            # Insert predefined departments if none exist
            cursor.execute("SELECT COUNT(*) FROM Department")
            if cursor.fetchone()[0] == 0:
                predefined_departments = [
                    ("Cardiology", None),
                    ("Neurology", None),
                    ("Oncology", None),
                    ("Pediatrics", None),
                    ("Orthopedics", None),
                    ("Dermatology", None),
                    ("General Surgery", None),
                    ("Gastroenterology", None)
                ]
                cursor.executemany('''
                INSERT INTO Department (Department_Name, Department_Head)
                VALUES (?, ?)
                ''', predefined_departments)

            conn.commit()
            print("Department table created with predefined departments successfully!")
        except sqlite3.Error as e:
            print(f"Error creating Department table: {e}")
        finally:
            conn.close()
    else:
        print("Failed to create the Department table due to connection issues.")
# Alter the Department table to add Department_Head
def add_department_head():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
            ALTER TABLE Department ADD COLUMN Department_Head INTEGER;
            ''')
            cursor.execute('''
            ALTER TABLE Department ADD FOREIGN KEY (Department_Head) REFERENCES Doctor(Doctor_ID) ON DELETE SET NULL;
            ''')
            conn.commit()
            print("Department table altered successfully to include Department_Head.")
        except sqlite3.Error as e:
            print(f"Error adding Department_Head: {e}")
        finally:
            conn.close()

# Create the Patient table
def create_patient_table():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS Patient (
                Patient_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Name TEXT NOT NULL,
                Address TEXT,
                Contact_Number TEXT,
                Date_of_Birth TEXT,
                Gender TEXT,
                Medical_History TEXT,
                User_ID INTEGER,
                FOREIGN KEY (User_ID) REFERENCES User(User_ID) ON DELETE CASCADE
            );
            ''')
            conn.commit()
            print("Patient table created successfully!")
        except sqlite3.Error as e:
            print(f"Error creating Patient table: {e}")
        finally:
            conn.close()

# Create the Lab Technician table
def create_lab_technician_table():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS Lab_Technician (
                Lab_Technician_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Name TEXT NOT NULL,
                Contact_Number TEXT
            );
            ''')
            
            # Insert one predefined lab technician if none exist
            cursor.execute("SELECT COUNT(*) FROM Lab_Technician")
            if cursor.fetchone()[0] == 0:
                predefined_technician = [("LabTech", "1234567890")]
                cursor.executemany('''
                INSERT INTO Lab_Technician (Name, Contact_Number)
                VALUES (?, ?)
                ''', predefined_technician)

            conn.commit()
            print("Lab Technician table created with one predefined lab technician successfully!")
        except sqlite3.Error as e:
            print(f"Error creating Lab Technician table: {e}")
        finally:
            conn.close()
    else:
        print("Failed to create the Lab Technician table due to connection issues.")

# Create the Lab Test table
def create_lab_test_table():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS Lab_Test (
                Lab_Test_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Test_Name TEXT NOT NULL,
                Patient_ID INTEGER,
                Doctor_ID INTEGER,
                Lab_Technician_ID INTEGER,
                Test_Date TEXT,
                Result TEXT,
                FOREIGN KEY (Patient_ID) REFERENCES Patient(Patient_ID) ON DELETE CASCADE,
                FOREIGN KEY (Doctor_ID) REFERENCES Doctor(Doctor_ID) ON DELETE SET NULL,
                FOREIGN KEY (Lab_Technician_ID) REFERENCES Lab_Technician(Lab_Technician_ID) ON DELETE SET NULL
            );
            ''')
            conn.commit()
            print("Lab Test table created successfully!")
        except sqlite3.Error as e:
            print(f"Error creating Lab Test table: {e}")
        finally:
            conn.close()

# Create the Room table
def create_room_table():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('DROP TABLE IF EXISTS Room')
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS Room (
                Room_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Room_Number INTEGER NOT NULL UNIQUE,
                Room_Type TEXT NOT NULL,
                Is_Assigned INTEGER DEFAULT 0
            );
            ''')
            cursor.execute("SELECT COUNT(*) FROM Room")
            if cursor.fetchone()[0] == 0:
                predefined_rooms = [
                    (1, 'ICU', 0),
                    (2, 'ICU', 0),
                    (3, 'General', 0),
                    (4, 'General', 0),
                    (5, 'Private', 0),
                    (6, 'Private', 0)
                ]
                cursor.executemany('''
                INSERT INTO Room (Room_Number, Room_Type, Is_Assigned)
                VALUES (?, ?, ?)
                ''', predefined_rooms)

            conn.commit()
            print("Room table created with predefined rooms successfully!")
        except sqlite3.Error as e:
            print(f"An error occurred while creating the room table: {e}")
        finally:
            conn.close()

# Create the Patient-Room table
def create_patient_room_table():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS Patient_Room (
                Patient_ID INTEGER,
                Room_ID INTEGER,
                FOREIGN KEY (Patient_ID) REFERENCES Patient(Patient_ID) ON DELETE CASCADE,
                FOREIGN KEY (Room_ID) REFERENCES Room(Room_ID) ON DELETE SET NULL
            );
            ''')
            conn.commit()
            print("Patient-Room table created successfully!")
        except sqlite3.Error as e:
            print(f"Error creating Patient-Room table: {e}")
        finally:
            conn.close()
def alter_patient_room_table():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Check if the columns already exist
            cursor.execute("PRAGMA table_info(Patient_Room);")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]  # Get the column names from the table schema

            # Add Admission_Date column if it doesn't exist
            if 'Admission_Date' not in column_names:
                cursor.execute("ALTER TABLE Patient_Room ADD COLUMN Admission_Date TEXT")
                print("Admission_Date column added to Patient_Room table.")
            else:
                print("Admission_Date column already exists.")

            # Add Discharge_Date column if it doesn't exist
            if 'Discharge_Date' not in column_names:
                cursor.execute("ALTER TABLE Patient_Room ADD COLUMN Discharge_Date TEXT")
                print("Discharge_Date column added to Patient_Room table.")
            else:
                print("Discharge_Date column already exists.")

            conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while altering Patient_Room table: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")

# Create the Appointment table
def create_appointment_table():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS Appointment (
                Appointment_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Patient_ID INTEGER,
                Doctor_ID INTEGER,
                Appointment_Date TEXT NOT NULL,
                Reason TEXT,
                FOREIGN KEY (Patient_ID) REFERENCES Patient(Patient_ID) ON DELETE CASCADE,
                FOREIGN KEY (Doctor_ID) REFERENCES Doctor(Doctor_ID) ON DELETE CASCADE
            );
            ''')
            conn.commit()
            print("Appointment table created successfully!")
        except sqlite3.Error as e:
            print(f"Error creating Appointment table: {e}")
        finally:
            conn.close()

# Create the Manager table
def create_manager_table():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS Manager (
                Manager_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Name TEXT NOT NULL,
                Contact_Number TEXT,
                Date_of_Birth TEXT,
                User_ID INTEGER,
                FOREIGN KEY (User_ID) REFERENCES User(User_ID) ON DELETE CASCADE
            );
            ''')
            conn.commit()
            print("Manager table created successfully!")
        except sqlite3.Error as e:
            print(f"Error creating Manager table: {e}")
        finally:
            conn.close()

# Drop all tables
def drop_tables():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = OFF;")
            cursor.execute("DROP TABLE IF EXISTS Appointment")
            cursor.execute("DROP TABLE IF EXISTS Lab_Test")
            cursor.execute("DROP TABLE IF EXISTS Patient_Room")
            cursor.execute("DROP TABLE IF EXISTS Room")
            cursor.execute("DROP TABLE IF EXISTS Lab_Technician")
            cursor.execute("DROP TABLE IF EXISTS Doctor")
            cursor.execute("DROP TABLE IF EXISTS Department")
            cursor.execute("DROP TABLE IF EXISTS Patient")
            cursor.execute("DROP TABLE IF EXISTS Manager")
            cursor.execute("DROP TABLE IF EXISTS User")
            cursor.execute("PRAGMA foreign_keys = ON;")
            conn.commit()
            print("All tables dropped successfully!")
        except sqlite3.Error as e:
            print(f"An error occurred while dropping tables: {e}")
        finally:
            conn.close()
# Add foreign keys after all tables are created
def add_foreign_keys():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Add Department foreign key to Doctor table
            cursor.execute('''
            ALTER TABLE Doctor
            ADD CONSTRAINT fk_doctor_department
            FOREIGN KEY (Department_ID) REFERENCES Department(Department_ID) ON DELETE SET NULL;
            ''')

            # Add Doctor foreign key to Department table (for Department Head)
            cursor.execute('''
            ALTER TABLE Department
            ADD CONSTRAINT fk_department_head
            FOREIGN KEY (Department_Head) REFERENCES Doctor(Doctor_ID) ON DELETE SET NULL;
            ''')

            conn.commit()
            print("Foreign keys added successfully!")
        except sqlite3.Error as e:
            print(f"Error adding foreign keys: {e}")
        finally:
            conn.close()
    else:
        print("Error: Unable to connect to the database.")

def create_prescription_table():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE Prescription (
    Prescription_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Doctor_ID INTEGER,
    Patient_ID INTEGER,
    Medicine_ID INTEGER,
    Dosage TEXT NOT NULL,
    Duration TEXT NOT NULL,
    Date TEXT NOT NULL,
    Instructions TEXT,
    FOREIGN KEY (Doctor_ID) REFERENCES Doctor(Doctor_ID) ON DELETE CASCADE,
    FOREIGN KEY (Patient_ID) REFERENCES Patient(Patient_ID) ON DELETE CASCADE,
    FOREIGN KEY (Medicine_ID) REFERENCES Medicine(Medicine_ID) ON DELETE CASCADE
);

            ''')
            conn.commit()
            print("Prescription table created successfully!")
        except sqlite3.Error as e:
            print(f"Error creating Prescription table: {e}")
        finally:
            conn.close()


# Reset the database
def reset_database():
    confirm = input("Are you sure you want to reset the database? This will delete all records and recreate the tables (yes/no): ")
    
    if confirm.lower() == "yes":
        try:
            create_all_tables()
            print("Database reset successfully! All records have been deleted, and tables have been recreated.")
        except sqlite3.Error as e:
            print(f"An error occurred while resetting the database: {e}")
    else:
        print("Database reset canceled.")

def create_billing_table():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Billing (
                    Bill_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Patient_ID INTEGER,
                    Amount REAL NOT NULL,
                    Payment_Status TEXT DEFAULT 'Unpaid',
                    Billing_Date TEXT DEFAULT CURRENT_DATE,
                    FOREIGN KEY (Patient_ID) REFERENCES Patient(Patient_ID) ON DELETE CASCADE
                );
            ''')
            conn.commit()
            print("Billing table created successfully!")
        except sqlite3.Error as e:
            print(f"An error occurred while creating the Billing table: {e}")
        finally:
            conn.close()
    else:
        print("Failed to create the Billing table due to connection issues.")

# Create all tables
def create_all_tables():
    drop_tables()  # Optional: To reset everything before creating

    create_user_table()
    create_doctor_table()  # Create Doctor table first
    create_department_table()  # Department now comes after Doctor
    create_patient_table()
    create_appointment_table()
    create_manager_table()
    create_lab_technician_table()
    create_lab_test_table()
    create_room_table()
    create_patient_room_table()
    alter_patient_room_table()  # Alter the table to add new columns
    create_prescription_table() 
    create_medicine_table()
    create_pharmacy_transaction_table()
    create_billing_table() 

# Call the function to create all tables when the file is run
if __name__ == "__main__":
    create_all_tables()
