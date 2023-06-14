from driver.gamepad import Gamepad
import pygame
import numpy as np
from scipy.spatial.transform import Rotation as R
import json
import time

config = json.load(open("src\config.json", "r"))

NORMAL_SPEED_FILTER = np.array([0.05, 0.05, 0.05]) * config["normal_mov_speed"]
NORMAL_ROT_FILTER = np.array([0.02, 0.02, 0.02]) * config["normal_rot_speed"]
ALT_SPEED_FILTER = np.array([1, 1, 1]) * config["alt_mov_speed"]
ALT_ROT_FILTER = np.array([1, 1, 1]) * config["alt_rot_speed"]
ZOOM_SPEED = 0.005 * config["zoom_speed"]
EXPOSURE_SPEED = 0.003 * config["exposure_speed"]
APERTURE_SPEED = 0.002 * config["aperture_speed"]
FOCUS_SPEED = 0.002 * config["focus_speed"]


def constrain(x: float, min_value: float = 0, max_value: float = 1) -> float:
    return max(min_value, min(max_value, x))


class Drone(Gamepad):
    def __init__(self):
        super().__init__()
        self.ENABLE = False
        self.MODE = config["mode"] # "fpv" or "drone"
        self.ALT_MOVE_MODE = False
        self.ALT_CONTROL_LAYER = False
        # self.CRUISE_COUNTROL = False
        # self.cruise_pos_diff = np.zeros(3)
        # self.cruise_rot_diff = np.zeros(3)
        self.pos_diff = np.zeros(3)
        self.rot_diff = np.zeros(3)
        self.pre_pos_diff = np.zeros(3)
        self.pre_rot_diff = np.zeros(3)
        # self.pos = np.zeros(3)  # in meter
        # self.rot = np.zeros(3)  # in rad
        self.current_pos = 0
        self.pos = np.array([np.zeros(3), np.zeros(3), np.zeros(3), np.zeros(3)])  # 4 positions
        self.rot = np.array([np.zeros(3), np.zeros(3), np.zeros(3), np.zeros(3)])  # 4 rotations
        # self.pre_pos = np.zeros(3)
        # self.pre_rot = np.zeros(3)
        self.pre_pos = np.array([np.zeros(3), np.zeros(3), np.zeros(3), np.zeros(3)])  # 4 positions
        self.pre_rot = np.array([np.zeros(3), np.zeros(3), np.zeros(3), np.zeros(3)])  # 4 rotations
        # lens parameters
        self.zoom = 0.3
        self.exposure = 0.5
        self.aperture = 0.17
        self.focus = 0.0

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

    def staet_alt_move_mode(self):
        self.ALT_MOVE_MODE = True

    def stop_alt_move_mode(self):
        self.ALT_MOVE_MODE = False

    def is_alt_move_mode(self):
        return self.ALT_MOVE_MODE

    def start_alt_control(self):
        self.ALT_CONTROL_LAYER = True

    def stop_alt_control(self):
        self.ALT_CONTROL_LAYER = False

    def is_alt_control(self):
        return self.ALT_CONTROL_LAYER

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
        self.pre_pos[self.current_pos] = self.pos[self.current_pos]
        if self.MODE == "fpv":
            rotation_matrix = R.from_euler(
                "xyz", self.rot[self.current_pos]
            ).as_matrix()  # calculate rotation matrix
        elif self.MODE == "drone":
            rotation_matrix = R.from_euler(
                "xyz", self.rot[self.current_pos]*np.array([0, 1, 0])
            ).as_matrix()
        else:
            raise ValueError("Invalid mode")
        pos_diff = np.transpose(
            np.matmul(rotation_matrix, np.transpose(self.pos_diff))
        )  # 对位移误差进行左乘旋转矩阵,得到当前旋转下的位移在原空间中的数值
        self.pos[self.current_pos] = self.pos[self.current_pos] + np.multiply(pos_diff, NORMAL_SPEED_FILTER)
        
    # TODO: 待修改
    def __calc_rotation(self):
        self.pre_rot[self.current_pos] = self.rot[self.current_pos]
        self.rot[self.current_pos] = self.rot[self.current_pos] + np.multiply(
            self.rot_diff, NORMAL_ROT_FILTER
        )  # rot alone y-x-z
        self.rot[self.current_pos] = np.mod(self.rot[self.current_pos], 2 * np.pi)  # get dicimal part

    def reset(self):
        self.clear_pos_rot()
        self.zoom = 0.3
        self.exposure = 0.5
        self.aperture = 0.17
        self.focus = 0.0

    def change_to_pos_0(self):
        self.current_pos = 0

    def change_to_pos_1(self):
        self.current_pos = 1

    def change_to_pos_2(self):
        self.current_pos = 2

    def change_to_pos_3(self):
        self.current_pos = 3

    def clear_pos(self):
        self.pos[self.current_pos] = np.zeros(3)
        self.pre_pos[self.current_pos] = np.zeros(3)

    def clear_rot(self):
        self.rot[self.current_pos] = np.zeros(3)
        self.pre_rot[self.current_pos] = np.zeros(3)

    def clear_pos_rot(self):
        self.clear_pos()
        self.clear_rot()

    def update(self):
        super().update()


        if self.ENABLE:  # if is True, stop process
            self.t = time.perf_counter()
            self.pre_pos_diff = self.pos_diff
            self.pre_rot_diff = self.rot_diff
            self.pos_diff = np.array(
                [
                    self.fix_zero_drift(-self.joystick.get_axis(0)),
                    (-self.joystick.get_axis(4) + self.joystick.get_axis(5)) / 2,
                    self.fix_zero_drift(-self.joystick.get_axis(1)),
                ]
            )
            self.rot_diff = np.array(
                [
                    self.fix_zero_drift(self.joystick.get_axis(3)),
                    self.fix_zero_drift(-self.joystick.get_axis(2)),
                    (-self.joystick.get_axis(4) + self.joystick.get_axis(5)) / 2,
                ]
            )


            if self.ALT_MOVE_MODE:  # if alternative move mode
                self.pos_diff = np.multiply(self.pos_diff, ALT_SPEED_FILTER)
                self.rot_diff = np.multiply(self.rot_diff, ALT_ROT_FILTER)


            if self.ALT_CONTROL_LAYER:
                self.pos_diff *= np.array([1, 0, 1])
                self.rot_diff *= np.array([0, 0, 1])
                self.__calc_position()  # update position not update rotation
                self.__calc_rotation()  # update rotation not update position
                # calc zoom
                self.joystick.rumble(
                    abs(self.joystick.get_axis(3)) / 20, abs(self.joystick.get_axis(3)) / 20, 1
                )
                self.zoom = self.zoom - self.fix_zero_drift(self.joystick.get_axis(3)) * ZOOM_SPEED
                self.zoom = constrain(self.zoom)
                # calc aperture
                self.aperture = self.aperture - self.fix_zero_drift(-self.joystick.get_axis(2)) * APERTURE_SPEED
                self.aperture = constrain(self.aperture)
                # calc exposure
                if self.button_state["12"]:
                    self.joystick.rumble(0.1, 0.1, 1)
                    self.exposure = self.exposure - EXPOSURE_SPEED
                    self.exposure = constrain(self.exposure)
                if self.button_state["13"]:
                    self.joystick.rumble(0.1, 0.1, 1)
                    self.exposure = self.exposure + EXPOSURE_SPEED
                    self.exposure = constrain(self.exposure)
                # calc focus
                if self.button_state["10"]:
                    self.joystick.rumble(0.1, 0.1, 1)
                    self.focus = self.focus + FOCUS_SPEED
                    self.focus = constrain(self.focus, 0.0, 0.99)
                if self.button_state["11"]:
                    self.joystick.rumble(0.1, 0.1, 1)
                    self.focus = self.focus - FOCUS_SPEED
                    self.focus = constrain(self.focus, 0.0, 0.99)


            else:
                self.pos_diff *= np.array([1, 1, 1])
                self.rot_diff *= np.array([1, 1, 0])
                self.__calc_position()  # update position
                self.__calc_rotation()  # update rotation


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
