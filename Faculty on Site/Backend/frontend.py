import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from users import UserManager, Role
from appointment import AppointmentManager
from cancellation import CancellationManager
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import asyncio
import websockets
import threading

# Database setup
engine = create_engine('sqlite:///faculty_on_site.db')
Session = sessionmaker(bind=engine)
session = Session()

# Backend Managers
user_manager = UserManager(session)
appointment_manager = AppointmentManager(user_manager)
cancellation_manager = CancellationManager(appointment_manager, user_manager)

# WebSocket Client for Real-Time Updates
async def websocket_client():
    async with websockets.connect("ws://localhost:8765") as websocket:
        while True:
            try:
                message = await websocket.recv()
                print("Real-time update received:", message)
            except websockets.exceptions.ConnectionClosed:
                print("WebSocket connection closed.")
                break

# Start WebSocket client in a separate thread
def start_websocket_client():
    asyncio.run(websocket_client())

threading.Thread(target=start_websocket_client, daemon=True).start()

# CustomTkinter Frontend Application
class FacultyOnSiteApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Faculty On-Site")
        self.geometry("800x600")

        # Login Frame
        self.login_frame = ctk.CTkFrame(self)
        self.login_frame.pack(pady=20, padx=60, fill="both", expand=True)

        self.label = ctk.CTkLabel(self.login_frame, text="Faculty On-Site Login", font=("Arial", 24))
        self.label.pack(pady=12, padx=10)

        self.username_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Username")
        self.username_entry.pack(pady=12, padx=10)

        self.password_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=12, padx=10)

        self.login_button = ctk.CTkButton(self.login_frame, text="Login", command=self.login)
        self.login_button.pack(pady=12, padx=10)

        self.message_label = ctk.CTkLabel(self.login_frame, text="", font=("Arial", 12))
        self.message_label.pack(pady=12, padx=10)

        # Placeholder for role-specific frames
        self.main_frame = None

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        user = user_manager.authenticate_user(username, password)
        if user:
            self.message_label.configure(text=f"Welcome, {user.role.value.title()}!", fg_color="green")
            self.show_main_frame(user)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def show_main_frame(self, user):
        self.login_frame.pack_forget()
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=20, padx=60, fill="both", expand=True)

        welcome_label = ctk.CTkLabel(self.main_frame, text=f"Welcome, {user.username}", font=("Arial", 18))
        welcome_label.pack(pady=12, padx=10)

        if user.role == Role.ADMIN:
            self.show_admin_controls()
        elif user.role == Role.FACULTY:
            self.show_faculty_controls(user)
        elif user.role == Role.STUDENT:
            self.show_student_controls(user)

        logout_button = ctk.CTkButton(self.main_frame, text="Logout", command=self.logout)
        logout_button.pack(pady=12, padx=10)

    def show_admin_controls(self):
        admin_label = ctk.CTkLabel(self.main_frame, text="Admin Controls", font=("Arial", 16))
        admin_label.pack(pady=12, padx=10)

        manage_users_button = ctk.CTkButton(self.main_frame, text="Manage Users", command=self.manage_users)
        manage_users_button.pack(pady=12, padx=10)

    def show_faculty_controls(self, user):
        faculty_label = ctk.CTkLabel(self.main_frame, text="Faculty Controls", font=("Arial", 16))
        faculty_label.pack(pady=12, padx=10)

        view_appointments_button = ctk.CTkButton(self.main_frame, text="View Appointments", command=self.view_appointments)
        view_appointments_button.pack(pady=12, padx=10)

    def show_student_controls(self, user):
        student_label = ctk.CTkLabel(self.main_frame, text="Student Controls", font=("Arial", 16))
        student_label.pack(pady=12, padx=10)

        request_appointment_button = ctk.CTkButton(self.main_frame, text="Request Appointment", command=self.request_appointment)
        request_appointment_button.pack(pady=12, padx=10)

    def manage_users(self):
        # Placeholder for admin user management logic
        messagebox.showinfo("Manage Users", "Admin user management functionality goes here.")

    def view_appointments(self):
        # Placeholder for faculty appointment viewing logic
        messagebox.showinfo("View Appointments", "Faculty appointment viewing functionality goes here.")

    def request_appointment(self):
        # Placeholder for student appointment request logic
        messagebox.showinfo("Request Appointment", "Student appointment request functionality goes here.")

    def logout(self):
        self.main_frame.pack_forget()
        self.login_frame.pack(pady=20, padx=60, fill="both", expand=True)

if __name__ == "__main__":
    app = FacultyOnSiteApp()
    app.mainloop()
