#! /usr/bin/env python3

import sys
import os
import time
import threading

from kortex_api.autogen.client_stubs.BaseClientRpc import BaseClient
from kortex_api.autogen.client_stubs.BaseCyclicClientRpc import BaseCyclicClient

from kortex_api.autogen.messages import Base_pb2, BaseCyclic_pb2, Common_pb2

# Maximum allowed waiting time during actions (in seconds)
TIMEOUT_DURATION = 20

# Create closure to set an event after an END or an ABORT
def check_for_end_or_abort(e):
    """Return a closure checking for END or ABORT notifications

    Arguments:
    e -- event to signal when the action is completed
        (will be set when an END or ABORT occurs)
    """
    def check(notification, e = e):
        print("EVENT : " + \
              Base_pb2.ActionEvent.Name(notification.action_event))
        if notification.action_event == Base_pb2.ACTION_END \
        or notification.action_event == Base_pb2.ACTION_ABORT:
            e.set()
    return check

def example_move_to_home_position(base):
    # Make sure the arm is in Single Level Servoing mode
    base_servo_mode = Base_pb2.ServoingModeInformation()
    base_servo_mode.servoing_mode = Base_pb2.SINGLE_LEVEL_SERVOING
    base.SetServoingMode(base_servo_mode)
    
    # Move arm to ready position
    print("Moving the arm to a safe position")
    action_type = Base_pb2.RequestedActionType()
    action_type.action_type = Base_pb2.REACH_JOINT_ANGLES
    action_list = base.ReadAllActions(action_type)
    action_handle = None
    for action in action_list.action_list:
        if action.name == "Home":
            action_handle = action.handle

    if action_handle is None:
        print("Can't reach safe position. Exiting")
        return False

    e = threading.Event()
    notification_handle = base.OnNotificationActionTopic(
        check_for_end_or_abort(e),
        Base_pb2.NotificationOptions()
    )

    base.ExecuteActionFromReference(action_handle)
    finished = e.wait(TIMEOUT_DURATION)
    base.Unsubscribe(notification_handle)

    if finished:
        print("Safe position reached")
    else:
        print("Timeout on action notification wait")
    return finished

def example_angular_action_movement(base):
    
    print("Starting angular action movement ...")
    action = Base_pb2.Action()
    action.name = "Example angular action movement"
    action.application_data = ""

    actuator_count = base.GetActuatorCount()

    # Place arm straight up
    for joint_id in range(actuator_count.count):
        joint_angle = action.reach_joint_angles.joint_angles.joint_angles.add()
        joint_angle.joint_identifier = joint_id
        joint_angle.value = 0

    e = threading.Event()
    notification_handle = base.OnNotificationActionTopic(
        check_for_end_or_abort(e),
        Base_pb2.NotificationOptions()
    )
    
    print("Executing action")
    base.ExecuteAction(action)

    print("Waiting for movement to finish ...")
    finished = e.wait(TIMEOUT_DURATION)
    base.Unsubscribe(notification_handle)

    if finished:
        print("Angular movement completed")
    else:
        print("Timeout on action notification wait")
    return finished

def example_cartesian_action_movement(base, base_cyclic):
    
    print("Starting Cartesian action movement ...")
    action = Base_pb2.Action()
    action.name = "Example Cartesian action movement"
    action.application_data = ""

    feedback = base_cyclic.RefreshFeedback()

    cartesian_pose = action.reach_pose.target_pose
    cartesian_pose.x = feedback.base.tool_pose_x          # (meters)
    cartesian_pose.y = feedback.base.tool_pose_y - 0.1    # (meters)
    cartesian_pose.z = feedback.base.tool_pose_z - 0.2    # (meters)
    cartesian_pose.theta_x = feedback.base.tool_pose_theta_x # (degrees)
    cartesian_pose.theta_y = feedback.base.tool_pose_theta_y # (degrees)
    cartesian_pose.theta_z = feedback.base.tool_pose_theta_z # (degrees)

    e = threading.Event()
    notification_handle = base.OnNotificationActionTopic(
        check_for_end_or_abort(e),
        Base_pb2.NotificationOptions()
    )

    print("Executing action")
    base.ExecuteAction(action)

    print("Waiting for movement to finish ...")
    finished = e.wait(TIMEOUT_DURATION)
    base.Unsubscribe(notification_handle)

    if finished:
        print("Cartesian movement completed")
    else:
        print("Timeout on action notification wait")
    return finished

def send_tool_command(base, tool_command, tool_duration, tool_cmd):
    """
    Send a command to the gripper.

    Args:
    - base: BaseClient instance.
    - tool_command: Mode of the tool (e.g., velocity or position).
    - tool_duration: Duration of the command (0 for immediate).
    - tool_cmd: Command value (e.g., -1 for close, 0 for open, 0.5 for half-open).

    Returns:
    - True if the command was sent successfully, False otherwise.
    """
    try:
        # Create gripper command
        gripper_command = Base_pb2.GripperCommand()
        gripper_command.mode = tool_command  # This would be a command that is valid for the gripper, check available modes
        gripper_command.duration = tool_duration

        # Set the gripper command value
        finger = gripper_command.gripper.finger.add()
        finger.finger_identifier = 1  # For example, for the first finger
        finger.value = tool_cmd

        # Send the command
        base.SendGripperCommand(gripper_command)
        print(f"Gripper command sent (Mode: {tool_command}, Cmd: {tool_cmd}).")
        time.sleep(2)  # Wait for the gripper to execute the command
        return True
    except Exception as e:
        print(f"Error sending gripper command: {e}")
        return False

def close_gripper(base):
    print("Closing the gripper...")
    # Use a valid mode, which you may need to refer to documentation for.
    return send_tool_command(base, Base_pb2.GRIPPER_POSITION, 0, 0.9)  # Position mode, close fully

def open_gripper_halfway(base):
    print("Opening the gripper halfway...")
    return send_tool_command(base, Base_pb2.GRIPPER_POSITION, 0, 0.5)  # Position mode, half-open

def open_gripper_fully(base):
    print("Opening the gripper fully...")
    return send_tool_command(base, Base_pb2.GRIPPER_POSITION, 0, 0.0)  # Position mode, fully open




def main():
    
    # Import the utilities helper module
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    import utilities

    # Parse arguments
    args = utilities.parseConnectionArguments()
    
    # Create connection to the device and get the router
    with utilities.DeviceConnection.createTcpConnection(args) as router:

        # Create required services
        base = BaseClient(router)
        base_cyclic = BaseCyclicClient(router)

        # Example core
        success = True

   
        success &= example_move_to_home_position(base)
        success &= example_cartesian_action_movement(base, base_cyclic)  
        success &= example_angular_action_movement(base)
    # Gripper control
        if not close_gripper(base):
            print("Failed to close the gripper.")
        if not open_gripper_halfway(base):
            print("Failed to open the gripper halfway.")
        if not open_gripper_fully(base):
            print("Failed to fully open the gripper.")


        return 0 if success else 1

if __name__ == "__main__":
    exit(main())
