"""mainController controller."""

from controller import Keyboard, Supervisor
from math import pi
import numpy as np

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

print(f"rows: {rows}, cols: {cols}")


def reset_robot_position():
    new_value = [-floor_width / 2 + 0.08, -floor_height / 2 + 0.08, 0.00]
    translation_field.setSFVec3f(new_value)
    rotation_field.setSFRotation([0, 1, 0, 0])
    bodyRotationField.setSFRotation([0, 1, 0, 0])


reset_robot_position()

# Create walls matrix
wall_matrix = np.random.choice([0, 1], size=(rows, cols), p=[0.01, 0.99])
for col in range(cols):
    wall_matrix[np.random.choice(rows)][col] = 0

wallsGroup = supervisor.getFromDef("walls")

for i in range(rows):
    for j in range(cols):
        if wall_matrix[i][j] == 1:
            x = floor_width / 2 - (i + 1) * floorTileSize[0] + floorTileSize[0] / 2
            y = floor_height / 2 - (j + 1) * floorTileSize[1]
            wallsGroup.getField("children").importMFNodeFromString(
                -1,
                f'Wall {{ name "wall{i}_{j}" translation {x} {y} 0 rotation 0 0 0 {pi/2} size 0.001 {floorTileSize[0]} {wallHeight} }}',
            )


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
        print("Resetting robot position")
        reset_robot_position()
    if key == keyboard.UP:
        moveBot("UP")
    if key == keyboard.DOWN:
        moveBot("DOWN")
    if key == keyboard.LEFT:
        moveBot("LEFT")
    if key == keyboard.RIGHT:
        moveBot("RIGHT")
