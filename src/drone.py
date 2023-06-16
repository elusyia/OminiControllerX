from driver.gamepad import Gamepad
import numpy as np
from scipy.spatial.transform import Rotation as R
import json
import time

config = json.load(open("src\config.json", "r"))
# config = json.load(open("config.json", "r"))

NORMAL_SPEED_FILTER = np.array([0.05, 0.05, 0.05]) * config["normal_mov_speed"]
NORMAL_ROT_FILTER = np.array([0.02, 0.02, 0.02]) * config["normal_rot_speed"]
# ALT_SPEED_FILTER = np.array([1, 1, 1]) * config["alt_mov_speed"]
# ALT_ROT_FILTER = np.array([1, 1, 1]) * config["alt_rot_speed"]
ZOOM_SPEED = 0.003 * config["zoom_speed"]
EXPOSURE_SPEED = 0.003 * config["exposure_speed"]
APERTURE_SPEED = 0.003 * config["aperture_speed"]
FOCUS_SPEED = 0.003 * config["focus_speed"]


def constrain(x: float, min_value: float = 0, max_value: float = 1) -> float:
    return max(min_value, min(max_value, x))

def normalize(v):
    return v/np.linalg.norm(v)


class Drone(Gamepad):
    def __init__(self):
        super().__init__()
        self.ENABLE = False
        self.FLY_MODE = config["fly_mode"]  # "fpv" or "drone"
        self.CONTROL_MODE = config["control_mode"]  # "game" or "japan" or "american" or "china"
        self.LB_CONTROL_LAYER = False
        self.RB_CONTROL_LAYER = False
        # self.ALT_MOVE_MODE = False
        self.FOCUS_DROPED = False
        self.focus_pos = np.zeros(3)
        self.pos_diff = np.zeros(3)
        self.rot_diff = np.zeros(3)
        self.pre_pos_diff = np.zeros(3)
        self.pre_rot_diff = np.zeros(3)
        self.current_pos = 0
        self.pos = np.array(
            [np.zeros(3), np.zeros(3), np.zeros(3), np.zeros(3)]
        )  # 4 positions
        self.rot = np.array(
            [np.zeros(3), np.zeros(3), np.zeros(3), np.zeros(3)]
        )  # 4 rotations
        self.pre_pos = np.array(
            [np.zeros(3), np.zeros(3), np.zeros(3), np.zeros(3)]
        )  # 4 positions
        self.pre_rot = np.array(
            [np.zeros(3), np.zeros(3), np.zeros(3), np.zeros(3)]
        )  # 4 rotations
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

    # def staet_alt_move_mode(self):
    #     self.ALT_MOVE_MODE = True

    # def stop_alt_move_mode(self):
    #     self.ALT_MOVE_MODE = False

    # def is_alt_move_mode(self):
    #     return self.ALT_MOVE_MODE

    def start_lb_control(self):
        self.LB_CONTROL_LAYER = True

    def stop_lb_control(self):
        self.LB_CONTROL_LAYER = False

    def start_rb_control(self):
        self.RB_CONTROL_LAYER = True

    def stop_rb_control(self):
        self.RB_CONTROL_LAYER = False

    def is_alt_control(self):
        return self.LB_CONTROL_LAYER and self.RB_CONTROL_LAYER
    
    def __map_stick_data(self, control_mode:str):
        if control_mode == "japan":
            self.pos_diff = np.array(
                [
                    self.fix_zero_drift(-self.joystick.get_axis(2)),
                    self.fix_zero_drift(-self.joystick.get_axis(3)),
                    self.fix_zero_drift(-self.joystick.get_axis(1)),
                ]
            )
            self.rot_diff = np.array(
                [
                    (self.joystick.get_axis(4) - self.joystick.get_axis(5)) / 2,
                    self.fix_zero_drift(-self.joystick.get_axis(0)),
                    (-self.joystick.get_axis(4) + self.joystick.get_axis(5)) / 2,
                ]
            )
        elif control_mode == "american":
            self.pos_diff = np.array(
                [
                    self.fix_zero_drift(-self.joystick.get_axis(2)),
                    self.fix_zero_drift(-self.joystick.get_axis(1)),
                    self.fix_zero_drift(-self.joystick.get_axis(3)),
                ]
            )
            self.rot_diff = np.array(
                [
                    (self.joystick.get_axis(4) - self.joystick.get_axis(5)) / 2,
                    self.fix_zero_drift(-self.joystick.get_axis(0)),
                    (-self.joystick.get_axis(4) + self.joystick.get_axis(5)) / 2,
                ]
            )
        elif control_mode == "china":
            self.pos_diff = np.array(
                [
                    self.fix_zero_drift(-self.joystick.get_axis(0)),
                    self.fix_zero_drift(-self.joystick.get_axis(3)),
                    self.fix_zero_drift(-self.joystick.get_axis(1)),
                ]
            )
            self.rot_diff = np.array(
                [
                    (self.joystick.get_axis(4) - self.joystick.get_axis(5)) / 2,
                    self.fix_zero_drift(-self.joystick.get_axis(2)),
                    (-self.joystick.get_axis(4) + self.joystick.get_axis(5)) / 2,
                ]
            )
        elif control_mode == "game":
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
        else:
            raise ValueError("Invalid control mode")

    def __calc_position(self):
        self.pre_pos[self.current_pos] = self.pos[self.current_pos]
        if self.FLY_MODE == "fpv":
            rotation_matrix = R.from_euler(
                "xyz", self.rot[self.current_pos]
            ).as_matrix()  # calculate rotation matrix
        elif self.FLY_MODE == "drone":
            rotation_matrix = R.from_euler(
                "xyz", self.rot[self.current_pos] * np.array([0, 1, 0])
            ).as_matrix()
        else:
            raise ValueError("Invalid mode")
        pos_diff = np.transpose(
            np.matmul(rotation_matrix, np.transpose(self.pos_diff))
        )  # 对位移误差进行左乘旋转矩阵,得到当前旋转下的位移在原空间中的数值
        self.pos[self.current_pos] = self.pos[self.current_pos] + np.multiply(
            pos_diff, NORMAL_SPEED_FILTER
        )

    # TODO: 待修改
    def __calc_rotation(self):
        self.pre_rot[self.current_pos] = self.rot[self.current_pos]
        self.rot[self.current_pos] = self.rot[self.current_pos] + np.multiply(
            self.rot_diff, NORMAL_ROT_FILTER
        )  # rot alone y-x-z
        self.rot[self.current_pos] = np.mod(
            self.rot[self.current_pos], 2 * np.pi
        )  # get dicimal part

    def __rot_tract_to(obj_pos, obj_rot, focus_pos):
        if (obj_pos == focus_pos).all():
            return obj_rot
        # Compute object-to-focus vector
        focus_vector = focus_pos - obj_pos
        yaw = np.arctan2(focus_vector[0], focus_vector[2])
        # Compute pitch (rotation around X-axis)
        pitch = np.arctan2(-focus_vector[1], np.sqrt(focus_vector[0]**2 + focus_vector[2]**2))
        # Adjust the current rotation by the computed yaw and pitch
        new_rot = np.array([pitch, yaw, 0])
        new_rot = np.mod(new_rot+2*np.pi, 2*np.pi)
        return new_rot
    
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

    def drop_collect_focus(self):
        if self.FOCUS_DROPED:
            self.focus_pos = np.zeros(3)
            self.FOCUS_DROPED = False
        else:
            self.focus_pos = self.pos[self.current_pos].copy()
            self.FOCUS_DROPED = True

    def update(self):
        super().update()

        if self.ENABLE:  # if is True, stop process
            self.t = time.perf_counter()
            self.pre_pos_diff = self.pos_diff
            self.pre_rot_diff = self.rot_diff
            self.__map_stick_data(self.CONTROL_MODE)

            # if self.ALT_MOVE_MODE:  # if alternative move mode
            #     self.pos_diff = np.multiply(self.pos_diff, ALT_SPEED_FILTER)
            #     self.rot_diff = np.multiply(self.rot_diff, ALT_ROT_FILTER)

            if self.LB_CONTROL_LAYER:
                if self.CONTROL_MODE == "game":
                    self.pos_diff *= np.array([1, 0, 1])
                    self.rot_diff *= np.array([1, 1, 1])
                else:
                    self.pos_diff *= np.array([1, 1, 1])
                    self.rot_diff *= np.array([0, 1, 1])
                self.__calc_position()  # update position not update rotation
                self.__calc_rotation()  # update rotation not update position
                # calc zoom
                if self.button_state["0"]:
                    self.joystick.rumble(0.1, 0.1, 1)
                    self.zoom = self.zoom - ZOOM_SPEED
                    self.zoom = constrain(self.zoom)
                if self.button_state["3"]:
                    self.joystick.rumble(0.1, 0.1, 1)
                    self.zoom = self.zoom + ZOOM_SPEED
                    self.zoom = constrain(self.zoom)
                # calc aperture
                if self.button_state["2"]:
                    self.joystick.rumble(0.1, 0.1, 1)
                    self.aperture = self.aperture - APERTURE_SPEED
                    self.aperture = constrain(self.aperture)
                if self.button_state["1"]:
                    self.joystick.rumble(0.1, 0.1, 1)
                    self.aperture = self.aperture + APERTURE_SPEED
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

            elif self.RB_CONTROL_LAYER:
                self.pos_diff *= np.array([1, 1, 1])
                self.rot_diff *= np.array([1, 1, 0])
                self.__calc_position()  # update position
                self.__calc_rotation()  # update rotation

            else:
                self.pos_diff *= np.array([1, 1, 1])
                self.rot_diff *= np.array([1, 1, 0])
                self.__calc_position()  # update position
                self.__calc_rotation()  # update rotation

            if self.FOCUS_DROPED: # focus droped, recalculate rotation point to focus point
                self.rot[self.current_pos] = self.__rot_tract_to(self.pos[self.current_pos], self.rot[self.current_pos], self.focus_pos)