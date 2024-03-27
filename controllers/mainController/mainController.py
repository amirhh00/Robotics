"""mainController controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot
import socket
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get HOST and PORT from environment variables
HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))

# create the Robot instance.
robot = Robot()

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())

# You should insert a getDevice-like function in order to get the
# instance of a device of the robot. Something like distance sensors
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

# Main loop:
# - perform simulation steps until Webots is stopping the controller
while robot.step(timestep) != -1:
    sensor_data = {
        "Up": dsUp.getValue(),
        "Down": dsDown.getValue(),
        "Left": dsLeft.getValue(),
        "Right": dsRight.getValue(),
    }

    # Convert sensor data to JSON
    sensor_data_json = json.dumps(sensor_data)

    # Send sensor data to client
    client_socket.sendall(sensor_data_json.encode())

client_socket.close()
