import re
import threading
import time
import math
import airsim
import cv2
import numpy as np
from PIL import Image
from airsim.types import Quaternionr
from scipy.spatial.transform import Rotation as ScipyRotation

from DroneEnvParameterController import DroneEnvParameterController
from ExperimentLogger import ExperimentLogger


class DroneState:
    def __init__(self):
        self.droneLog = None
        self.state = None
        self.rc_command = {'vx': 0, 'vy': 0, 'vz': 0, 'vyaw': 0}
        self.is_recording = False

        # Drone client
        self.client = airsim.MultirotorClient()
        self.client.confirmConnection()
        self.client.enableApiControl(True)
        
        self.client.armDisarm(True)
        self.client.simEnableWeather(True)

        # Experiment logger
        self.experimentLogger = ExperimentLogger()

        # Drone environment parameter controller
        self.envParameterController = DroneEnvParameterController(self.client)

        # Threads
        self.listen_drone_state_thread = threading.Thread(target=self.listen_drone_state, daemon=True)
        self.listen_drone_state_thread.start()

        # Settings
        self.rc_command_duration = 0.4  # The duration of rc command
        self.CAMERA_NAME = '0'  # Camera

        # logger
        self.experimentLogger = ExperimentLogger()

        # drone size in meter of real world
        self.drone_size = 0.18

        # user name
        self.user_name = 'default'

        # trial number of user
        self.trial_num = 1

        # max speed
        self.max_speed = 8

        # tester pose
        self.tester_pose = airsim.Pose(
            airsim.Vector3r(self.distance_convertor(-1), self.distance_convertor(0),
                            self.distance_convertor(-0.65)), airsim.to_quaternion(-math.pi/18, 0, 0))
        self.change_tester_pose()

    def get_current_frame(self):
        response_image = self.client.simGetImage(
            self.CAMERA_NAME, airsim.ImageType.Scene)
        np_response_image = np.asarray(
            bytearray(response_image), dtype="uint8")
        decoded_frame = cv2.imdecode(np_response_image, cv2.IMREAD_COLOR)
        decoded_frame = cv2.cvtColor(
            decoded_frame, cv2.COLOR_BGR2RGBA)  # convert color

        # :dtype: <class 'PIL.Image.Image'>; :size: (256, 144)
        frame = Image.fromarray(decoded_frame)
        return frame

    def start_experiment(self):
        self.is_recording = True

    def end_experiment(self, path_type, path_width, path_distance, userName=None, num_of_trial=None):
        self.is_recording = False
        self.experimentLogger.output_log(path_type, path_width, path_distance, userName, num_of_trial)
        self.experimentLogger.reset()
        self.client.reset()
        self.client.enableApiControl(True)

    def send_rc_command(self, rc_command):
        # if random() > 0.5:
        self.rc_command = rc_command
        drone_orientation = ScipyRotation.from_quat(
            Quaternionr(**self.state['kinematics_estimated']['orientation']).to_numpy_array())
        yaw = drone_orientation.as_euler('zyx')[0]
        vx, vy = self.rc_command['vx'], self.rc_command['vy']
        self.rc_command['vx'] = vx * np.cos(yaw) + vy * np.cos(yaw + np.deg2rad(90))
        self.rc_command['vy'] = vx * np.sin(yaw) + vy * np.sin(yaw + np.deg2rad(90))
        self.client.moveByVelocityAsync(
            self.rc_command['vx'],
            self.rc_command['vy'],
            self.rc_command['vz'],
            self.rc_command_duration,
            drivetrain=airsim.DrivetrainType.ForwardOnly,
            yaw_mode=airsim.YawMode(True, self.rc_command['vyaw'])
        )

    def trigger_event(self, event: dict):
        current_timestamp = time.time()
        self.experimentLogger.add_event(current_timestamp, event)

    def get_drone_env_settings(self):
        return self.envParameterController.get_env_setting()

    def update_drone_env_parameters(self, settings: dict):
        for i in settings:
            self.envParameterController.update_env_setting(i, settings[i])

    def set_is_recording(self, is_recording: bool):
        self.is_recording = is_recording

    def get_user_name(self):
        return self.user_name

    def get_user_trial(self):
        return self.trial_num

    def set_user_name(self, new_name):
        if new_name:
            self.user_name = new_name

    def set_trial_num(self, new_trial):
        if new_trial:
            self.trial_num = new_trial

    def distance_convertor(self, real_dis) -> float:
        return real_dis / self.drone_size

    def get_drone_size(self):
        return self.drone_size

    def set_drone_size(self, size: float):
        self.drone_size = size

    def get_velocity(self):
        return self.max_speed

    def get_tester_pose(self):
        return self.tester_pose

    def change_tester_pose(self):
        print('change_tester_pose')
        self.client.simSetObjectPose('ExternalCamera', self.tester_pose)

    def set_tester_pose(self, new_pose):
        self.tester_pose = new_pose

    def listen_drone_state(self):
        while True:
            client_2 = airsim.MultirotorClient()
            droneState = client_2.getMultirotorState()
            if client_2.simGetCollisionInfo().has_collided:
                droneState.collision = client_2.simGetCollisionInfo()
            droneState = re.sub(r'<.*?>', '', str(droneState))
            droneState = eval(droneState)
            self.state = droneState

            if self.is_recording:
                current_timestamp = time.time()
                # XXX: Which rc command shall be recorded, world-axis command or drone-axis command?
                self.experimentLogger.add_rc_command(
                    current_timestamp, self.rc_command)
                self.experimentLogger.add_state(current_timestamp, self.state)

            time.sleep(0.1)


if __name__ == '__main__':
    pass
