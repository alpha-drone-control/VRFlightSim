import csv
import json
import os
import time
from collections import OrderedDict

class ExperimentLogger:
    def __init__(self, experiment_name='Development Trials'):
        self.experiment_name = experiment_name
        self.start_timestamp = time.time()
        self.headers = []
        self.events = OrderedDict()
        self.states = OrderedDict()
        self.rc_commands = OrderedDict()
        self.user_info = OrderedDict()

    def reset(self):
        self.__init__(experiment_name=self.experiment_name)

    def add_event(self, timestamp, data: dict):
        data["collision_position_x_val"] = data["position"].x_val
        data["collision_position_y_val"] = data["position"].y_val
        data["collision_position_z_val"] = data["position"].z_val
        del data["position"]
        self.events[timestamp] = data

    def preprocessing_data(self, data):
        temp_data = {}
        temp_data["has_collide"] = data['collision']['has_collided']
        temp_data["impact_point_x"] = data['collision']['impact_point']['x_val']
        temp_data["impact_point_y"] = data['collision']['impact_point']['y_val']
        temp_data["impact_point_z"] = data['collision']['impact_point']['z_val']
        temp_data["normal_x"] = data['collision']['normal']['x_val']
        temp_data["normal_y"] = data['collision']['normal']['y_val']
        temp_data["normal_z"] = data['collision']['normal']['z_val']
        temp_data["object_id"] = data['collision']['object_id']
        temp_data["object_name"] = data['collision']['object_name']
        temp_data["penetration_depth"] = data['collision']['penetration_depth']
        temp_data["altitude"] = data['gps_location']['altitude']
        temp_data["latitude"] = data['gps_location']['latitude']
        temp_data["longitude"] = data['gps_location']['longitude']
        temp_data["angular_acceleration_x"] = data['kinematics_estimated']['angular_acceleration']['x_val']
        temp_data["angular_acceleration_y"] = data['kinematics_estimated']['angular_acceleration']['y_val']
        temp_data["angular_acceleration_z"] = data['kinematics_estimated']['angular_acceleration']['z_val']
        temp_data["angular_velocity_x"] = data['kinematics_estimated']['angular_velocity']['x_val']
        temp_data["angular_velocity_y"] = data['kinematics_estimated']['angular_velocity']['y_val']
        temp_data["angular_velocity_z"] = data['kinematics_estimated']['angular_velocity']['z_val']
        temp_data["linear_acceleration_x"] = data['kinematics_estimated']['linear_acceleration']['x_val']
        temp_data["linear_acceleration_y"] = data['kinematics_estimated']['linear_acceleration']['y_val']
        temp_data["linear_acceleration_z"] = data['kinematics_estimated']['linear_acceleration']['z_val']
        temp_data["linear_velocity_x"] = data['kinematics_estimated']['linear_velocity']['x_val']
        temp_data["linear_velocity_y"] = data['kinematics_estimated']['linear_velocity']['y_val']
        temp_data["linear_velocity_z"] = data['kinematics_estimated']['linear_velocity']['z_val']
        temp_data["orientation_w"] = data['kinematics_estimated']['orientation']['w_val']
        temp_data["orientation_x"] = data['kinematics_estimated']['orientation']['x_val']
        temp_data["orientation_y"] = data['kinematics_estimated']['orientation']['y_val']
        temp_data["orientation_z"] = data['kinematics_estimated']['orientation']['z_val']
        temp_data["position_x"] = data['kinematics_estimated']['position']['x_val']
        temp_data["position_y"] = data['kinematics_estimated']['position']['y_val']
        temp_data["position_z"] = data['kinematics_estimated']['position']['z_val']
        return temp_data

    def add_state(self, timestamp, data):
        self.states[timestamp] = self.preprocessing_data(data)

    def add_rc_command(self, timestamp, data):
        self.rc_commands[timestamp] = data

    def output_log(self, path_type, path_width, path_distance, userName, num_of_trial, filetype='csv'):
        """
        :param filetype: the file type of the output log file
        :type filetype: str, 'csv' or 'json'

        Args:
            num_of_trial:
            userName:
            path_distance:
            path_width:
            path_type:
        """
        self._output_events_log(path_type, path_width, path_distance, userName, num_of_trial, filetype=filetype)
        self._output_states_log(path_type, path_width, path_distance, userName, num_of_trial, filetype=filetype)
        self._output_rc_commands_log(path_type, path_width, path_distance, userName, num_of_trial, filetype=filetype)

    def _output_events_log(self, path_type, path_width, path_distance, userName, num_of_trial, filetype='csv'):
        filename = "{}_{}_{}_{}_{}_{}_{}.{}".format(path_type, path_width, path_distance, userName,
                                                    num_of_trial, 'event', time.time(),
                                                    filetype)
        if len(self.events) == 0:
            print(
                "[warning] Drone events log is blank! Check whether the recording switch is on.")
            return

        if filetype == 'csv':
            header = list(list(self.events.items())[0][1].keys())
            header.insert(0, 'client_timestamp')
            self._write_csv_log_file(
                filename=filename, header=header, data=self.events)
        elif filetype == 'json':
            self._write_json_log_file(filename=filename, data=self.events)

    def _output_states_log(self, path_type, path_width, path_distance, userName, num_of_trial, filetype='csv'):
        filename = "{}_{}_{}_{}_{}_{}_{}.{}".format(path_type, path_width, path_distance, userName,
                                                    num_of_trial, 'states', time.time(),
                                                    filetype)
        if len(self.states) == 0:
            print(
                "[warning] Drone states log is blank! Check whether the recording switch is on.")
            return

        if filetype == 'csv':
            header = list(list(self.states.items())[0][1].keys())
            header.insert(0, 'client_timestamp')
            self._write_csv_log_file(
                filename=filename, header=header, data=self.states)
        elif filetype == 'json':
            self._write_json_log_file(filename=filename, data=self.states)

    def _output_rc_commands_log(self, path_type, path_width, path_distance, userName, num_of_trial, filetype='csv'):
        filename = "{}_{}_{}_{}_{}_{}_{}.{}".format(path_type, path_width, path_distance, userName,
                                                    num_of_trial, 'rcCommands', time.time(),
                                                    filetype)
        if len(self.rc_commands) == 0:
            print(
                "[warning] Drone rc commands log is blank! Check whether the recording switch is on.")
            return

        if filetype == 'csv':
            header = list(list(self.rc_commands.items())[0][1].keys())
            header.insert(0, 'client_timestamp')
            self._write_csv_log_file(
                filename=filename, header=header, data=self.rc_commands)
        elif filetype == 'json':
            self._write_json_log_file(filename=filename, data=self.rc_commands)

    def _write_csv_log_file(self, filename, header, data: dict):
        try:
            os.mkdir('./temp_log')
        except OSError as e:
            print('temp_log exists')
        with open('./temp_log/' + filename, 'w', newline='', encoding='utf-8') as fp:
            writer = csv.DictWriter(fp, fieldnames=header)
            writer.writeheader()
            for timestamp, val in data.items():
                val['client_timestamp'] = timestamp
                writer.writerow(val)

    def _write_json_log_file(self, filename, data):
        with open(filename, 'w', encoding='utf-8') as fp:
            json.dump(data, fp, indent=4)
