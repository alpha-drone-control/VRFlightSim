import airsim
from airsim import Vector3r, Quaternionr, Pose


class Checker:
    def __init__(self, client, index, x, y, z, scale, ori=Quaternionr(0, 0, 0, 1), direction=0, is_check=False):
        self.scale = Vector3r(scale[0], scale[1], scale[2])
        self.direction = direction
        if direction == 1:
            self.ori = Quaternionr(0, 0, 0.7071, 0.7071)
        elif direction == 2:
            self.ori = Quaternionr(0, 0.7071, 0, 0.7071)
        else:
            self.ori = ori
        self.pos = Pose(Vector3r(x, y, z), self.ori)
        self.is_check = is_check
        self.index = index
        self.client = client

    def get_state(self):
        return self.is_check

    def get_index(self):
        return self.index

    def update_ck_state(self, new_state):
        self.is_check = new_state

    def get_ori(self):
        return self.ori


class CrossingChecker(Checker):
    ck_type: str = "crossing"

    def __init__(self, client, index, x, y, z, scale, ori=Quaternionr(0, 0, 0, 1), direction=0, is_check=False):
        Checker.__init__(self, client, index, x, y, z, scale, ori, direction, is_check)
        self.frame_name = (
            self.client.simSpawnObject(object_name="frame" + str(index), asset_name="ck_frame", pose=self.pos,
                                       scale=self.scale))
        self.mid_name = (
            self.client.simSpawnObject(object_name="ck" + str(index), asset_name="ck_mid", pose=self.pos,
                                       scale=self.scale))

    def destroy_mid(self):
        self.client.simDestroyObject(str(self.mid_name))

    def destroy(self):
        self.client.simDestroyObject(str(self.frame_name))
        self.client.simDestroyObject(str(self.mid_name))

    def complete(self):
        self.client.simDestroyObject(str(self.mid_name))
        self.is_check = True

    def get_name(self):
        return self.mid_name, self.frame_name

    def get_mid_name(self):
        return self.mid_name

    def get_frame_name(self):
        return self.frame_name


class PointingChecker(Checker):
    ck_type: str = "pointing"

    def __init__(self, client, index, x, y, z, scale, ori=Quaternionr(0, 0, 0, 1), direction=0, is_check=False):
        Checker.__init__(self, client, index, x, y, z, scale, ori, direction, is_check)
        self.frame_name = None
        self.mid_name = None
        self.lp_name = self.client.simSpawnObject(object_name="ck" + str(index), asset_name="land_point",
                                                  pose=self.pos, scale=self.scale)

    def destroy(self):
        self.client.simDestroyObject(str(self.lp_name))

    def complete(self):
        self.client.simDestroyObject(str(self.lp_name))
        self.is_check = True

    def get_name(self):
        return self.lp_name


