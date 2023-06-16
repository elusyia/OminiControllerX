import pygame
import json

config = json.load(open("src/config.json", "r"))
# config = json.load(open("config.json", "r"))
SUPPORTED_GAMEPAD = ["Controller (Xbox One For Windows)"]

class Gamepad:
    def __init__(self):
        NO_SUPPORT_GAMEPAD = True
        self.joystick = None
        pygame.init()
        pygame.joystick.init()
        joystick_count = pygame.joystick.get_count()
        try:
            if joystick_count == 0:
                print("No gamepads detected. Please connect a gamepad to your device.")
            else:
                # for each gamepad, print out its info
                for i in range(joystick_count):
                    self.joystick = pygame.joystick.Joystick(i)
                    self.joystick.init()
                    print(f"Gamepad{i} detected:")
                    print("  Name:", self.joystick.get_name())
                    print("  ID:", self.joystick.get_id())
                    if self.joystick.get_name() in SUPPORTED_GAMEPAD:
                        NO_SUPPORT_GAMEPAD = False
                    self.joystick.quit()
                if NO_SUPPORT_GAMEPAD:
                    print("No supported gamepads detected. Connect to gamepad 0 anyway")
                    self.joystick = pygame.joystick.Joystick(0)
                    self.joystick.init()
        except Exception as e:
            print(f"Controller not available: {e}")
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
            "0": 2,  # A
            "1": 2,  # B
            "2": 2,  # X
            "3": 2,  # Y
            "4": 2,  # LB
            "5": 2,  # RB
            "6": 0,  # back
            "7": 0,  # start
            "8": 0,  # left stick
            "9": 0,  # right stick
        }

    def fix_zero_drift(self, value):
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
        if not self.button_state["4"] and not self.button_state["5"]:
            self.button_state["10"] = False
            self.button_state["11"] = False
            self.button_state["12"] = False
            self.button_state["13"] = False
        for event in pygame.event.get():
            if event.type == pygame.JOYDEVICEADDED:
                if (
                    pygame.joystick.Joystick(event.device_index).get_name()
                    in SUPPORTED_GAMEPAD
                ):  # if gamepad is xbox one controller
                    self.joystick = pygame.joystick.Joystick(event.device_index)
                    self.joystick.init()
                    print("Supported gamepad connected:", self.joystick.get_name())
            elif event.type == pygame.JOYDEVICEREMOVED:
                print("Gamepad disconnected.")
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
                if event.value == (0, 1):  # joyhat up
                    self.button_state["10"] = True
                elif event.value == (0, -1):  # joyhat down
                    self.button_state["11"] = True
                elif event.value == (-1, 0):  # joyhat left
                    self.button_state["12"] = True
                elif event.value == (1, 0):  # joyhat right
                    self.button_state["13"] = True
                else:
                    self.button_state["10"] = False
                    self.button_state["11"] = False
                    self.button_state["12"] = False
                    self.button_state["13"] = False
