import threading
from collections import OrderedDict
from socket import socket, AF_INET, SOCK_DGRAM

import PathManager
from DroneState import DroneState


class UDPServer:
    def __init__(self, drone: DroneState, path_manager: PathManager):
        self.host = '0.0.0.0'
        self.port = 8889
        self.buffsize = 1024
        self.addr = (self.host, self.port)

        self.pm = path_manager

        self.server = socket(AF_INET, SOCK_DGRAM)
        self.server.bind(self.addr)

        # Drone
        self.drone = drone

        # Data members
        self.rc_command = {'vx': 0, 'vy': 0, 'vz': 0, 'vyaw': 0}
        self.controller_logs = OrderedDict()
        self.is_recording = False

        # Main loop thread
        self.main_loop_thread = threading.Thread(target=self.main_loop)
        self.main_loop_thread.start()

    def start_exp(self):
        self.is_recording = True
        self.drone.start_experiment()

    def end_exp(self, path_type, path_width, path_distance, userName, num_of_trial):
        self.is_recording = False
        self.drone.end_experiment(path_type, path_width, path_distance, userName, num_of_trial)

    def send_rc_command(self):
        self.drone.send_rc_command(self.rc_command)

    def main_loop(self):
        while True:
            data, addr = self.server.recvfrom(self.buffsize)
            data = data.decode('utf-8')
            if data == 'start_exp':
                self.drone.start_experiment()
            elif data == 'end_exp':
                self.drone.end_experiment(path_type=self.pm.current_path.path_type,
                                          path_width=self.pm.current_path.get_width(),
                                          path_distance=self.pm.current_path.get_distance(),
                                          userName=self.drone.get_user_name(), num_of_trial=self.drone.get_user_trial())
            elif data == 'command':
                pass
                # TODO: add handling
            elif data == 'takeoff':
                pass
            elif data == 'land':
                pass
            elif data.startswith('rc'):
                command_list = data.split(' ')
                velocity = self.drone.get_velocity()
                self.rc_command = {'vx': int(command_list[2]) / 100 * velocity,
                                   'vy': int(command_list[1]) / 100 * velocity,
                                   'vz': -int(command_list[3]) / 100 * velocity,
                                   'vyaw': int(command_list[1]) / 100 * velocity}
                self.send_rc_command()
            else:
                # print(data)
                data = eval(data)
                self.rc_command = data
                self.send_rc_command()

    def get_recording_state(self):
        return self.is_recording


if __name__ == '__main__':
    d = DroneState()
    pm = PathManager.PathManager(d)
    u = UDPServer(drone=d, path_manager=pm)
