import threading
import airsim
import PathGenerator
from DroneState import DroneState


class PathManager:
    current_path = None

    def __init__(self, drone_state: DroneState):
        self.client = airsim.MultirotorClient()
        self.grid_enable = False
        self.drone_state = drone_state
        self.event_listener_thread = threading.Thread(target=self.event_listener, daemon=True)
        self.event_listener_thread.start()
        self.drone_size = drone_state.get_drone_size()

    def event_listener(self):
        while True:
            self.check_grid()
            if self.client.simGetCollisionInfo().has_collided:
                # print(self.client.simGetCollisionInfo().has_collided)
                temp_collision = self.client.simGetCollisionInfo()
                # print(temp_collision.object_name[0:2])
                if temp_collision.object_name[0:2] == "ck":
                    # print(temp_collision.object_name[0:2])
                    if self.current_path.path_type == "crossing":
                        self.current_path.get_ck_dic()[temp_collision.object_name].destroy_mid()

                    self.current_path.update_ck_list_state(temp_collision.object_name, True)
                    # print(self.current_path.get_ck_state())

                    temp = {"time_stamp": temp_collision.time_stamp,
                            "position": temp_collision.position,
                            "event": str(self.current_path.get_ck_dic()[temp_collision.object_name].get_index())}
                    # print('log event')
                    self.drone_state.trigger_event(event=temp)

                    temp_bool = True

                    for i in self.current_path.ck_state_list:
                        if not self.current_path.ck_state_list[i]:
                            temp_bool = False
                    if temp_bool and not self.current_path.get_complete_state():
                        self.current_path.update_complete_state(True)
                    # print(self.current_path.get_complete_state())

    def check_grid(self):
        # generate grid with 1m x 1m and the range from the begin to the checker with width as 20m
        if self.get_grid_state():
            num_of_row = 10 + 1
            left_most = -10
            right_most = 10
            num_of_column = 21
            self.generate_grid_row(num_of_row, left_most, right_most)
            self.generate_grid_column(num_of_column)

    def generate_grid_row(self, num_of_row, left_most, right_most):
        vector_list = []
        for i in range(0, num_of_row):
            vector_list.append(airsim.Vector3r(self.drone_state.distance_convertor(i),
                                               self.drone_state.distance_convertor(left_most), 1))
            vector_list.append(airsim.Vector3r(self.drone_state.distance_convertor(i),
                                               self.drone_state.distance_convertor(right_most), 1))
        self.client.simPlotLineList(vector_list, duration=0.1)

    def generate_grid_column(self, num_of_column):
        left_most = -num_of_column // 2
        vector_list = []
        for i in range(0, num_of_column):
            vector_list.append(airsim.Vector3r(self.drone_state.distance_convertor(0),
                                               self.drone_state.distance_convertor(left_most + i), 1))
            vector_list.append(airsim.Vector3r(self.drone_state.distance_convertor(10),
                                               self.drone_state.distance_convertor(left_most + i), 1))
        self.client.simPlotLineList(vector_list, duration=0.1)

    def create_crossing_path(self) -> bool:
        if not self.current_path:
            self.current_path = PathGenerator.CrossingPath(drone_size=self.drone_size)
            self.current_path.create_path()
            return True
        if self.current_path.get_complete_state():
            self.current_path.destroy_path()
            self.current_path = PathGenerator.CrossingPath(drone_size=self.drone_size)
            self.current_path.create_path()
            return True
        return False

    def create_pointing_path(self) -> bool:
        if not self.current_path:
            self.current_path = PathGenerator.PointingPath(drone_size=self.drone_size)
            self.current_path.create_path()
            return True
        if self.current_path.get_complete_state():
            self.current_path.destroy_path()
            self.current_path = PathGenerator.PointingPath(drone_size=self.drone_size)
            self.current_path.create_path()
            return True
        return False

    def get_grid_state(self):
        return self.grid_enable

    def set_grid_state(self, new_state):
        self.grid_enable = new_state

    if __name__ == '__main__':
        drone = DroneState()
        pm = PathManager()
        pm.create_crossing_path()
