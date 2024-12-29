# main_app.py

from dbm import sqlite3
import customtkinter as ctk
from tkinter import messagebox
from database import db_connection, cursor, check_password, close_connection, hash_password

# Configure CustomTkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# GUI Utility Functions
def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def show_login(frame):
    clear_frame(frame)
    ctk.CTkLabel(frame, text="Faculty on Site", font=("Arial", 24)).pack(pady=20)

    username_entry = ctk.CTkEntry(frame, placeholder_text="Username", width=250)
    username_entry.pack(pady=10)

    password_entry = ctk.CTkEntry(frame, placeholder_text="Password", show="*", width=250)
    password_entry.pack(pady=10)

    login_error_label = ctk.CTkLabel(frame, text="", text_color="red", font=("Arial", 12))
    login_error_label.pack(pady=5)

    def handle_login():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        print(f"Attempting login for user: {username}")  # Debugging line
        try:
            user = cursor.execute("SELECT * FROM Users WHERE username = ?", (username,)).fetchone()
            print(f"User fetched: {user}")  # Debugging line
            if user and check_password(password, user[1]):
                role = user[2]
                print(f"User role: {role}")  # Debugging line
                if role == "admin":
                    show_admin_menu(frame, Admin(username))
                elif role == "student":
                    show_student_menu(frame, Student(username))
                elif role == "faculty":
                    show_faculty_menu(frame, Faculty(username))
                else:
                    login_error_label.configure(text="Role not recognized.")
            else:
                print("Invalid username or password.")  # Debugging line
                login_error_label.configure(text="Invalid username or password.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            print(f"Error during login: {e}")  # Debugging line

    ctk.CTkButton(frame, text="Login", command=handle_login).pack(pady=20)

# Change Password Feature
def change_password(frame, username):
    clear_frame(frame)
    ctk.CTkLabel(frame, text="Change Password", font=("Arial", 24)).pack(pady=20)

    old_password_entry = ctk.CTkEntry(frame, placeholder_text="Old Password", show="*", width=250)
    old_password_entry.pack(pady=10)

    new_password_entry = ctk.CTkEntry(frame, placeholder_text="New Password", show="*", width=250)
    new_password_entry.pack(pady=10)

    confirm_password_entry = ctk.CTkEntry(frame, placeholder_text="Confirm New Password", show="*", width=250)
    confirm_password_entry.pack(pady=10)

    error_label = ctk.CTkLabel(frame, text="", text_color="red", font=("Arial", 12))
    error_label.pack(pady=5)

    def handle_change_password():
        old_password = old_password_entry.get().strip()
        new_password = new_password_entry.get().strip()
        confirm_password = confirm_password_entry.get().strip()

        try:
            user = cursor.execute("SELECT * FROM Users WHERE username = ?", (username,)).fetchone()
            if user and check_password(old_password, user[1]):
                if new_password != confirm_password:
                    error_label.configure(text="New passwords do not match.")
                    return

                # Update the password
                cursor.execute("UPDATE Users SET password = ? WHERE username = ?", (hash_password(new_password), username))
                db_connection.commit()
                messagebox.showinfo("Success", "Password updated successfully.")
                # Redirect to the appropriate menu based on role
                role = user[2]
                if role == "admin":
                    show_admin_menu(frame, Admin(username))
                elif role == "student":
                    show_student_menu(frame, Student(username))
                elif role == "faculty":
                    show_faculty_menu(frame, Faculty(username))
            else:
                error_label.configure(text="Old password is incorrect.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            print(f"Error during password change: {e}")  # Debugging line

    ctk.CTkButton(frame, text="Change Password", command=handle_change_password).pack(pady=20)
    ctk.CTkButton(frame, text="Back", command=lambda: navigate_back(username, frame)).pack(pady=10)

def navigate_back(username, frame):
    # Determine user role to navigate back correctly
    try:
        user = cursor.execute("SELECT * FROM Users WHERE username = ?", (username,)).fetchone()
        if user:
            role = user[2]
            if role == "admin":
                show_admin_menu(frame, Admin(username))
            elif role == "student":
                show_student_menu(frame, Student(username))
            elif role == "faculty":
                show_faculty_menu(frame, Faculty(username))
            else:
                show_main_menu(frame)
        else:
            show_login(frame)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        print(f"Error during navigation: {e}")  # Debugging line

# Admin Class
class Admin:
    def __init__(self, username):
        self.username = username

    def approve_cancellations(self, frame):
        clear_frame(frame)
        ctk.CTkLabel(frame, text="Approve Cancellations", font=("Arial", 18)).pack(pady=10)

        try:
            requests = cursor.execute("SELECT * FROM Appointments WHERE cancellation_requested = 1").fetchall()
            if not requests:
                ctk.CTkLabel(frame, text="No cancellation requests to approve.").pack(pady=10)
                ctk.CTkButton(frame, text="Back", command=lambda: show_admin_menu(frame, self)).pack(pady=20)
                return

            for appointment in requests:
                request_text = f"Appointment {appointment[0]}\nStudent: {appointment[1]}\nLecturer: {appointment[2]}"
                decision_label = ctk.CTkLabel(frame, text=request_text)
                decision_label.pack(pady=5)

                def handle_decision(decision, app_id=appointment[0], label=decision_label):
                    try:
                        if decision == "accept":
                            cursor.execute("DELETE FROM Appointments WHERE appointment_id = ?", (app_id,))
                        elif decision == "reject":
                            cursor.execute("UPDATE Appointments SET cancellation_requested = 0 WHERE appointment_id = ?", (app_id,))
                        db_connection.commit()
                        label.destroy()
                        messagebox.showinfo("Success", f"Appointment {app_id} {decision}ed.")
                    except Exception as e:
                        messagebox.showerror("Error", f"An error occurred: {e}")
                        print(f"Error handling decision: {e}")  # Debugging line

                ctk.CTkButton(frame, text="Accept", command=lambda d="accept": handle_decision(d)).pack(pady=5)
                ctk.CTkButton(frame, text="Reject", command=lambda d="reject": handle_decision(d)).pack(pady=5)

            ctk.CTkButton(frame, text="Back", command=lambda: show_admin_menu(frame, self)).pack(pady=20)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            print(f"Error in approve_cancellations: {e}")  # Debugging line

    def edit_database(self, frame):
        clear_frame(frame)
        ctk.CTkLabel(frame, text="Edit Database", font=("Arial", 18)).pack(pady=10)

        table_option = ctk.CTkComboBox(frame, values=["Students", "Lecturers", "Appointments"])
        table_option.pack(pady=5)

        entry_id = ctk.CTkEntry(frame, placeholder_text="ID")
        entry_id.pack(pady=5)

        entry_field = ctk.CTkEntry(frame, placeholder_text="Field to Edit")
        entry_field.pack(pady=5)

        entry_value = ctk.CTkEntry(frame, placeholder_text="New Value")
        entry_value.pack(pady=5)

        def edit_table():
            edit_option = table_option.get()
            record_id = entry_id.get().strip()
            field = entry_field.get().strip()
            new_value = entry_value.get().strip()

            # Validate table and field names to prevent SQL injection
            valid_tables = {
                "Students": ["name", "surname", "department", "year", "email", "phone"],
                "Lecturers": ["name", "surname", "department", "email", "phone", "chair"],
                "Appointments": ["date", "start_time", "end_time", "status", "cancellation_requested"]
            }

            if edit_option not in valid_tables:
                messagebox.showerror("Error", "Invalid table selected.")
                return

            if field not in valid_tables[edit_option]:
                messagebox.showerror("Error", "Invalid field selected.")
                return

            try:
                if edit_option == "Students":
                    cursor.execute(f"UPDATE Students SET {field} = ? WHERE number = ?", (new_value, record_id))
                elif edit_option == "Lecturers":
                    cursor.execute(f"UPDATE Lecturers SET {field} = ? WHERE number = ?", (new_value, record_id))
                elif edit_option == "Appointments":
                    cursor.execute(f"UPDATE Appointments SET {field} = ? WHERE appointment_id = ?", (new_value, record_id))
                db_connection.commit()
                messagebox.showinfo("Success", f"{edit_option} table updated.")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
                print(f"Error in edit_database: {e}")  # Debugging line

        ctk.CTkButton(frame, text="Submit", command=edit_table).pack(pady=10)
        ctk.CTkButton(frame, text="Back", command=lambda: show_admin_menu(frame, self)).pack(pady=20)

# Student Class
class Student:
    def __init__(self, username):
        self.username = username

    def view_appointments(self, frame):
        clear_frame(frame)
        ctk.CTkLabel(frame, text="Your Appointments", font=("Arial", 18)).pack(pady=10)

        try:
            appointments = cursor.execute("SELECT * FROM Appointments WHERE student_number = ?", (self.username,)).fetchall()
            if appointments:
                for a in appointments:
                    ctk.CTkLabel(frame, text=f"ID {a[0]}: {a[3]} {a[4]}-{a[5]} ({a[6]})").pack(pady=5)
            else:
                ctk.CTkLabel(frame, text="No appointments found.").pack(pady=10)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            print(f"Error in view_appointments: {e}")  # Debugging line

        ctk.CTkButton(frame, text="Back", command=lambda: show_student_menu(frame, self)).pack(pady=20)

    def request_appointment(self, frame):
        clear_frame(frame)
        ctk.CTkLabel(frame, text="Request Appointment", font=("Arial", 18)).pack(pady=10)

        try:
            lecturers = cursor.execute("SELECT * FROM Lecturers").fetchall()
            if not lecturers:
                ctk.CTkLabel(frame, text="No lecturers available.").pack(pady=10)
                ctk.CTkButton(frame, text="Back", command=lambda: show_student_menu(frame, self)).pack(pady=20)
                return

            lecturer_list = ctk.CTkComboBox(frame, values=[f"{l[0]}: {l[1]} {l[2]}" for l in lecturers])
            lecturer_list.pack(pady=5)

            entry_date = ctk.CTkEntry(frame, placeholder_text="Date (YYYY-MM-DD)")
            entry_date.pack(pady=5)

            entry_start = ctk.CTkEntry(frame, placeholder_text="Start Time (HH:MM)")
            entry_start.pack(pady=5)

            entry_end = ctk.CTkEntry(frame, placeholder_text="End Time (HH:MM)")
            entry_end.pack(pady=5)

            def submit_request():
                lecturer_id = lecturer_list.get().split(":")[0].strip()
                date = entry_date.get().strip()
                start_time = entry_start.get().strip()
                end_time = entry_end.get().strip()

                # Basic validation
                if not (lecturer_id and date and start_time and end_time):
                    messagebox.showerror("Error", "All fields are required.")
                    return

                try:
                    # Verify that lecturer exists
                    lecturer_exists = cursor.execute("SELECT * FROM Lecturers WHERE number = ?", (lecturer_id,)).fetchone()
                    if not lecturer_exists:
                        messagebox.showerror("Error", "Selected lecturer does not exist.")
                        return

                    # Verify that student exists
                    student_exists = cursor.execute("SELECT * FROM Students WHERE number = ?", (self.username,)).fetchone()
                    if not student_exists:
                        messagebox.showerror("Error", "Student record does not exist.")
                        return

                    cursor.execute(
                        "INSERT INTO Appointments (student_number, lecturer_number, date, start_time, end_time, status) VALUES (?, ?, ?, ?, ?, 'Pending')",
                        (self.username, lecturer_id, date, start_time, end_time)
                    )
                    db_connection.commit()
                    messagebox.showinfo("Success", "Appointment request submitted.")
                    show_student_menu(frame, self)
                except sqlite3.IntegrityError as ie:
                    messagebox.showerror("Integrity Error", f"An integrity error occurred: {ie}")
                    print(f"Integrity Error: {ie}")  # Debugging line
                except sqlite3.Error as e:
                    messagebox.showerror("Error", f"An error occurred: {e}")
                    print(f"Error in request_appointment: {e}")  # Debugging line

            ctk.CTkButton(frame, text="Submit", command=submit_request).pack(pady=10)
            ctk.CTkButton(frame, text="Back", command=lambda: show_student_menu(frame, self)).pack(pady=20)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            print(f"Error in request_appointment: {e}")  # Debugging line

    def request_cancellation(self, frame):
        clear_frame(frame)
        ctk.CTkLabel(frame, text="Request Cancellation", font=("Arial", 18)).pack(pady=10)

        entry_id = ctk.CTkEntry(frame, placeholder_text="Appointment ID")
        entry_id.pack(pady=5)

        def submit_cancellation():
            app_id = entry_id.get().strip()
            if not app_id:
                messagebox.showerror("Error", "Appointment ID is required.")
                return
            try:
                cursor.execute("UPDATE Appointments SET cancellation_requested = 1 WHERE appointment_id = ? AND student_number = ?", (app_id, self.username))
                if cursor.rowcount == 0:
                    messagebox.showerror("Error", "No such appointment found or you are not authorized to cancel it.")
                else:
                    db_connection.commit()
                    messagebox.showinfo("Success", "Cancellation request submitted.")
                    show_student_menu(frame, self)
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
                print(f"Error in submit_cancellation: {e}")  # Debugging line

        ctk.CTkButton(frame, text="Submit", command=submit_cancellation).pack(pady=10)
        ctk.CTkButton(frame, text="Back", command=lambda: show_student_menu(frame, self)).pack(pady=20)

# Faculty Class
class Faculty:
    def __init__(self, username):
        self.username = username

    def view_counseling_hours(self, frame):
        clear_frame(frame)
        ctk.CTkLabel(frame, text="Counseling Hours", font=("Arial", 18)).pack(pady=10)

        try:
            appointments = cursor.execute("SELECT * FROM Appointments WHERE lecturer_number = ?", (self.username,)).fetchall()
            if appointments:
                for a in appointments:
                    ctk.CTkLabel(frame, text=f"ID {a[0]}: {a[3]} {a[4]}-{a[5]} ({a[6]})").pack(pady=5)
            else:
                ctk.CTkLabel(frame, text="No counseling hours found.").pack(pady=10)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            print(f"Error in view_counseling_hours: {e}")  # Debugging line

        ctk.CTkButton(frame, text="Back", command=lambda: show_faculty_menu(frame, self)).pack(pady=20)

    def accept_or_reject_appointment(self, frame):
        clear_frame(frame)
        ctk.CTkLabel(frame, text="Pending Appointments", font=("Arial", 18)).pack(pady=10)

        try:
            pending_appointments = cursor.execute("SELECT * FROM Appointments WHERE status = 'Pending' AND lecturer_number = ?", (self.username,)).fetchall()
            if not pending_appointments:
                ctk.CTkLabel(frame, text="No pending appointments.").pack(pady=10)
                ctk.CTkButton(frame, text="Back", command=lambda: show_faculty_menu(frame, self)).pack(pady=20)
                return

            for appointment in pending_appointments:
                request_text = f"Appointment {appointment[0]}\nStudent: {appointment[1]}\nDate: {appointment[3]} {appointment[4]}-{appointment[5]}"
                ctk.CTkLabel(frame, text=request_text).pack(pady=5)

                def handle_decision(decision, app_id=appointment[0]):
                    try:
                        if decision == "accept":
                            cursor.execute("UPDATE Appointments SET status = 'Scheduled' WHERE appointment_id = ?", (app_id,))
                        elif decision == "reject":
                            cursor.execute("DELETE FROM Appointments WHERE appointment_id = ?", (app_id,))
                        db_connection.commit()
                        messagebox.showinfo("Success", f"Appointment {app_id} {decision}ed.")
                        self.accept_or_reject_appointment(frame)  # Refresh the list
                    except Exception as e:
                        messagebox.showerror("Error", f"An error occurred: {e}")
                        print(f"Error in accept_or_reject_appointment: {e}")  # Debugging line

                ctk.CTkButton(frame, text="Accept", command=lambda d="accept": handle_decision(d)).pack(pady=5)
                ctk.CTkButton(frame, text="Reject", command=lambda d="reject": handle_decision(d)).pack(pady=5)

            ctk.CTkButton(frame, text="Back", command=lambda: show_faculty_menu(frame, self)).pack(pady=20)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            print(f"Error in accept_or_reject_appointment: {e}")  # Debugging line

    def cancel_appointment(self, frame):
        clear_frame(frame)
        ctk.CTkLabel(frame, text="Cancel Appointment", font=("Arial", 18)).pack(pady=10)

        entry_id = ctk.CTkEntry(frame, placeholder_text="Appointment ID")
        entry_id.pack(pady=5)

        def submit_cancellation():
            app_id = entry_id.get().strip()
            if not app_id:
                messagebox.showerror("Error", "Appointment ID is required.")
                return
            try:
                cursor.execute("DELETE FROM Appointments WHERE appointment_id = ? AND lecturer_number = ?", (app_id, self.username))
                if cursor.rowcount == 0:
                    messagebox.showerror("Error", "No such appointment found or you are not authorized to cancel it.")
                else:
                    db_connection.commit()
                    messagebox.showinfo("Success", "Appointment cancelled.")
                    show_faculty_menu(frame, self)
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
                print(f"Error in cancel_appointment: {e}")  # Debugging line

        ctk.CTkButton(frame, text="Submit", command=submit_cancellation).pack(pady=10)
        ctk.CTkButton(frame, text="Back", command=lambda: show_faculty_menu(frame, self)).pack(pady=20)

# View Table Functionality
def view_table(frame, table_name):
    clear_frame(frame)
    ctk.CTkLabel(frame, text=f"View {table_name} Table", font=("Arial", 18)).pack(pady=10)

    # Validate table name to prevent SQL injection
    valid_tables = ["Students", "Lecturers", "Appointments"]
    if table_name not in valid_tables:
        messagebox.showerror("Error", "Invalid table name.")
        show_main_menu(frame)
        return

    try:
        rows = cursor.execute(f"SELECT * FROM {table_name}").fetchall()
        if rows:
            for row in rows:
                ctk.CTkLabel(frame, text=str(row)).pack(pady=5)
        else:
            ctk.CTkLabel(frame, text="No data found.").pack(pady=10)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        print(f"Error in view_table: {e}")  # Debugging line

    ctk.CTkButton(frame, text="Back", command=lambda: show_main_menu(frame)).pack(pady=20)

# GUI Functions
def show_main_menu(frame):
    clear_frame(frame)
    ctk.CTkLabel(frame, text="Main Menu", font=("Arial", 24)).pack(pady=20)

    ctk.CTkButton(frame, text="View Students Table", command=lambda: view_table(frame, "Students")).pack(pady=10)
    ctk.CTkButton(frame, text="View Lecturers Table", command=lambda: view_table(frame, "Lecturers")).pack(pady=10)
    ctk.CTkButton(frame, text="View Appointments Table", command=lambda: view_table(frame, "Appointments")).pack(pady=10)
    ctk.CTkButton(frame, text="Logout", command=lambda: show_login(frame)).pack(pady=10)
    ctk.CTkButton(frame, text="Exit", command=exit_application).pack(pady=20)

def show_admin_menu(frame, admin):
    clear_frame(frame)
    ctk.CTkLabel(frame, text="Admin Menu", font=("Arial", 24)).pack(pady=20)

    ctk.CTkButton(frame, text="Approve Cancellations", command=lambda: admin.approve_cancellations(frame)).pack(pady=10)
    ctk.CTkButton(frame, text="Edit Database", command=lambda: admin.edit_database(frame)).pack(pady=10)
    ctk.CTkButton(frame, text="Change Password", command=lambda: change_password(frame, admin.username)).pack(pady=10)
    ctk.CTkButton(frame, text="Logout", command=lambda: show_login(frame)).pack(pady=10)
    ctk.CTkButton(frame, text="Exit", command=exit_application).pack(pady=20)

def show_student_menu(frame, student):
    clear_frame(frame)
    ctk.CTkLabel(frame, text="Student Menu", font=("Arial", 24)).pack(pady=20)

    ctk.CTkButton(frame, text="View Appointments", command=lambda: student.view_appointments(frame)).pack(pady=10)
    ctk.CTkButton(frame, text="Request Appointment", command=lambda: student.request_appointment(frame)).pack(pady=10)
    ctk.CTkButton(frame, text="Request Cancellation", command=lambda: student.request_cancellation(frame)).pack(pady=10)
    ctk.CTkButton(frame, text="Change Password", command=lambda: change_password(frame, student.username)).pack(pady=10)
    ctk.CTkButton(frame, text="Logout", command=lambda: show_login(frame)).pack(pady=10)
    ctk.CTkButton(frame, text="Exit", command=exit_application).pack(pady=20)

def show_faculty_menu(frame, faculty):
    clear_frame(frame)
    ctk.CTkLabel(frame, text="Faculty Menu", font=("Arial", 24)).pack(pady=20)

    ctk.CTkButton(frame, text="View Counseling Hours", command=lambda: faculty.view_counseling_hours(frame)).pack(pady=10)
    ctk.CTkButton(frame, text="Accept/Reject Appointments", command=lambda: faculty.accept_or_reject_appointment(frame)).pack(pady=10)
    ctk.CTkButton(frame, text="Cancel Appointment", command=lambda: faculty.cancel_appointment(frame)).pack(pady=10)
    ctk.CTkButton(frame, text="Change Password", command=lambda: change_password(frame, faculty.username)).pack(pady=10)
    ctk.CTkButton(frame, text="Logout", command=lambda: show_login(frame)).pack(pady=10)
    ctk.CTkButton(frame, text="Exit", command=exit_application).pack(pady=20)

def exit_application():
    if messagebox.askyesno("Confirm Exit", "Are you sure you want to exit?"):
        try:
            close_connection()  # Close the connection using the function from database.py
        except Exception as e:
            print(f"Error closing database connection: {e}")  # Debugging line
        exit()

# Main Application Setup
def main():
    root = ctk.CTk()  # Initialize the CustomTkinter root window
    root.title("Appointment Management System")
    root.geometry("600x400")  # Set the window size

    # Main frame for dynamic content
    main_frame = ctk.CTkFrame(root)
    main_frame.pack(fill="both", expand=True)

    # Start with the login screen
    show_login(main_frame)

    root.mainloop()

if __name__ == "__main__":
    main()
