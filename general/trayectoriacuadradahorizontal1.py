#programa mejorado para ir a home y ejecutar una trayectoria cuadrada en plano xz repetida

import threading
import sys
import os
from kortex_api.autogen.client_stubs.BaseClientRpc import BaseClient
from kortex_api.autogen.client_stubs.BaseCyclicClientRpc import BaseCyclicClient
from kortex_api.autogen.messages import Base_pb2, BaseCyclic_pb2
import time

TIMEOUT_DURATION = 20  # Tiempo de espera en segundos para completar la acción

# Función para verificar si el movimiento se completó correctamente
def check_for_end_or_abort(e):
    def check(notification, e=e):
        print("EVENTO: " + Base_pb2.ActionEvent.Name(notification.action_event))
        if notification.action_event == Base_pb2.ACTION_END or notification.action_event == Base_pb2.ACTION_ABORT:
            e.set()
    return check

# Función para realizar el movimiento cartesiano a una posición específica
def move_to_pose(base, base_cyclic, target_pose):
    print(f"Moviendo a la pose: {target_pose}")

    # Crear una acción de tipo cartesiano
    action = Base_pb2.Action()
    action.name = "Movimiento cartesiano a pose específica"
    action.application_data = ""

    # Configurar la pose deseada
    cartesian_pose = action.reach_pose.target_pose
    cartesian_pose.x = target_pose["x"]
    cartesian_pose.y = target_pose["y"]
    cartesian_pose.z = target_pose["z"]
    cartesian_pose.theta_x = target_pose["theta_x"]
    cartesian_pose.theta_y = target_pose["theta_y"]
    cartesian_pose.theta_z = target_pose["theta_z"]

    # Configurar notificaciones de finalización
    e = threading.Event()
    notification_handle = base.OnNotificationActionTopic(
        check_for_end_or_abort(e),
        Base_pb2.NotificationOptions()
    )

    # Ejecutar la acción
    print("Ejecutando acción...")
    base.ExecuteAction(action)

    print("Esperando a que el movimiento finalice...")
    finished = e.wait(TIMEOUT_DURATION)
    base.Unsubscribe(notification_handle)

    if finished:
        print("Movimiento completado exitosamente.")
    else:
        print("Timeout al esperar la notificación de finalización.")

    # Retroalimentación final
    feedback = base_cyclic.RefreshFeedback()
    print("Pose final alcanzada:")
    print(f"x: {feedback.base.tool_pose_x:.3f} m")
    print(f"y: {feedback.base.tool_pose_y:.3f} m")
    print(f"z: {feedback.base.tool_pose_z:.3f} m")
    print(f"theta_x: {feedback.base.tool_pose_theta_x:.3f}°")
    print(f"theta_y: {feedback.base.tool_pose_theta_y:.3f}°")
    print(f"theta_z: {feedback.base.tool_pose_theta_z:.3f}°")

# Función para ir a la posición "Home"
def move_to_home(base, base_cyclic):
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

# Función para mover a la trayectoria cuadrada con repeticiones
def move_square(base, base_cyclic, repetitions=3):
    # Definir los puntos de la trayectoria cuadrada
    path = [
 #       {"x": 0.400, "y": 0.200, "z": 0.400, "theta_x": 90.000, "theta_y": 0.000, "theta_z": 150.000},
 #       {"x": 0.300, "y": 0.200, "z": 0.400, "theta_x": 90.000, "theta_y": 0.000, "theta_z": 150.000},
 #       {"x": 0.300, "y": 0.200, "z": 0.500, "theta_x": 90.000, "theta_y": 0.000, "theta_z": 150.000},
 #       {"x": 0.400, "y": 0.200, "z": 0.500, "theta_x": 90.000, "theta_y": 0.000, "theta_z": 150.000},
 #       {"x": 0.400, "y": 0.200, "z": 0.400, "theta_x": 90.000, "theta_y": 0.000, "theta_z": 150.000}  #movimiento cuadrado vertical
 #       {"x": 0.200, "y": 0.400, "z": 0.400, "theta_x": 90.000, "theta_y": 0.000, "theta_z": 150.000},
 #       {"x": 0.200, "y": 0.300, "z": 0.400, "theta_x": 90.000, "theta_y": 0.000, "theta_z": 150.000},
 #       {"x": 0.200, "y": 0.300, "z": 0.500, "theta_x": 90.000, "theta_y": 0.000, "theta_z": 150.000},
 #       {"x": 0.200, "y": 0.400, "z": 0.500, "theta_x": 90.000, "theta_y": 0.000, "theta_z": 150.000},
 #       {"x": 0.200, "y": 0.400, "z": 0.400, "theta_x": 90.000, "theta_y": 0.000, "theta_z": 150.000}  # movimiento cuadrado vertical
 #       {"x": 0.400, "y": 0.400, "z": 0.200, "theta_x": 90.000, "theta_y": 0.000, "theta_z": 150.000},
 #       {"x": 0.300, "y": 0.400, "z": 0.200, "theta_x": 90.000, "theta_y": 0.000, "theta_z": 150.000},
 #       {"x": 0.300, "y": 0.500, "z": 0.200, "theta_x": 90.000, "theta_y": 0.000, "theta_z": 150.000},
 #       {"x": 0.400, "y": 0.500, "z": 0.200, "theta_x": 90.000, "theta_y": 0.000, "theta_z": 150.000},
 #       {"x": 0.400, "y": 0.400, "z": 0.200, "theta_x": 90.000, "theta_y": 0.000, "theta_z": 150.000}  # movimiento cuadrado horizontal al lado izquierdo de la mesa desde el #manipul 
        {"x": 0.300, "y":  0.200, "z": 0.200, "theta_x": 90.000, "theta_y": 0.000, "theta_z": 150.000}, #SW
        {"x": 0.300, "y": -0.200, "z": 0.200, "theta_x": 90.000, "theta_y": 0.000, "theta_z": 150.000}, #SE
        {"x": 0.400, "y": -0.200, "z": 0.200, "theta_x": 90.000, "theta_y": 0.000, "theta_z": 150.000}, #NE
        {"x": 0.400, "y":  0.200, "z": 0.200, "theta_x": 90.000, "theta_y": 0.000, "theta_z": 150.000}, #NW

 
    ]

    # Repetir la trayectoria cuadrada las veces que se desee
    for i in range(repetitions):
        print(f"\nInicio de la repetición {i+1}/{repetitions} de la trayectoria cuadrada")
        for target_pose in path:
            print(f"Moviendo a la pose {target_pose}")
            move_to_pose(base, base_cyclic, target_pose)

def main():
    # Importar utilidades
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    import utilities

    # Parsear argumentos y conectar al dispositivo
    args = utilities.parseConnectionArguments()
    with utilities.DeviceConnection.createTcpConnection(args) as router:
        base = BaseClient(router)
        base_cyclic = BaseCyclicClient(router)

        # Primero, mover a la posición 'Home'
        if not move_to_home(base, base_cyclic):
            print("Error al mover a la posición 'Home'.")
            return

        # Después, mover a la trayectoria cuadrada 3 veces
        move_square(base, base_cyclic, repetitions=3)

if __name__ == "__main__":
    main()
