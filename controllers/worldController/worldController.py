"""supervisor controller."""

import os, sys
from controller import Keyboard, Supervisor
from math import pi
import socket
import json
from dotenv import load_dotenv
import os
import time
import threading

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../../")
from utils.maze import create_maze

# Load environment variables from .env file
load_dotenv()

# Get HOST and PORT from environment variables
HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))

supervisor = Supervisor()
keyboard = Keyboard()
stimestep = int(supervisor.getBasicTimeStep())
keyboard.enable(stimestep)

bb8_node = supervisor.getFromDef("BB-8")
body_node = supervisor.getFromDef("body_pose")
translation_field = bb8_node.getField("translation")
rotation_field = bb8_node.getField("rotation")
bodyRotationField = body_node.getField("rotation")

# get fakeBody_node shape Box and get its size
bb8_shapeSize = supervisor.getFromDef("fakeBodyShape").getField("size").getSFVec3f()

floor = supervisor.getFromDef("floor")
floorSize = floor.getField("floorSize")
floorTileSize = [x / 2 for x in (floor.getField("floorTileSize").getSFVec2f())]
wallHeight = floor.getField("wallHeight").getSFVec3f()
floor_width, floor_height = floorSize.getSFVec2f()

rows, cols = int(floor_width / floorTileSize[0]), int(floor_height / floorTileSize[1])

# Create walls matrix
matrixCols = cols
matrixRows = rows
maze = create_maze(matrixRows, matrixCols)

# for i in range(matrixRows):
#     for j in range(matrixCols):
#         print(maze[i][j], end=" ")
#     print()

startingPoint: list[int]
endingPoint: list[int]

for i in range(matrixRows):
    if maze[0][i] == 0:
        startingPoint = [0, i]
        break

for i in range(matrixRows):
    if maze[matrixRows - 1][i] == 0:
        endingPoint = [matrixRows - 1, i]
        break

print(f"Starting point: {startingPoint}")
print(f"Ending point: {endingPoint}")


wallsGroup = supervisor.getFromDef("walls")

for i in range(matrixRows):
    for j in range(matrixCols):
        if maze[i][j] != 0:
            x = floor_width / 2 - (i + 1) * floorTileSize[0] + floorTileSize[0] / 2
            y = floor_height / 2 - (j + 1) * floorTileSize[1] + floorTileSize[1] / 2
            wallsGroup.getField("children").importMFNodeFromString(
                -1,
                f'Wall {{ name "wall{i}_{j}" translation {x} {y} 0 rotation 0 0 0 {pi/2} size {floorTileSize[0]} {floorTileSize[1]} {wallHeight} }}',
            )


def reset_robot_position():
    # traverse first row to find a cell with value 0 to place the robot
    extraDistance = startingPoint[1] * floorTileSize[0]
    robotX = (
        floor_height / 2
        - extraDistance
        - (bb8_shapeSize[1] / 2)
        - (floorTileSize[1] / 2 - bb8_shapeSize[1] / 2)
    )
    robotY = (
        floor_width / 2
        - (bb8_shapeSize[0] / 2)
        - (floorTileSize[0] / 2 - bb8_shapeSize[0] / 2)
    )
    new_value = [robotY, robotX, 0.00]
    translation_field.setSFVec3f(new_value)
    rotation_field.setSFRotation([0, 1, 0, 0])
    bodyRotationField.setSFRotation([0, 1, 0, 0])


reset_robot_position()

sensor_data: dict[str, float]
moving = False
move_bot_thread: threading.Thread


def moveBot(direction: str, step=False):
    current_position = translation_field.getSFVec3f()
    bodyRotation = bodyRotationField.getSFRotation()
    global moving, move_bot_thread

    loopCount = 1 if not step else int(floorTileSize[1] * 100)

    if moving:
        return

    moving = True
    for i in range(loopCount):
        if direction == "UP":
            current_position[0] += 0.01
            bodyRotation = [0, 1, 0, bodyRotation[3] + 0.3]
        elif direction == "DOWN":
            current_position[0] -= 0.01
            bodyRotation = [0, 1, 0, bodyRotation[3] - 0.3]
        elif direction == "LEFT":
            current_position[1] += 0.01
            bodyRotation = [1, 0, 0, bodyRotation[3] - 0.3]
        elif direction == "RIGHT":
            current_position[1] -= 0.01
            bodyRotation = [1, 0, 0, bodyRotation[3] + 0.3]
        translation_field.setSFVec3f(current_position)
        bodyRotationField.setSFRotation(bodyRotation)
        if step:
            time.sleep(0.01)
    moving = False


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

discoveryMatrix: list[list[int]] = [
    [0 for i in range(matrixCols)] for j in range(matrixRows)
]


def auto_move():
    # move bot to the right for ever unless it hits a wall
    # if sensor_data[direction] < 1000.0 then there is a wall
    # if sensor_data[direction] == 1000.0 then there is no wall
    global moving, move_bot_thread, sensor_data
    while True:
        try:
            if moving:
                continue
            direction = ""
            # if sensor_data["Right"] == 1000.0:
            #     direction = "RIGHT"
            # elif sensor_data["Up"] == 1000.0:
            #     direction = "UP"
            # elif sensor_data["Down"] == 1000.0:
            #     direction = "DOWN"
            # elif sensor_data["Left"] == 1000.0:
            #     direction = "LEFT"
            if direction != "":
                moveBot(direction, True)
        except Exception as e:
            pass


def keyBoardHandler():
    key = keyboard.getKey()
    global move_bot_thread
    if key == ord("R"):
        print("Resetting robot")
        reset_robot_position()
    direction = ""
    useStep = False
    if key == keyboard.UP:
        direction = "UP"
    if key == keyboard.DOWN:
        direction = "DOWN"
    if key == keyboard.LEFT:
        direction = "LEFT"
    if key == keyboard.RIGHT:
        direction = "RIGHT"
    if key == ord("W"):
        direction = "UP"
        useStep = True
    if key == ord("S"):
        direction = "DOWN"
        useStep = True
    if key == ord("A"):
        direction = "LEFT"
        useStep = True
    if key == ord("D"):
        direction = "RIGHT"
        useStep = True
    if direction != "":
        if useStep:
            move_bot_thread = threading.Thread(
                target=moveBot, args=(direction, True), name="move_bot_thread"
            )
            move_bot_thread.start()
        else:
            moveBot(direction)


threading.Thread(target=auto_move).start()

while supervisor.step(stimestep) != -1:
    keyBoardHandler()
    sensor_data_json = client_socket.recv(1024)
    sensor_data = json.loads(sensor_data_json.decode())

client_socket.close()
