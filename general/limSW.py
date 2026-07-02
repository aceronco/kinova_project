
#es mejor desde home

#! /usr/bin/env python3
#pose basica y saber donde quedo
import threading 
import sys
import os
from kortex_api.autogen.client_stubs.BaseClientRpc import BaseClient
from kortex_api.autogen.client_stubs.BaseCyclicClientRpc import BaseCyclicClient
from kortex_api.autogen.messages import Base_pb2, BaseCyclic_pb2

# Tiempo máximo de espera
TIMEOUT_DURATION = 20

# Función para chequear el estado de la acción
def check_for_end_or_abort(e):
    def check(notification, e=e):
        print("EVENTO: " + Base_pb2.ActionEvent.Name(notification.action_event))
        if notification.action_event == Base_pb2.ACTION_END or notification.action_event == Base_pb2.ACTION_ABORT:
            e.set()
    return check

# Movimiento cartesiano a una posición específica
def move_to_pose(base, base_cyclic, target_pose):
    print("Iniciando movimiento cartesiano...")
    
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

def main():
    # Importar utilidades
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    import utilities

    # Parsear argumentos y conectar al dispositivo
    args = utilities.parseConnectionArguments()
    with utilities.DeviceConnection.createTcpConnection(args) as router:
        base = BaseClient(router)
        base_cyclic = BaseCyclicClient(router)

        # Pose objetivo
        target_pose = {
            "x": 0.240,
            "y": 0.200,
            "z": 0.400,
            "theta_x": 90.000,
            "theta_y": 0.000,
            "theta_z": 150.000
        }

        # Mover a la pose objetivo
        move_to_pose(base, base_cyclic, target_pose)

if __name__ == "__main__":
    main()
