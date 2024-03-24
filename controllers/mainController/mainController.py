"""mainController controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot, Keyboard, Motor, Supervisor

srobot = Supervisor()
# create the Robot instance.
# robot = Robot()
keyboard = Keyboard()

# get the time step of the current world.
# timestep = int(robot.getBasicTimeStep())
stimestep = int(srobot.getBasicTimeStep())
keyboard.enable(stimestep)

bb8_node = srobot.getFromDef("BB-8")
body_node = srobot.getFromDef("body_pose")
translation_field = bb8_node.getField("translation")
rotation_field = bb8_node.getField("rotation")
bodyRotationField = body_node.getField("rotation")
# ps = []
# psNames = ["ps0", "ps1", "ps2", "ps3", "ps4", "ps5", "ps6", "ps7"]

# for i in range(8):
#     ps.append(robot.getDevice(psNames[i]))
#     ps[i].enable(TIME_STEP)

# bodyWh: Motor = robot.getDevice("body_wheel")
# bodyWh.setPosition(float("inf"))
# bodyWh.setVelocity(0.5)

# You should insert a getDevice-like function in order to get the
# instance of a device of the robot. Something like:
#  motor = robot.getDevice('motorname')
#  ds = robot.getDevice('dsname')
#  ds.enable(timestep)

# print(Keyboard.CONTROL + ord("B"))


# Main loop:
# - perform simulation steps until Webots is stopping the controller
# def reset_robot_position():
#     # Add code to reset the robot's position here
#     bodyWh.setPosition(0)
#     bodyWh.setVelocity(0)
#     bodyWh.setAcceleration(0)
#     # bodyWh.setRotation(0)
#     pass


def reset_robot_position():
    new_value = [0, 0, 0.1]
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


while srobot.step(stimestep) != -1:
    key = keyboard.getKey()
    if key == ord("R"):
        print("Resetting robot position")
        reset_robot_position()
    if key == keyboard.UP:
        print("UP")
        moveBot("UP")
    if key == keyboard.DOWN:
        print("DOWN")
        moveBot("DOWN")
    if key == keyboard.LEFT:
        print("LEFT")
        moveBot("LEFT")
    if key == keyboard.RIGHT:
        print("RIGHT")
        moveBot("RIGHT")

# while robot.step(timestep) != -1:
#     key = keyboard.getKey()
#     if key == ord("R"):
#         print("Resetting robot position")
#         reset_robot_position()
#     # Read the sensors:
#     # Enter here functions to read sensor data, like:
#     #  val = ds.getValue()

#     # Process sensor data here.

#     # Enter here functions to send actuator commands, like:
#     #  motor.setPosition(10.0)
#     pass

# Enter here exit cleanup code.
