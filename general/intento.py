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


def move_to_pose(base, base_cyclic, x, y, z):

    # Leer orientación actual
    feedback = base_cyclic.RefreshFeedback()

    theta_x = feedback.base.tool_pose_theta_x
    theta_y = feedback.base.tool_pose_theta_y
    theta_z = feedback.base.tool_pose_theta_z

    print("\nOrientación conservada:")
    print(theta_x, theta_y, theta_z)

    action = Base_pb2.Action()
    action.name = "Move"

    pose = action.reach_pose.target_pose

    pose.x = x
    pose.y = y
    pose.z = z

    pose.theta_x = theta_x
    pose.theta_y = theta_y
    pose.theta_z = theta_z

    e = threading.Event()

    notification_handle = base.OnNotificationActionTopic(
        check_for_end_or_abort(e),
        Base_pb2.NotificationOptions()
    )

    print("\nMoviendo...")
    base.ExecuteAction(action)

    finished = e.wait(TIMEOUT_DURATION)

    base.Unsubscribe(notification_handle)

    if not finished:
        print("Timeout")
        return

    feedback = base_cyclic.RefreshFeedback()

    print("\nPose alcanzada")

    print(f"x = {feedback.base.tool_pose_x:.3f}")
    print(f"y = {feedback.base.tool_pose_y:.3f}")
    print(f"z = {feedback.base.tool_pose_z:.3f}")

    print(f"theta_x = {feedback.base.tool_pose_theta_x:.3f}")
    print(f"theta_y = {feedback.base.tool_pose_theta_y:.3f}")
    print(f"theta_z = {feedback.base.tool_pose_theta_z:.3f}")


def main():

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

    import utilities

    args = utilities.parseConnectionArguments()

    with utilities.DeviceConnection.createTcpConnection(args) as router:

        base = BaseClient(router)
        base_cyclic = BaseCyclicClient(router)

        feedback = base_cyclic.RefreshFeedback()

        print("\nPose actual")

        print(f"x = {feedback.base.tool_pose_x:.3f}")
        print(f"y = {feedback.base.tool_pose_y:.3f}")
        print(f"z = {feedback.base.tool_pose_z:.3f}")

        print(f"theta_x = {feedback.base.tool_pose_theta_x:.3f}")
        print(f"theta_y = {feedback.base.tool_pose_theta_y:.3f}")
        print(f"theta_z = {feedback.base.tool_pose_theta_z:.3f}")

        while True:

            print("\nIntroduzca la nueva posición.")

            x = float(input("x = "))
            y = float(input("y = "))
            z = float(input("z = "))

            move_to_pose(base, base_cyclic, x, y, z)


if __name__ == "__main__":
    main()
