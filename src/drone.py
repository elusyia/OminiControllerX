from driver.gamepad import Gamepad
import pygame
import numpy as np
from scipy.spatial.transform import Rotation as R

NORMAL_SPEED_FILTER = np.array([0.05, 0.05, 0.05])
NORMAL_ROT_FILTER = np.array([0.02, 0.02, 0.02])
SLOW_SPEED_FILTER = np.array([0.3, 0.3, 0.3])
ZOOM_SPEED = 0.005
EXPOSURE_SPEED = 0.01
APERTURE_SPEED = 0.002
FOCUS_SPEED = 0.01

def constrain(x: float, min_value: float = 0, max_value: float = 1) -> float:
    return max(min_value, min(max_value, x))

class Drone(Gamepad):
    def __init__(self):
        super().__init__()
        self.ENABLE = False
        self.SLOWMODE = False
        self.AF = True
        self.ZOOM_APERTURE_TUNNER = False
        # self.CRUISE_COUNTROL = False
        # self.cruise_pos_diff = np.array([0, 0, 0])
        # self.cruise_rot_diff = np.array([0, 0, 0])
        # self.variable_list = []
        self.pre_pos = np.array([0, 0, 0])
        self.pre_rot = np.array([0, 0, 0])
        self.pos = np.array([0, 0, 0])  # in meter
        self.rot = np.array([0, 0, 0])  # in rad
        # lens parameters
        self.zoom = 0.3
        self.exposure = 0.5
        self.aperture = 0.17
        self.focus = 0.0
        # filter list that storage filter function handle
        # self.pre_pos_filter_list = []
        # self.pre_rot_filter_list = []
        # self.after_pos_filter_list = []
        # self.after_rot_filter_list = []
        # self.button_func_list = []
        # for i in range(len(self.event_dict)):
        #     self.pre_pos_filter_list.append([])
        #     self.pre_rot_filter_list.append([])
        #     self.after_pos_filter_list.append([])
        #     self.after_rot_filter_list.append([])
        #     self.button_func_list.append([])

    def __repr__(self):
        return (
            "State: "
            + str(self.ENABLE)
            + "Position: "
            + str(self.pos)
            + "Rotation: "
            + str(self.rot)
            + "Button: "
            + str(self.button_state)
            + "Time: "
            + str(self.t)
        )

    def start(self):
        self.ENABLE = True

    def stop(self):
        self.ENABLE = False

    def toggle_start(self):
        self.ENABLE = not self.ENABLE
        if self.ENABLE:
            self.stop()
        else:
            self.start()

    def is_started(self):
        return self.ENABLE

    def staet_slow_mode(self):
        self.SLOWMODE = True

    def stop_slow_mode(self):
        self.SLOWMODE = False

    def is_slow_mode(self):
        return self.SLOWMODE

    def start_zoom_aperture_tunner(self):
        self.ZOOM_APERTURE_TUNNER = True

    def stop_zoom_aperture_tunner(self):
        self.ZOOM_APERTURE_TUNNER = False

    # def start_cruise_control(self):
    #     self.CRUISE_COUNTROL = True
    #     self.cruise_pos_diff = self.pos_diff
    #     self.cruise_rot_diff = self.rot_diff

    # def stop_cruise_control(self):
    #     self.CRUISE_COUNTROL = False

    # def toggle_cruise_control(self):
    #     self.CRUISE_COUNTROL = not self.CRUISE_COUNTROL
    #     if self.CRUISE_COUNTROL:
    #         self.cruise_pos_diff = np.array([-self.raw.x, self.raw.z, self.raw.y])
    #         self.cruise_rot_diff = np.array([self.raw.pitch, -self.raw.yaw, self.raw.roll])

    def __calc_position(self):
        self.pre_pos = self.pos
        rotation_matrix = R.from_euler(
            "xyz", self.rot
        ).as_matrix()  # calculate rotation matrix
        pos_diff = np.transpose(
            np.matmul(rotation_matrix, np.transpose(self.pos_diff))
        )  # 对位移误差进行左乘旋转矩阵,得到当前旋转下的位移在原空间中的数值
        self.pos = self.pos + np.multiply(pos_diff, NORMAL_SPEED_FILTER)

    # TODO: 待修改
    def __calc_rotation(self):
        self.pre_rot = self.rot
        self.rot = self.rot + np.multiply(
            self.rot_diff, NORMAL_ROT_FILTER
        )  # rot alone y-x-z
        self.rot = np.mod(self.rot, 2 * np.pi)  # get dicimal part

    def reset(self):
        self.pre_pos = np.array([0, 0, 0])
        self.pre_rot = np.array([0, 0, 0])
        self.pos = np.array([0, 0, 0])  # in meter
        self.rot = np.array([0, 0, 0])  # in rad
        self.zoom = 0.3
        self.exposure = 0.5
        self.aperture = 0.17
        self.focus = 0.0
        self.AF = True

    def clear_pos(self):
        self.pre_pos = np.array([0, 0, 0])
        self.pos = np.array([0, 0, 0])

    def clear_rot(self):
        self.pre_rot = np.array([0, 0, 0])
        self.rot = np.array([0, 0, 0])

    def clear_pos_rot(self):
        self.clear_pos()
        self.clear_rot()

    def update(self):
        super().update()
        if self.ENABLE:  # if is True, stop process

            if self.SLOWMODE:  # if left stick is pressed, enable fast mode
                self.pos_diff = np.multiply(self.pos_diff, SLOW_SPEED_FILTER)

            self.__calc_position()  # update position
            if (
                not self.ZOOM_APERTURE_TUNNER
            ):  # stop update rotation when variable tunner is on
                self.__calc_rotation()  # update rotation
            else:
                self.joystick.rumble(abs(self.rot_diff[0])/20, abs(self.rot_diff[0])/20, 1)
                # calc zoom
                self.zoom = self.zoom - self.rot_diff[0] * ZOOM_SPEED
                self.zoom = constrain(self.zoom)
                # calc aperture
                self.aperture = self.aperture - self.rot_diff[1] * APERTURE_SPEED
                self.aperture = constrain(self.aperture)




if __name__ == "__main__":
    drone = Drone()

    while True:
        drone.update()
        print(
            "Position: "
            + str(drone.pos)
            + "Rotation: "
            + str(drone.rot)
            + "Button: "
            + str(drone.button_state)
            + "Time: "
            + str(drone.t),
            end="     \r",
        )
        pygame.time.wait(16)  # 60Hz
