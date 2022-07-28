import threading
import ControllerKeyboard
import DroneState
import PathManager
import UDPServer
from DroneEnvParameterController import DroneEnvParameterController
from DroneEnvSettingGUI import DroneEnvSettingGUI


# Create the drone state
d = DroneState.DroneState()
print('start')

# create a path manager
pm = PathManager.PathManager(d)

# create a UDP server
u = UDPServer.UDPServer(d, pm)

def control_thread():
    controller = ControllerKeyboard.ControllerKeyboard()


# Create keyboard control thread
controlThread = threading.Thread(target=control_thread, daemon=True)
controlThread.start()

# create the GUI
depc = DroneEnvParameterController(d.client)
GUI = DroneEnvSettingGUI(depc, u, pm, d)
