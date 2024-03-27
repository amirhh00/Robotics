"""supervisor controller."""


import os, sys
from controller import Keyboard, Supervisor
from math import pi

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../../")
from utils.maze import create_maze

supervisor = Supervisor()
keyboard = Keyboard()
stimestep = int(supervisor.getBasicTimeStep())
keyboard.enable(stimestep)

bb8_node = supervisor.getFromDef("BB-8")
body_node = supervisor.getFromDef("body_pose")
translation_field = bb8_node.getField("translation")
rotation_field = bb8_node.getField("rotation")
bodyRotationField = body_node.getField("rotation")

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

for i in range(matrixRows):
    for j in range(matrixCols):
        print(maze[i][j], end=" ")
    print()

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
    robotX = floor_height / 2 - 0.08 - extraDistance
    robotY = floor_width / 2 - 0.08
    new_value = [robotY, robotX, 0.00]
    translation_field.setSFVec3f(new_value)
    rotation_field.setSFRotation([0, 1, 0, 0])
    bodyRotationField.setSFRotation([0, 1, 0, 0])


reset_robot_position()


def moveBot(direction: str):
    current_position = translation_field.getSFVec3f()
    bodyRotation = bodyRotationField.getSFRotation()

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

while supervisor.step(stimestep) != -1:
    key = keyboard.getKey()
    if key == ord("R"):
        print("Resetting robot")
        reset_robot_position()
    if key == keyboard.UP:
        moveBot("UP")
    if key == keyboard.DOWN:
        moveBot("DOWN")
    if key == keyboard.LEFT:
        moveBot("LEFT")
    if key == keyboard.RIGHT:
        moveBot("RIGHT")
