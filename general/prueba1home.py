#! /usr/bin/env python3
#lo lleva a un home configurado, esto es lo que se obtiene
""" Posición cartesiana del efector final:
x: 0.439 m
y: 0.193 m
z: 0.447 m
theta_x: 90.683°
theta_y: -1.067°
theta_z: 150.018° """
import sys
import os
from kortex_api.autogen.client_stubs.BaseClientRpc import BaseClient
from kortex_api.autogen.client_stubs.BaseCyclicClientRpc import BaseCyclicClient
from kortex_api.autogen.messages import Base_pb2, BaseCyclic_pb2

def get_home_position(base, base_cyclic):
    # Mueve el brazo a la posición "Home"
    print("Moviendo el brazo a la posición 'Home'...")
    action_type = Base_pb2.RequestedActionType()
    action_type.action_type = Base_pb2.REACH_JOINT_ANGLES
    action_list = base.ReadAllActions(action_type)
    action_handle = None

    for action in action_list.action_list:
        if action.name == "Home":
            action_handle = action.handle

    if action_handle is None:
        print("No se encontró la acción 'Home'.")
        return False

    base.ExecuteActionFromReference(action_handle)

    # Esperar unos segundos para asegurar que el movimiento se complete
    import time
    time.sleep(5)

    # Obtener retroalimentación
    feedback = base_cyclic.RefreshFeedback()

    # Obtener posiciones articulares
    joint_angles = [joint.position for joint in feedback.actuators]

    # Obtener posición cartesiana del efector final
    cartesian_pose = {
        "x": feedback.base.tool_pose_x,
        "y": feedback.base.tool_pose_y,
        "z": feedback.base.tool_pose_z,
        "theta_x": feedback.base.tool_pose_theta_x,
        "theta_y": feedback.base.tool_pose_theta_y,
        "theta_z": feedback.base.tool_pose_theta_z,
    }

    print("Ángulos articulares:")
    for i, angle in enumerate(joint_angles):
        print(f"Articulación {i+1}: {angle:.2f}°")

    print("\nPosición cartesiana del efector final:")
    print(f"x: {cartesian_pose['x']:.3f} m")
    print(f"y: {cartesian_pose['y']:.3f} m")
    print(f"z: {cartesian_pose['z']:.3f} m")
    print(f"theta_x: {cartesian_pose['theta_x']:.3f}°")
    print(f"theta_y: {cartesian_pose['theta_y']:.3f}°")
    print(f"theta_z: {cartesian_pose['theta_z']:.3f}°")

    return True

def main():
    # Importar utilidades
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    import utilities

    # Parsear argumentos y conectar al dispositivo
    args = utilities.parseConnectionArguments()
    with utilities.DeviceConnection.createTcpConnection(args) as router:
        base = BaseClient(router)
        base_cyclic = BaseCyclicClient(router)
        get_home_position(base, base_cyclic)

if __name__ == "__main__":
    main()
