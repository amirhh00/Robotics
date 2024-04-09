"""supervisor controller."""

import random
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

# enum for matrix values
# 0: empty cell
# 1: unreachable cell: e.g. wall
# 2: ending cell
# 3: visited cell
# infinite: unvisited cell
EMPTY = 0
WALL = 1
ENDING = 2
VISITED = 3
UNVISITED = float("inf")

isFinished = False


def printMatrix(mat=maze):
    for i in range(len(mat)):
        for j in range(len(mat[i])):
            print("[" if j == 0 else "", end="")
            print(
                (
                    "i,"
                    if mat[i][j] == UNVISITED
                    else (f"{mat[i][j]}{"," if j < len(mat[i]) - 1 else ""}") # nopep8
                ),
                end=" " if j < len(mat[i]) - 1 else "],\n",
            )

        print()
    print("-----------------------\n")

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
                f'DEF WALL{i}_{j} Wall {{ translation {x} {y} 0 rotation 0 0 0 {pi/2} size {floorTileSize[0]} {floorTileSize[1]} {wallHeight} }}',
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

robotPosition = [startingPoint[0], startingPoint[1]]


grid: list[list[int]] = [
    [UNVISITED for i in range(matrixCols)] for j in range(matrixRows)
]

# set the ending cell
grid[endingPoint[0]][endingPoint[1]] = ENDING

# set the starting cell
grid[startingPoint[0]][startingPoint[1]] = VISITED

# get direction based on x and y and the current robot position
def determine_direction(x, y):
    if x == robotPosition[0] + 1:
        return "DOWN"
    if x == robotPosition[0] - 1:
        return "UP"
    if y == robotPosition[1] + 1:
        return "RIGHT"
    if y == robotPosition[1] - 1:
        return "LEFT"
    print(f"cant go to [{x}, {y}] from {robotPosition}")

def isWall(direction):
    global sensor_data
    if direction == "UP":
        return sensor_data["Up"] < 1000.0
    if direction == "DOWN":
        return sensor_data["Down"] < 1000.0
    if direction == "LEFT":
        return sensor_data["Left"] < 1000.0
    if direction == "RIGHT":
        return sensor_data["Right"] < 1000.0


def lookAroundCurrentPositionForWalls(print=False):
    if isWall("UP") and robotPosition[0] - 1 >= 0:
        grid[robotPosition[0] - 1][robotPosition[1]] = WALL
    if isWall("DOWN") and robotPosition[0] + 1 < matrixRows:
        grid[robotPosition[0] + 1][robotPosition[1]] = WALL
    if isWall("LEFT") and robotPosition[1] - 1 >= 0:
        grid[robotPosition[0]][robotPosition[1] - 1] = WALL
    if isWall("RIGHT") and robotPosition[1] + 1 < matrixCols:
        grid[robotPosition[0]][robotPosition[1] + 1] = WALL
    if print:
        printMatrix(grid)


def moveBot(direction: str, step=False):
    if step and not direction:
        return
    if isFinished:
        return
    current_position = translation_field.getSFVec3f()
    bodyRotation = bodyRotationField.getSFRotation()
    global moving, move_bot_thread
    loopCount = 1 if not step else int(floorTileSize[1] * 100)

    if moving:
        return

    moving = True
    if step: 
        robotPosition[0] = (
            robotPosition[0] + 1
            if direction == "DOWN"
            else robotPosition[0] - 1 if direction == "UP" else robotPosition[0]
        )
        robotPosition[1] = (
            robotPosition[1] + 1
            if direction == "RIGHT"
            else robotPosition[1] - 1 if direction == "LEFT" else robotPosition[1]
        )
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
    # time.sleep(0.5)
    moving = False
    if step:
        lookAroundCurrentPositionForWalls(True)
        print(f"Moved {direction} to {robotPosition}")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

def determineDirectionBasedOnPosition(x, y):
    if x == robotPosition[0] + 1:
        return "DOWN"
    if x == robotPosition[0] - 1:
        return "UP"
    if y == robotPosition[1] + 1:
        return "RIGHT"
    if y == robotPosition[1] - 1:
        return "LEFT"


def auto_move():
    def display_maze( path):
        for item in path:
            maze[item[0]][item[1]] = VISITED
        pass
    def search(path):
        global isFinished
        if isFinished:
            return
        try:
            # time.sleep(0.3)
            cur = path[-1]
            # display_maze(path)
            dir = determine_direction(cur[0], cur[1])
            if dir is not None:
                moveBot(dir, True)
            possibles = [
                (cur[0], cur[1] + 1),
                (cur[0], cur[1] - 1),
                (cur[0] + 1, cur[1]),
                (cur[0] - 1, cur[1]),
            ]
            random.shuffle(possibles)
            for pos in possibles:
                if (
                    pos[0] < 0
                    or pos[1] < 0
                    or pos[0] > len(maze)
                    or pos[1] > len(maze[0])
                ):
                    continue
                # elif pos[0] < 0 or pos[1] < 0 or pos[0] > matrixRows -1 or pos[1] > matrixCols -1:
                #     continue
                elif maze[pos[0]][pos[1]] in [WALL, VISITED]:
                    continue
                elif pos in path:
                    continue
                # elif maze[pos[0]][pos[1]] == ENDING:
                #     path = path + (pos,)
                #     display_maze(path)
                #     isFinished = True
                #     print("Solution found! Press enter to finish")
                #     return
                else:
                    newpath = path + (pos,)
                    search(newpath)
                    maze[pos[0]][pos[1]] = VISITED
                    # display_maze(path)
                    dir = determine_direction(cur[0], cur[1])
                    if dir is not None:
                        moveBot(dir, True)
                    # time.sleep(0.3)
        except Exception as e:
            isFinished = True
            # display_maze(path)
            print("Solution found!")
            # change the color of the all walls to green
            # wallsGroup.getField("children").setMFColor(-1, [0, 1, 0])
            time.sleep(10)
            supervisor.worldReload()

    time.sleep(0.5)
    lookAroundCurrentPositionForWalls(True)
    search(((startingPoint[0], startingPoint[1]),))
    printMatrix(grid)

# https://www.laurentluce.com/posts/solving-mazes-using-python-simple-recursivity-and-a-search/


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
