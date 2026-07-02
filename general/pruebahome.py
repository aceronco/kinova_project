import threading
import sys
import os

from kortex_api.autogen.client_stubs.BaseClientRpc import BaseClient
from kortex_api.autogen.client_stubs.BaseCyclicClientRpc import BaseCyclicClient
from kortex_api.autogen.messages import Base_pb2

TIMEOUT_DURATION = 20


def check_for_end_or_abort(e):
    def check(notification, e=e):
        print("EVENTO:", Base_pb2.ActionEvent.Name(notification.action_event))

        if notification.action_event in (
            Base_pb2.ACTION_END,
            Base_pb2.ACTION_ABORT,
        ):
            e.set()

    return check


def move_to_home(base, base_cyclic):

    print("Buscando la acción Home...")

    action_type = Base_pb2.RequestedActionType()
    action_type.action_type = Base_pb2.REACH_JOINT_ANGLES

    action_list = base.ReadAllActions(action_type)

    action_handle = None

    for action in action_list.action_list:
        print("Acción encontrada:", action.name)

        if action.name == "Home":
            action_handle = action.handle
            break

    if action_handle is None:
        print("No existe una acción llamada Home.")
        return False

    e = threading.Event()

    notification_handle = base.OnNotificationActionTopic(
        check_for_end_or_abort(e),
        Base_pb2.NotificationOptions()
    )

    print("Moviendo el robot a Home...")

    base.ExecuteActionFromReference(action_handle)

    finished = e.wait(TIMEOUT_DURATION)

    base.Unsubscribe(notification_handle)

    if not finished:
        print("Timeout.")
        return False

    print("\nMovimiento terminado.\n")

    feedback = base_cyclic.RefreshFeedback()

    print("===== POSE CARTESIANA =====")
    print(f"x = {feedback.base.tool_pose_x:.3f} m")
    print(f"y = {feedback.base.tool_pose_y:.3f} m")
    print(f"z = {feedback.base.tool_pose_z:.3f} m")
    print(f"theta_x = {feedback.base.tool_pose_theta_x:.3f}°")
    print(f"theta_y = {feedback.base.tool_pose_theta_y:.3f}°")
    print(f"theta_z = {feedback.base.tool_pose_theta_z:.3f}°")

    print("\n===== ÁNGULOS ARTICULARES =====")

    for i, actuator in enumerate(feedback.actuators):
        print(f"Joint {i+1}: {actuator.position:.3f}°")

    return True


def main():

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

    import utilities

    args = utilities.parseConnectionArguments()

    with utilities.DeviceConnection.createTcpConnection(args) as router:

        base = BaseClient(router)
        base_cyclic = BaseCyclicClient(router)

        move_to_home(base, base_cyclic)


if __name__ == "__main__":
    main()
