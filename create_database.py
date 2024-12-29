# create_database.py

import sqlite3
import os

def create_tables(conn):
    cursor = conn.cursor()
    
    # Enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Create Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin', 'student', 'faculty'))
    );
    """)
    
    # Create Students table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Students (
        number TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        surname TEXT NOT NULL,
        department TEXT NOT NULL,
        year TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        FOREIGN KEY (number) REFERENCES Users(username) ON DELETE CASCADE
    );
    """)
    
    # Create Lecturers table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Lecturers (
        number TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        surname TEXT NOT NULL,
        department TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        chair TEXT NOT NULL,
        FOREIGN KEY (number) REFERENCES Users(username) ON DELETE CASCADE
    );
    """)
    
    # Create Appointments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Appointments (
        appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_number TEXT NOT NULL,
        lecturer_number TEXT NOT NULL,
        date TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('Pending', 'Scheduled', 'Cancelled')),
        cancellation_requested INTEGER DEFAULT 0 CHECK(cancellation_requested IN (0,1)),
        FOREIGN KEY (student_number) REFERENCES Students(number) ON DELETE CASCADE,
        FOREIGN KEY (lecturer_number) REFERENCES Lecturers(number) ON DELETE CASCADE
    );
    """)
    
    conn.commit()
    print("All tables created successfully.")

def main():
    # Define the database path
    db_path = os.path.join(os.path.dirname(__file__), 'FacultyOnSite.db')
    
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    print(f"Connected to database at {db_path}")
    
    try:
        create_tables(conn)
    except sqlite3.Error as e:
        print(f"An error occurred while creating tables: {e}")
    finally:
        conn.close()
        print("Database connection closed.")

if __name__ == "__main__":
    main()