class Path:
    path_type = None

    # current check:60mm x 60mm x36mm
    # 60mm = 0.06m = 1 in unreal
    def __init__(self, name, num_of_ck, pos_list, dir_list, scale_list, drone_size: float):
        self.client = airsim.MultirotorClient()
        self.ck_dic = {}
        self.ck_state_list = {}
        self.is_complete = {}
        self.pos_list = pos_list
        self.dir_list = dir_list
        self.scale_list = scale_list
        self.pos_dict: dict = {}
        self.scale_dict: dict = {}
        self.dir_dict: dict = {}
        self.drone_size = drone_size
        self.distance = self.pos_list[0][0] * self.drone_size
        self.width = float(self.scale_list[0][1]) * self.drone_size
        self.num_of_ck = num_of_ck
        self.name = name

    def get_complete_state(self):
        return self.is_complete

    def update_complete_state(self, new_state: bool):
        self.is_complete = new_state

    def get_ck_dic(self):
        return self.ck_dic

    def get_ck_state(self):
        return self.ck_state_list

    def distance_convertor(self, real_dis) -> float:
        return real_dis / self.drone_size

    def get_drone_size(self):
        return self.drone_size

    def set_drone_size(self, size: float):
        self.drone_size = size

    def update_ck_list_state(self, ck_name, new_state: bool):
        self.ck_dic[ck_name].update_ck_state(new_state)
        self.ck_state_list[ck_name] = new_state

    def get_width(self):
        return round(self.width, 2)

    def get_distance(self):
        return round(self.distance, 2)

    def update_distance(self, new_distance: float):
        converted_distance = self.distance_convertor(new_distance)
        difference: float = converted_distance - self.pos_list[0][0]
        for i in self.ck_dic:
            if self.path_type == "crossing":
                self.client.simSetObjectPose(object_name=self.ck_dic[i].get_frame_name(),
                                             pose=airsim.Pose(
                                                 airsim.Vector3r(self.pos_dict[i][0] + difference,
                                                                 self.pos_dict[i][1],
                                                                 self.pos_dict[i][2]),
                                                 self.ck_dic[i].get_ori()))
                self.client.simSetObjectPose(object_name=self.ck_dic[i].get_mid_name(),
                                             pose=airsim.Pose(
                                                 airsim.Vector3r(self.pos_dict[i][0] + difference,
                                                                 self.pos_dict[i][1],
                                                                 self.pos_dict[i][2]),
                                                 self.ck_dic[i].get_ori()))
            else:
                self.client.simSetObjectPose(object_name=self.ck_dic[i].get_name(),
                                             pose=airsim.Pose(
                                                 airsim.Vector3r(self.pos_dict[i][0] + difference,
                                                                 self.pos_dict[i][1],
                                                                 self.pos_dict[i][2]),
                                                 self.ck_dic[i].get_ori()))

        self.distance = new_distance

    def update_width(self, new_width: float):
        converted_width = self.distance_convertor(new_width)
        print(self.scale_dict)
        for i in self.ck_dic:
            if type(self.ck_dic[i]) == CrossingChecker:
                self.client.simSetObjectScale(object_name=self.ck_dic[i].get_frame_name(),
                                              scale_vector=airsim.Vector3r(converted_width, converted_width,
                                                                           self.scale_dict[i][2]))
                self.client.simSetObjectScale(object_name=self.ck_dic[i].get_mid_name(),
                                              scale_vector=airsim.Vector3r(converted_width, converted_width,
                                                                           self.scale_dict[i][2]))
            else:
                self.client.simSetObjectScale(object_name=self.ck_dic[i].get_name(),
                                              scale_vector=airsim.Vector3r(converted_width, converted_width,
                                                                           self.scale_dict[i][2]))

        self.width = new_width
        old_dis = self.get_distance()
        self.update_distance(old_dis+self.get_width()/2)
        self.distance = old_dis

    def destroy_path(self):
        for key in self.ck_dic:
            self.ck_dic[key].destroy()


class CrossingPath(Path):
    path_type = "crossing"

    def __init__(self, drone_size, name=None, pos_list=None, dir_list=None, scale_list=None):
        self.drone_size = drone_size
        Path.__init__(self, "crossing", 1, [(self.distance_convertor(2.5), 0, self.distance_convertor(0.18))], [1],
                      [(self.distance_convertor(1), self.distance_convertor(1), self.distance_convertor(0.8))],
                      drone_size=drone_size)
        # in meter

    def create_path(self):
        for i in range(1, self.num_of_ck + 1):
            temp = CrossingChecker(client=self.client, index=i, x=self.pos_list[i - 1][0], y=self.pos_list[i - 1][1],
                                   z=self.pos_list[i - 1][2], scale=self.scale_list[i - 1],
                                   direction=self.dir_list[i - 1])
            self.pos_dict[temp.get_name()] = self.pos_list[i - 1]
            self.scale_dict[temp.get_name()] = self.scale_list[i - 1]
            self.dir_dict[temp.get_name()] = self.scale_list[i - 1]

            # Checker dict using the mid name as key
            self.ck_dic[temp.get_mid_name()] = temp
            self.ck_state_list[temp.get_mid_name()] = False


class PointingPath(Path):
    path_type = "pointing"

    def __init__(self, drone_size, name=None, pos_list=None, scale_list=None, ):
        self.drone_size = drone_size
        Path.__init__(self, "pointing", 1, [(self.distance_convertor(2), 0, 0.95)], [0],
                      [(self.distance_convertor(0.4), self.distance_convertor(0.4), self.distance_convertor(0.01))],
                      drone_size=drone_size)

    def create_path(self):
        for i in range(1, self.num_of_ck + 1):
            temp = PointingChecker(self.client, index=i, x=self.pos_list[i - 1][0], y=self.pos_list[i - 1][1],
                                   z=self.pos_list[i - 1][2], scale=self.scale_list[i - 1], direction=self.dir_list)
            self.pos_dict[temp.get_name()] = self.pos_list[i - 1]
            self.scale_dict[temp.get_name()] = self.scale_list[i - 1]
            self.dir_dict[temp.get_name()] = self.scale_list[i - 1]
            self.ck_dic[temp.get_name()] = temp
            self.ck_state_list[temp.get_name()] = False
