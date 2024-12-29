# database.py

import sqlite3
import bcrypt
import os
import logging

# Configure logging
logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configure the path to the database file
db_path = os.path.join(os.path.dirname(__file__), 'FacultyOnSite.db')

# Establish a persistent connection to SQLite database
try:
    db_connection = sqlite3.connect(db_path, check_same_thread=False)
    cursor = db_connection.cursor()
    logging.debug(f"Connected to database at {db_path}")
except sqlite3.Error as e:
    logging.critical(f"Failed to connect to database: {e}")
    raise e

# Enable foreign key constraints
try:
    cursor.execute("PRAGMA foreign_keys = ON;")
    logging.debug("Foreign key constraints enabled.")
except sqlite3.Error as e:
    logging.error(f"Failed to enable foreign key constraints: {e}")

def hash_password(password):
    """
    Hash a password for storing.
    """
    try:
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        logging.debug("Password hashed successfully.")
        return hashed.decode('utf-8')
    except Exception as e:
        logging.error(f"Error hashing password: {e}")
        raise e

def check_password(password, hashed):
    """
    Check a hashed password against a plain text password.
    """
    try:
        result = bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        logging.debug("Password verification result: {}".format(result))
        return result
    except ValueError as ve:
        logging.error(f"Invalid salt in hashed password: {ve}")
        return False
    except Exception as e:
        logging.error(f"Error checking password: {e}")
        return False

def close_connection():
    """
    Close the database connection gracefully.
    """
    try:
        if db_connection:
            db_connection.close()
            logging.debug("Database connection closed.")
    except sqlite3.Error as e:
        logging.error(f"Error closing database connection: {e}")
