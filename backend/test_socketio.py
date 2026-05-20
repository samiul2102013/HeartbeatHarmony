import socketio
import time

# Create a Socket.IO client
sio = socketio.Client(logger=True, engineio_logger=True)

@sio.event
def connect():
    print("\n✅ Successfully connected to the Socket.IO server!")
    
    print("Sending a test community message...")
    sio.emit('message', {
        "room": "community",
        "content": "Hello from the Python test script!"
    })

@sio.event
def disconnect():
    print("\n❌ Disconnected from server.")

@sio.on('chat_message')
def on_chat_message(data):
    print("\n📥 Received community message broadcast:")
    print(data)

@sio.on('online_users')
def on_online_users(data):
    print("\n👥 Online Users List Received:")
    print(data)

@sio.on('user_joined')
def on_user_joined(data):
    print(f"\n👋 User Joined: {data['username']}")

@sio.on('error')
def on_error(data):
    print(f"\n⚠️ Error from server: {data}")

if __name__ == '__main__':
    print("=== Socket.IO Testing Script ===")
    
    # 1. Provide a real JWT token here
    TOKEN = input("Please paste a valid JWT access token: ").strip()
    
    if not TOKEN:
        print("A token is required to test.")
        exit(1)

    try:
        print("\nAttempting to connect to http://localhost:8000...")
        # 2. Connect with the token in the headers, just like the frontend will do!
        sio.connect(
            'http://localhost:8000', 
            headers={'Authorization': f'Bearer {TOKEN}'},
            transports=['websocket', 'polling']
        )
        
        # Keep the script running to listen for events
        sio.wait()
    except socketio.exceptions.ConnectionError as e:
        print(f"\n🚨 Connection failed. Make sure your Django server is running on localhost:8000.")
        print(f"Error details: {e}")
    except KeyboardInterrupt:
        print("\nTest stopped.")
