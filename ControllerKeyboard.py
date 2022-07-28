import threading
import time
from socket import socket, AF_INET, SOCK_DGRAM
import keyboard


class ControllerKeyboard:
    MAX_SPEED = 5.0  # Max speed for horizontal and vertical movement
    MAX_OMEGA = 5.0  # Max angular velocity in degrees/sec for rotation
    step_size_speed = 0.5
    step_size_omega = 250

    def __init__(self):
        self.vx = 0
        self.vy = 0
        self.vz = 0
        self.vyaw = 0

        # UDP server 
        self.host = 'localhost'
        self.port = 8889
        self.buffsize = 1024
        self.addr = (self.host, self.port)
        self.udp_client = socket(AF_INET, SOCK_DGRAM)

        # Main loop thread
        self.main_loop_thread = threading.Thread(target=self.main_loop)
        self.main_loop_thread.start()

    def set_key(self):
        if keyboard.is_pressed('n'):
            return 'start_exp'
        if keyboard.is_pressed('m'):
            return 'end_exp'

        # vx
        if keyboard.is_pressed('w'):
            if keyboard.is_pressed('s'):
                self.vx = 0
            else:
                if self.vx < self.MAX_SPEED:
                    self.vx += 1.0 * self.step_size_speed
        else:
            if keyboard.is_pressed('s'):
                if self.vx > -self.MAX_SPEED:
                    self.vx += -1.0 * self.step_size_speed
            else:
                self.vx = 0

        # vy
        if keyboard.is_pressed('a'):
            if keyboard.is_pressed('d'):
                self.vy = 0
            else:
                if self.vy > -self.MAX_SPEED:
                    self.vy += -1.0 * self.step_size_speed
        else:
            if keyboard.is_pressed('d'):
                if self.vy < self.MAX_SPEED:
                    self.vy += 1.0 * self.step_size_speed
            else:
                self.vy = 0

        # vz
        if keyboard.is_pressed('up'):
            if keyboard.is_pressed('down'):
                self.vz = 0
            else:
                if self.vz > -self.MAX_SPEED:
                    self.vz += -1.0 * self.step_size_speed
        else:
            if keyboard.is_pressed('down'):
                if self.vz < self.MAX_SPEED:
                    self.vz += 1.0 * self.step_size_speed
            else:
                self.vz = 0

        # vyaw
        if keyboard.is_pressed('right'):
            if keyboard.is_pressed('left'):
                self.vyaw = 0
            else:
                if self.vyaw < self.MAX_OMEGA:
                    self.vyaw += 1.0 * self.step_size_omega
        else:
            if keyboard.is_pressed('left'):
                if self.vyaw > -self.MAX_OMEGA:
                    self.vyaw += -1.0 * self.step_size_omega
            else:
                self.vyaw = 0

        return 1

    def reset(self):
        self.vx = 0
        self.vy = 0
        self.vz = 0
        self.vyaw = 0

    def command(self) -> dict:
        command = {
            'vx': self.vx,
            'vy': self.vy,
            'vz': self.vz,
            'vyaw': self.vyaw
        }
        return command

    def main_loop(self):
        is_started = False
        while True:
            cmd = self.set_key()
            # print(f"\r{self.vx:.2f}\t{self.vy:.2f}\t{self.vz:.2f}", end='')
            if (not is_started) and cmd == 'start_exp':
                self.udp_client.sendto('start_exp'.encode('utf-8'), (self.addr))
                is_started = True
            elif is_started and cmd == 'end_exp':
                self.udp_client.sendto('end_exp'.encode('utf-8'), (self.addr))
            else:
                self.udp_client.sendto(str(self.command()).encode('utf-8'), (self.addr))
            time.sleep(0.1)


if __name__ == '__main__':
    ck = ControllerKeyboard()
