import pygame
import numpy as np
import time

class Gamepad:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        joystick_count = pygame.joystick.get_count()
        try:
            if joystick_count == 0:
                print("No gamepads detected.")
            else:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
            print("Initialized gamepad:", self.joystick.get_name())
        except Exception as e:
            print(f"Controller not available: {e}")
        self.pos_diff = np.array([0, 0, 0])
        self.rot_diff = np.array([0, 0, 0])
        self.pre_pos_diff = np.array([0, 0, 0])
        self.pre_rot_diff = np.array([0, 0, 0])
        self.t = 0
        self.button_state = {
            "0": False,  # A
            "1": False,  # B
            "2": False,  # X
            "3": False,  # Y
            "4": False,  # LB
            "5": False,  # RB
            "6": False,  # back
            "7": False,  # start
            "8": False,  # left stick
            "9": False,  # right stick
            "10": False,  # joyhat up
            "11": False,  # joyhat down
            "12": False,  # joyhat left
            "13": False,  # joyhat right
        }
        self.button_type = {  # 0: key, 1: toggle, 2: push to activate
            "0": 0,  # A
            "1": 0,  # B
            "2": 0,  # X
            "3": 0,  # Y
            "4": 2,  # LB
            "5": 2,  # RB
            "6": 1,  # back
            "7": 1,  # start
            "8": 0,  # left stick
            "9": 0,  # right stick
            # "10": 0,  # joyhat up
            # "11": 0,  # joyhat down
            # "12": 0,  # joyhat left
            # "13": 0,  # joyhat right
        }

    def __repr__(self):
        return "Position Differential: "+ str(self.pos_diff)+ "Rotation Differential: " + str(self.rot_diff) + "Button: " + str(self.button_state) + "Time: " + str(self.t)

    def __zero_drift(self, value):
        if abs(value) < 0.08:
            return 0
        else:
            return value

    def update(self):
        """update state"""
        for button in self.button_type:
            if (
                self.button_type[button] == 0
            ):  # if button type is key then set state to False every time
                self.button_state[button] = False
        # for joyhat, set state to False every time
        self.button_state["10"] = False
        self.button_state["11"] = False
        self.button_state["12"] = False
        self.button_state["13"] = False
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                # print("Button", event.button, "pressed.")
                pass
                if self.button_type[str(event.button)] == 0:  # key
                    self.button_state[str(event.button)] = True
                elif self.button_type[str(event.button)] == 1:  # toggle
                    self.button_state[str(event.button)] = not self.button_state[
                        str(event.button)
                    ]
                elif self.button_type[str(event.button)] == 2:  # push to activate
                    self.button_state[str(event.button)] = True
            elif event.type == pygame.JOYBUTTONUP:
                # print("Button", event.button, "released.")
                pass
                if self.button_type[str(event.button)] == 0:  # key
                    self.button_state[str(event.button)] = False
                elif self.button_type[str(event.button)] == 1:  # toggle
                    pass
                elif self.button_type[str(event.button)] == 2:  # push to activate
                    self.button_state[str(event.button)] = False
            elif event.type == pygame.JOYAXISMOTION:
                # print("Joystick axis", event.axis, "moved to", event.value)
                pass
            elif event.type == pygame.JOYHATMOTION:
                # print("Joystick hat", event.hat, "moved to", event.value)
                pass
                if event.value == (0, 1): # joyhat up
                    self.button_state["10"] = True
                elif event.value == (0, -1): # joyhat down
                    self.button_state["11"] = True
                elif event.value == (-1, 0): # joyhat left
                    self.button_state["12"] = True
                elif event.value == (1, 0): # joyhat right
                    self.button_state["13"] = True
                
        self.t = time.perf_counter()
        self.pre_pos_diff = self.pos_diff
        self.pre_rot_diff = self.rot_diff
        self.pos_diff = np.array(
            [
                self.__zero_drift(-self.joystick.get_axis(0)),
                (-self.joystick.get_axis(4) + self.joystick.get_axis(5)) / 2,
                self.__zero_drift(-self.joystick.get_axis(1)),
            ]
        )
        self.rot_diff = np.array(
            [
                self.__zero_drift(self.joystick.get_axis(3)),
                self.__zero_drift(-self.joystick.get_axis(2)),
                0,
            ]
        )


if __name__ == "__main__":
    controller = Gamepad()
    while True:
        controller.update()
        print(
            controller,
            end="     \r",
        )
        pygame.time.wait(16)  # 60Hz
