import airsim
from airsim import Vector3r


class DroneEnvParameterController:
    def __init__(self, client: airsim.MultirotorClient):
        self.key_to_ref_map = {1: airsim.WeatherParameter.Rain, 2: airsim.WeatherParameter.Snow,
                               3: airsim.WeatherParameter.Dust,
                               4: airsim.WeatherParameter.Fog, 5: 5}
        self.key_val_map = {1: 0, 2: 0, 3: 0, 4: 0, 5: [0, 0, 0]}
        self.client = client

    def update_env_setting(self, key: int, val):
        if self.key_to_ref_map.get(key) is None:
            return False
        else:
            self.key_val_map[key] = val
            if key in range(1, 5):
                self.client.simSetWeatherParameter(self.key_to_ref_map[key], self.key_val_map[key])
            elif key == 5:
                self.client.simSetWind(
                    Vector3r(self.key_val_map[5][0], self.key_val_map[5][1], self.key_val_map[5][2]))
            return True

    def get_env_setting(self):
        return self.key_val_map
