import asyncio
import websockets
import json
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from appointment import AppointmentManager
from users import UserManager
from cancellation import CancellationManager

# Database setup
engine = create_engine('sqlite:///faculty_on_site.db')
Session = sessionmaker(bind=engine)
session = Session()

# Create instances of UserManager, AppointmentManager, and CancellationManager
user_manager = UserManager(session)
appointment_manager = AppointmentManager(user_manager)
cancellation_manager = CancellationManager(appointment_manager, user_manager)

# Store connected WebSocket clients
connected_clients = set()

# WebSocket server to handle real-time updates
async def handle_client(websocket, path):
    """Handles communication with the client."""
    print("Client connected")
    connected_clients.add(websocket)  # Register the client

    try:
        while True:
            message = await websocket.recv()  # Receive a message from the client
            print(f"Message received: {message}")
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                print("Invalid JSON received.")
                continue

            # Handle actions based on the message received
            action = data.get("action")
            if action == "request_appointment":
                await handle_request_appointment(data)
            elif action == "request_cancellation":
                await handle_request_cancellation(data)
            elif action == "admin_accept_cancellation":
                await handle_admin_accept_cancellation(data)
            elif action == "admin_reject_cancellation":
                await handle_admin_reject_cancellation(data)

    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
    finally:
        connected_clients.discard(websocket)  # Unregister the client

# Handlers for specific actions
async def handle_request_appointment(data):
    """Handle student appointment requests."""
    try:
        student_id = data["student_id"]
        faculty_id = data["faculty_id"]
        date_time = data["date_time"]
        reason = data["reason"]
        appointment = appointment_manager.request_appointment(student_id, faculty_id, date_time, reason)
        if appointment:
            await broadcast_appointment_update(appointment)
    except KeyError as e:
        print(f"Missing data for request_appointment: {e}")

async def handle_request_cancellation(data):
    """Handle cancellation requests."""
    try:
        appointment_id = data["appointment_id"]
        requester_id = data["requester_id"]
        reason = data["reason"]
        cancellation_manager.request_cancellation(appointment_id, requester_id, reason)
        await broadcast_cancellation_update(appointment_id)
    except KeyError as e:
        print(f"Missing data for request_cancellation: {e}")

async def handle_admin_accept_cancellation(data):
    """Handle admin acceptance of a cancellation."""
    try:
        appointment_id = data["appointment_id"]
        admin_id = data["admin_id"]
        cancellation_manager.admin_accept_or_reject(appointment_id, admin_id, "accept")
        await broadcast_cancellation_update(appointment_id)
    except KeyError as e:
        print(f"Missing data for admin_accept_cancellation: {e}")

async def handle_admin_reject_cancellation(data):
    """Handle admin rejection of a cancellation."""
    try:
        appointment_id = data["appointment_id"]
        admin_id = data["admin_id"]
        cancellation_manager.admin_accept_or_reject(appointment_id, admin_id, "reject")
        await broadcast_cancellation_update(appointment_id)
    except KeyError as e:
        print(f"Missing data for admin_reject_cancellation: {e}")

# Broadcast updates to all clients
async def broadcast_appointment_update(appointment):
    """Broadcast updated appointment to all connected clients."""
    message = json.dumps({
        "action": "update_appointment",
        "appointment": str(appointment)
    })
    await send_to_all_clients(message)

async def broadcast_cancellation_update(appointment_id):
    """Broadcast cancellation request update to all connected clients."""
    message = json.dumps({
        "action": "update_cancellation",
        "appointment_id": appointment_id
    })
    await send_to_all_clients(message)

async def send_to_all_clients(message):
    """Send the message to all connected WebSocket clients."""
    disconnected_clients = set()
    for client in connected_clients:
        try:
            await client.send(message)
        except websockets.exceptions.ConnectionClosed:
            print("A client has disconnected during broadcast.")
            disconnected_clients.add(client)

    # Remove disconnected clients from the set
    connected_clients.difference_update(disconnected_clients)

# Start WebSocket server
async def start_server():
    """Start the WebSocket server to listen for connections."""
    async with websockets.serve(handle_client, "localhost", 8765):
        print("WebSocket server is running on ws://localhost:8765")
        await asyncio.Future()  # Run server until interrupted

if __name__ == "__main__":
    asyncio.run(start_server())
