import re
import tkinter as tk
import airsim
import DroneEnvParameterController
import DroneState
import PathManager
import UDPServer


class DroneEnvSettingGUI:
    def __init__(self, d: DroneEnvParameterController.DroneEnvParameterController, udp: UDPServer.UDPServer,
                 pm: PathManager.PathManager, drone: DroneState.DroneState):
        self.d = d
        self.pm = pm
        self.udp = udp
        self.drone = drone
        self.client = airsim.MultirotorClient()
        self.root = tk.Tk()
        self.root.title('Drone_Interaction Experiment')
        self.root.geometry('600x300')
        self.vx_val = tk.StringVar()
        self.vy_val = tk.StringVar()
        self.vz_val = tk.StringVar()
        self.vYaw_val = tk.StringVar()
        self.weather_val = tk.StringVar()
        self.vx_val.set('vx: 0')
        self.vy_val.set('vy: 0')
        self.vz_val.set('vz: 0')
        self.vYaw_val.set('angle: 0')
        self.weather_val.set('0')

        self.experiment_switch_val = tk.StringVar()
        self.experiment_switch_val.set('Start Experiment')

        self.vx = tk.Label(self.root, textvariable=self.vx_val)
        self.vy = tk.Label(self.root, textvariable=self.vy_val)
        self.vz = tk.Label(self.root, textvariable=self.vz_val)
        self.vYaw = tk.Label(self.root,
                             textvariable=self.vYaw_val)
        self.weather = tk.Label(
            self.root, textvariable=self.weather_val)

        # self.label_ms = tk.Label(self.root, text='Max Speed')
        # self.e_max_speed = tk.Entry(self.root)
        self.label_weather = tk.Label(self.root, text='Weather Ratio')
        self.e_weather_ratio = tk.Entry(self.root)
        self.label_ws = tk.Label(self.root, text='Wind Speed \n(Input a 1x3 array without brackets)'
                                 )
        self.e_wind = tk.Entry(self.root)

        # self.change_speed = tk.Button(self.root, text='Change Speed', command=self.cs)s
        self.rain = tk.Button(self.root, text='Rain',
                              command=lambda: self.d.update_env_setting(1, float(self.e_weather_ratio.get())))
        self.snow = tk.Button(self.root, text='Snow',
                              command=lambda: self.d.update_env_setting(2, float(self.e_weather_ratio.get())))
        self.dust = tk.Button(self.root, text='Dust',
                              command=lambda: self.d.update_env_setting(3, float(self.e_weather_ratio.get())))
        self.fog = tk.Button(self.root, text='Fog',
                             command=lambda: self.d.update_env_setting(4, float(self.e_weather_ratio.get())))
        self.wind = tk.Button(self.root, text='Wind',
                              command=lambda: self.d.update_env_setting(5, (
                                  int(re.findall(
                                      r"\d+", self.e_weather_ratio.get())[0]),
                                  int(re.findall(
                                      r"\d+", self.e_weather_ratio.get())[1]),
                                  int(re.findall(r"\d+", self.e_weather_ratio.get())[2]))))

        self.experiment_switch = tk.Button(self.root, textvariable=self.experiment_switch_val,
                                           command=lambda: self.update_exp_state())
        self.distance_e = tk.Entry(self.root)
        self.distance_b = tk.Button(self.root, text='Change the pointing distance',
                                    command=lambda: self.update_land_distance())
        self.width_e = tk.Entry(self.root)
        self.width_b = tk.Button(self.root, text='Change the width', command=lambda: self.update_width())

        self.username_e = tk.Entry(self.root)
        self.username_b = tk.Button(self.root, text='Tester Name',
                                    command=lambda: self.drone.set_user_name(self.username_e.get()))

        self.trial_e = tk.Entry(self.root)
        self.trial_b = tk.Button(self.root, text='Trial Turn',
                                 command=lambda: self.drone.set_trial_num(self.trial_e.get()))

        self.crossing_path = tk.Button(self.root, text='Crossing path',
                                       command=lambda: self.init_path("crossing"))
        self.pointing_path = tk.Button(self.root, text='Pointing Path',
                                       command=lambda: self.init_path("pointing"))
        self.grid_b = tk.Button(self.root, text='Generate Grid',
                                command=lambda: self.change_grid_state())

        self.vx.grid(row=0, column=0)
        self.vy.grid(row=1, column=0)
        self.vz.grid(row=2, column=0)
        self.vYaw.grid(row=3, column=0)
        self.label_weather.grid(row=4, column=0)
        self.e_weather_ratio.grid(row=5, column=0)
        self.label_ws.grid(row=6, column=0)
        self.e_wind.grid(row=7, column=0)
        self.rain.grid(row=0, column=1)
        self.snow.grid(row=1, column=1)
        self.dust.grid(row=2, column=1)
        self.fog.grid(row=3, column=1)
        self.wind.grid(row=4, column=1)
        self.experiment_switch.grid(row=9, column=1)
        self.crossing_path.grid(row=0, column=2)
        self.pointing_path.grid(row=1, column=2)
        self.username_e.grid(row=5, column=1)
        self.username_b.grid(row=6, column=1)
        self.trial_e.grid(row=7, column=1)
        self.trial_b.grid(row=8, column=1)
        self.grid_b.grid(row=8, column=0)

        # self.root.after(0, self.check_exp_state())
        self.root.after(0, self.update_parm())

        self.root.mainloop()

    def init_path(self, path_type: str):
        if path_type == "crossing":
            self.pm.create_crossing_path()
        else:
            self.pm.create_pointing_path()
        self.distance_e.grid(row=2, column=2)
        self.distance_b.grid(row=3, column=2)
        self.width_e.grid(row=4, column=2)
        self.width_b.grid(row=5, column=2)

    def update_parm(self):
        if self.pm.current_path:
            self.vx_val.set('vx: ' + str(
                self.client.getMultirotorState().kinematics_estimated.linear_velocity.x_val
                / self.pm.current_path.get_drone_size()) + 'm/s')
            self.vy_val.set('vy: ' + str(
                self.client.getMultirotorState().kinematics_estimated.linear_velocity.y_val
                / self.pm.current_path.get_drone_size()) + 'm/s')
            self.vz_val.set('vz: ' + str(
                self.client.getMultirotorState().kinematics_estimated.linear_velocity.z_val
                / self.pm.current_path.get_drone_size()) + 'm/s')
            self.vYaw_val.set(
                'angle: ' + str(
                    airsim.to_eularian_angles(
                        self.client.getMultirotorState().kinematics_estimated.orientation)[2]) + '°')
        self.root.after(500, self.update_parm)

    def check_exp_state(self):
        if self.pm.current_path:
            if self.pm.current_path.get_complete_state():
                self.update_exp_state()
        self.root.after(500, self.check_exp_state)

    def change_grid_state(self):
        self.pm.set_grid_state(not self.pm.get_grid_state())

    def update_land_distance(self):
        # in meter
        self.pm.current_path.update_distance(float(self.distance_e.get()))
        print(self.pm.current_path.get_distance())

    def update_width(self):
        self.pm.current_path.update_width(float(self.width_e.get()))
        print(self.pm.current_path.get_width())

    def update_exp_state(self):
        if self.udp.get_recording_state():  # End the experiment
            self.experiment_switch_val.set('Start Experiment')
            self.udp.end_exp(self.pm.current_path.path_type, self.pm.current_path.get_width(),
                             self.pm.current_path.get_distance(), self.username_e.get(), self.trial_e.get())
            self.pm.current_path.destroy_path()

        else:  # Start the experiment
            self.experiment_switch_val.set('End Experiment')
            self.udp.start_exp()


if __name__ == '__main__':
    client = airsim.MultirotorClient()
    depc = DroneEnvParameterController.DroneEnvParameterController(client)
    d = DroneState.DroneState()
    pm = PathManager.PathManager(d)
    udp = UDPServer.UDPServer(d, pm)
    pm.create_crossing_path()
    GUI = DroneEnvSettingGUI(depc, udp, pm, d)
