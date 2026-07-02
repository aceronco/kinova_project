import os
import ctypes

# Ruta al archivo remoteApi.so (modifica esta ruta según tu instalación)

remote_api_path = "/home/alexander/CoppeliaSim_Pro_V4_9_0_rev6_Ubuntu24_04/programming/legacyRemoteApi/remoteApiBindings/lib/lib/Ubuntu20_04/remoteApi.so"

# Verifica si el archivo existe
if os.path.exists(remote_api_path):
    # Carga la biblioteca manualmente
    ctypes.CDLL(remote_api_path)
    print(f"Biblioteca cargada desde: {remote_api_path}")
else:
    raise FileNotFoundError(f"No se encontró la biblioteca en {remote_api_path}")

# Ahora importa sim
# Carga la biblioteca manualmente
if os.path.exists(remote_api_path):
    ctypes.CDLL(remote_api_path)
else:
    raise FileNotFoundError(f"No se encontró la biblioteca en {remote_api_path}")



import math
import time
import sim  # Asegúrate de tener el archivo sim.py en tu directorio o instalado en tu sistema

def simkinova(angle_alpha, angle_beta, angle_gamma, angle_omega, angle_sigma, duration):
    # Convertimos a radianes
    pos_alpha = math.radians(angle_alpha)
    pos_beta = math.radians(angle_beta)
    pos_gamma = math.radians(angle_gamma)
    pos_omega = math.radians(angle_omega)
    pos_sigma = math.radians(angle_sigma)

    # Conexión a CoppeliaSim
    print("Inicio programa")
    sim.simxFinish(-1)  # Cierra conexiones anteriores
    client_id = sim.simxStart('127.0.0.1', 19999, True, True, 5000, 10)

    if client_id != -1:
        print("Conexión exitosa con CoppeliaSim")

        # Obtención de handlers
        _, alpha_j1 = sim.simxGetObjectHandle(client_id, 'J1', sim.simx_opmode_blocking)
        _, beta_j2 = sim.simxGetObjectHandle(client_id, 'J2', sim.simx_opmode_blocking)
        _, gamma_j3 = sim.simxGetObjectHandle(client_id, 'J4', sim.simx_opmode_blocking)
        _, omega_j4 = sim.simxGetObjectHandle(client_id, 'J5', sim.simx_opmode_blocking)
        _, sigma_j5 = sim.simxGetObjectHandle(client_id, 'J6', sim.simx_opmode_blocking)

        # Cambio de posición
        sim.simxSetJointTargetPosition(client_id, alpha_j1, pos_alpha, sim.simx_opmode_blocking)
        sim.simxSetJointTargetPosition(client_id, beta_j2, pos_beta, sim.simx_opmode_blocking)
        sim.simxSetJointTargetPosition(client_id, gamma_j3, pos_gamma, sim.simx_opmode_blocking)
        sim.simxSetJointTargetPosition(client_id, omega_j4, pos_omega, sim.simx_opmode_blocking)
        sim.simxSetJointTargetPosition(client_id, sigma_j5, pos_sigma, sim.simx_opmode_blocking)
        
        time.sleep(duration)  # Pausa por el tiempo especificado

        # Envía un mensaje a la barra de estado en CoppeliaSim
        sim.simxAddStatusbarMessage(client_id, 'Hello CoppeliaSim!', sim.simx_opmode_oneshot)

        # Asegura que el último comando enviado haya llegado
        sim.simxGetPingTime(client_id)

        # Cierra la conexión
        sim.simxFinish(client_id)
        print("Conexión cerrada con CoppeliaSim")

    else:
        print("Conexión fallida")
    
    print("Programa terminado")

# Ejemplo de uso
simkinova(30, 45, 60, 90, 120, 5)  # Angulos en grados, duración en segundos
