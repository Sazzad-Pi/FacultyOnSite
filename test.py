# test.py

import sqlite3
from database import db_connection, cursor, hash_password, close_connection
import logging

def insert_users():
    """
    Insert users into the Users table.
    """
    users = [
        # Admin Users
        ('admin1', hash_password('Admin@123'), 'admin'),
        ('admin2', hash_password('Admin@456'), 'admin'),
        ('admin3', hash_password('Admin@789'), 'admin'),
        
        # Student Users
        ('student1', hash_password('Student@123'), 'student'),
        ('student2', hash_password('Student@123'), 'student'),
        ('student3', hash_password('Student@123'), 'student'),
        ('student4', hash_password('Student@123'), 'student'),
        
        # Faculty Users
        ('faculty1', hash_password('Faculty@123'), 'faculty'),
        ('faculty2', hash_password('Faculty@123'), 'faculty'),
        ('faculty3', hash_password('Faculty@123'), 'faculty'),
        ('faculty4', hash_password('Faculty@123'), 'faculty'),
    ]
    
    try:
        cursor.executemany("INSERT INTO Users (username, password, role) VALUES (?, ?, ?);", users)
        logging.debug("Inserted users into Users table.")
    except sqlite3.IntegrityError as ie:
        logging.warning(f"Integrity Error while inserting users: {ie}")
    except Exception as e:
        logging.error(f"Unexpected error while inserting users: {e}")
        raise e

def insert_students():
    """
    Insert student records into the Students table.
    """
    students = [
        ('student1', 'John', 'Doe', 'Computer Science', '2', 'john.doe@example.com', '1234567890'),
        ('student2', 'Alice', 'Johnson', 'Mathematics', '3', 'alice.johnson@example.com', '2345678901'),
        ('student3', 'Bob', 'Smith', 'Physics', '1', 'bob.smith@example.com', '3456789012'),
        ('student4', 'Carol', 'Williams', 'Chemistry', '4', 'carol.williams@example.com', '4567890123'),
    ]
    
    try:
        cursor.executemany("""
            INSERT INTO Students (number, name, surname, department, year, email, phone)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, students)
        logging.debug("Inserted students into Students table.")
    except sqlite3.IntegrityError as ie:
        logging.warning(f"Integrity Error while inserting students: {ie}")
    except Exception as e:
        logging.error(f"Unexpected error while inserting students: {e}")
        raise e

def insert_lecturers():
    """
    Insert lecturer records into the Lecturers table.
    """
    lecturers = [
        ('faculty1', 'Jane', 'Smith', 'Computer Science', 'jane.smith@example.com', '5678901234', 'Head of CS Department'),
        ('faculty2', 'Mark', 'Brown', 'Mathematics', 'mark.brown@example.com', '6789012345', 'Head of Mathematics Department'),
        ('faculty3', 'Linda', 'Davis', 'Physics', 'linda.davis@example.com', '7890123456', 'Head of Physics Department'),
        ('faculty4', 'James', 'Wilson', 'Chemistry', 'james.wilson@example.com', '8901234567', 'Head of Chemistry Department'),
    ]
    
    try:
        cursor.executemany("""
            INSERT INTO Lecturers (number, name, surname, department, email, phone, chair)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, lecturers)
        logging.debug("Inserted lecturers into Lecturers table.")
    except sqlite3.IntegrityError as ie:
        logging.warning(f"Integrity Error while inserting lecturers: {ie}")
    except Exception as e:
        logging.error(f"Unexpected error while inserting lecturers: {e}")
        raise e

def insert_appointments():
    """
    Insert sample appointments into the Appointments table.
    """
    appointments = [
        ('student1', 'faculty1', '2024-05-10', '10:00', '11:00', 'Pending'),
        ('student2', 'faculty2', '2024-05-11', '12:00', '13:00', 'Pending'),
        ('student3', 'faculty3', '2024-05-12', '14:00', '15:00', 'Pending'),
        ('student4', 'faculty4', '2024-05-13', '16:00', '17:00', 'Pending'),
    ]
    
    try:
        cursor.executemany("""
            INSERT INTO Appointments (student_number, lecturer_number, date, start_time, end_time, status)
            VALUES (?, ?, ?, ?, ?, ?);
        """, appointments)
        logging.debug("Inserted appointments into Appointments table.")
    except sqlite3.IntegrityError as ie:
        logging.warning(f"Integrity Error while inserting appointments: {ie}")
    except Exception as e:
        logging.error(f"Unexpected error while inserting appointments: {e}")
        raise e

def main():
    try:
        insert_users()
        insert_students()
        insert_lecturers()
        insert_appointments()
        db_connection.commit()
        logging.info("Test data inserted successfully.")
        print("Test data inserted successfully.")
    except Exception as e:
        db_connection.rollback()
        logging.critical(f"Failed to insert test data: {e}")
        print(f"Failed to insert test data: {e}")
    finally:
        close_connection()
        print("Database connection closed.")

if __name__ == "__main__":
    main()
