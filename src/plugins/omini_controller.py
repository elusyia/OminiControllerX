import time
from pythonosc import udp_client
import numpy as np

class OminiController:
    def __init__(self, osc_client: udp_client.SimpleUDPClient):
        self.osc_client = osc_client
        self.positions = np.zeros(3)
        self.posRough = np.zeros(3)
        self.posFine = np.zeros(3)
        self.rotation = np.zeros(3)
        self.DELTA = 0.007874015748031497
        self.RANGE = 250

    def __quantiPos(self, pos: np.ndarray) -> tuple: # vrchat use only 8bit float, so quantize pos to 2 8bit float overlapped to increase precision
        pos = pos / self.RANGE # normalize pos to -1 to 1
        pos_rough = np.round(pos / self.DELTA) * self.DELTA # quantize pos to rough and fine
        e = (pos - pos_rough) / (self.DELTA / 2)
        pos_fine = np.round(e / self.DELTA) * self.DELTA
        return (pos_rough, pos_fine)

    def __space_conversion(self, pos: np.ndarray, rot: np.ndarray): # change to left hand coordinate system
        self.positions[0] = -pos[0]
        self.positions[1] = pos[1]
        self.positions[2] = pos[2]
        self.posRough, self.posFine = self.__quantiPos(self.positions)

        self.rotation[0] = rot[0]
        self.rotation[1] = 2 * np.pi - rot[1]
        self.rotation[2] = 2 * np.pi - rot[2]
        self.rotation = self.rotation / np.pi - 1

    def sync_state(self, pos: np.ndarray, rot: np.ndarray):
        self.__space_conversion(pos, rot)
        self.osc_client.send_message("/avatar/parameters/Omini.X", self.posRough[0])
        self.osc_client.send_message("/avatar/parameters/Omini.XFine", self.posFine[0])
        self.osc_client.send_message("/avatar/parameters/Omini.Y", self.posRough[1])
        self.osc_client.send_message("/avatar/parameters/Omini.YFine", self.posFine[1])
        self.osc_client.send_message("/avatar/parameters/Omini.Z", self.posRough[2])
        self.osc_client.send_message("/avatar/parameters/Omini.ZFine", self.posFine[2])

        self.osc_client.send_message("/avatar/parameters/Omini.Pitch", self.rotation[0])
        self.osc_client.send_message("/avatar/parameters/Omini.Yaw", self.rotation[1])
        self.osc_client.send_message("/avatar/parameters/Omini.Roll", self.rotation[2])

    def reset(self):
        self.osc_client.send_message("/avatar/parameters/Omini.Reset", True)
        time.sleep(0.1)
        self.osc_client.send_message("/avatar/parameters/Omini.Reset", False)
        time.sleep(0.1)

    def change_target(self):
        self.osc_client.send_message("/avatar/parameters/Omini.ChangeTarget", True)
        time.sleep(0.1)
        self.osc_client.send_message("/avatar/parameters/Omini.ChangeTarget", False)
        time.sleep(0.1)

    def smooth(self):
        self.osc_client.send_message("/avatar/parameters/Omini.Smooth", True)
        time.sleep(0.1)
        self.osc_client.send_message("/avatar/parameters/Omini.Smooth", False)
        time.sleep(0.1)

    def follow(self):
        self.osc_client.send_message("/avatar/parameters/Omini.Follow", True)
        time.sleep(0.1)
        self.osc_client.send_message("/avatar/parameters/Omini.Follow", False)
        time.sleep(0.1)
