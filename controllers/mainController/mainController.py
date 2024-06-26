"""mainController controller."""

from controller import Robot
import socket
import json
import importlib.util

HOST = "127.0.0.1"
PORT = 12345
try:
    importlib.util.find_spec("dotenv")
    # Load environment variables from .env file (HOST, PORT)
    from dotenv import load_dotenv
    import os

    load_dotenv()
    HOST = os.getenv("HOST")
    PORT = int(os.getenv("PORT"))
except ImportError:
    pass

robot = Robot()

timestep = int(robot.getBasicTimeStep())

dsUp = robot.getDevice("ds_up")
dsDown = robot.getDevice("ds_down")
dsLeft = robot.getDevice("ds_left")
dsRight = robot.getDevice("ds_right")
dsUp.enable(timestep)
dsDown.enable(timestep)
dsLeft.enable(timestep)
dsRight.enable(timestep)

# Initialize socket server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()
# Accept a client connection
client_socket, addr = server_socket.accept()

print(f"Server listening on {HOST}:{PORT}")

while robot.step(timestep) != -1:
    sensor_data = {
        "Up": dsUp.getValue(),
        "Down": dsDown.getValue(),
        "Left": dsLeft.getValue(),
        "Right": dsRight.getValue(),
    }

    # Convert sensor data to JSON
    sensor_data_json = json.dumps(sensor_data)

    # Send sensor data to 1 client (for more clients we need to use threads)
    client_socket.sendall(sensor_data_json.encode())

client_socket.close()
