from drone import Drone
from plugins.vrclens import VRCLens
from plugins.omini_controller import OminiController
from plugins.user_avatar import Avatar
from pythonosc import udp_client
import time
import pygame
import json


""" 可调整的变量
"""
# SYSTEM_EVALUATION_CYCLE_TIME = 0.05  # The loop time of the whole system, do not change it unless you know what you are doing. It will also effect the sample speed of the system, which will make the camera move faster or slower.
# RECORD_VOLUME = 10000
# RECORDING = False
config = json.load(open("src/config.json", "r"))
OSC_ADRESS = config["osc_adress"]
OSC_PORT = config["osc_port"]
TARGET_FPS = 60

""" 录制
"""

# class RecordTape:
#     volume = RECORD_VOLUME

#     def __init__(self):
#         self.rec_point = []

#     def init_tape(self):
#         self.rec_point = []

#     def add_rec_point(self, pos, rot, t_diff):
#         if len(self.rec_point) < self.volume:
#             self.rec_point.append((pos, rot, t_diff))

#     def replay(self, client: VRC_UAVCam_Client):
#         for i in range(len(self.rec_point)):
#             pos, rot, t_diff = self.rec_point[i]
#             client.omini_sync_state(pos, rot)
#             time.sleep(t_diff + 5 / 1000)


# def start_record():
#     global RECORDING
#     global tape
#     RECORDING = True
#     tape.init_tape()
#     print("start recording")


# def stop_record():
#     global RECORDING
#     RECORDING = False
#     print("stop recording")


# def toggle_record():
#     global RECORDING
#     if RECORDING:
#         stop_record()
#     else:
#         start_record()


# def replay_record():
#     global tape
#     tape.replay(vrc_client)
#     print("replay finished")

# tape = RecordTape()

if __name__ == "__main__":
    """Get Instances"""
    osc_client = udp_client.SimpleUDPClient(OSC_ADRESS, OSC_PORT)
    drone = Drone()
    omini = OminiController(osc_client)
    vrcl = VRCLens(osc_client)
    avatar = Avatar(osc_client)

    """Button functions register map
    """
    button_func_map = {
        "0": [[avatar.user_defined_parameter_on], [avatar.user_defined_parameter_off]],  # A
        "1": [[avatar.user_defined_parameter_on], [avatar.user_defined_parameter_off]],  # B
        "2": [[avatar.user_defined_parameter_on], [avatar.user_defined_parameter_off]],  # X
        "3": [[avatar.user_defined_parameter_on], [avatar.user_defined_parameter_off]],  # Y
        "4": [[drone.start_alt_control], [drone.stop_alt_control]],  # LB
        "5": [[drone.staet_alt_move_mode], [drone.stop_alt_move_mode]],  # RB
        "6": [[vrcl.toggle_hud], []],  # back
        "7": [[vrcl.toggle_direct_cast], []],  # start
        "8": [[drone.clear_pos_rot, omini.reset], []],  # left stick
        "9": [[], []],  # right stick
        "10": [[vrcl.toggle_portrait], []],  # joyhat up
        "11": [
            [drone.clear_pos_rot, omini.reset, omini.change_target],
            [],
        ],  # joyhat down
        "12": [[], []],  # joyhat left
        "13": [[], []],  # joyhat right
    }
    button_alt_func_map = {
        "0": [[drone.change_to_pos_0], []],  # A
        "1": [[drone.change_to_pos_1], []],  # B
        "2": [[drone.change_to_pos_2], []],  # X
        "3": [[drone.change_to_pos_3], []],  # Y
        "4": [[drone.start_alt_control], [drone.stop_alt_control]],  # LB
        "5": [[], []],  # RB
        "6": [[vrcl.toggle_focus_peak], []],  # back
        "7": [[vrcl.toggle_avatar_focus], []],  # start
        "8": [[drone.clear_pos_rot, omini.reset], []],  # left stick
        "9": [[], []],  # right stick
        "10": [[], []],  # joyhat up
        "11": [[], []],  # joyhat down
        "12": [[], []],  # joyhat left
        "13": [[], []],  # joyhat right
    }

    """ Init
    """
    omini.sync_state(drone.pos[drone.current_pos], drone.rot[drone.current_pos])
    omini.reset()
    vrcl.sync_aperture(drone.aperture)
    vrcl.sync_focus(drone.focus)
    vrcl.sync_zoom(drone.zoom)
    vrcl.sync_exposure(drone.exposure)

    while True:
        """Long hold L1+R1 to toggle start/stop system"""
        if drone.button_state["4"] and drone.button_state["5"]:
            enable_timer = time.perf_counter()
            while drone.button_state["4"] and drone.button_state["5"]:
                if time.perf_counter() - enable_timer > 0.3:
                    if drone.is_started():
                        """Srop Anima Here"""
                        vrcl.stop()
                        pass
                        """Srop Anima Here"""
                        drone.joystick.rumble(0.4, 0.4, 800)
                        pygame.time.wait(800)
                        drone.joystick.rumble(0, 0, 0)
                        omini.sync_state(drone.pos[drone.current_pos], drone.rot[drone.current_pos])
                        drone.reset()
                        omini.reset()
                        drone.stop()
                        vrcl.sync_aperture(drone.aperture)
                        vrcl.sync_focus(drone.focus)
                        vrcl.sync_zoom(drone.zoom)
                        vrcl.sync_exposure(drone.exposure)
                    else:
                        drone.reset()
                        omini.sync_state(drone.pos[drone.current_pos], drone.rot[drone.current_pos])
                        omini.reset()
                        """Start Anima Here"""
                        vrcl.start()
                        pass
                        """Start Anima Here"""
                        drone.joystick.rumble(0.5, 1, 200)
                        pygame.time.wait(200)
                        drone.joystick.rumble(0, 0, 0)
                        pygame.time.wait(600)
                        drone.start()
                drone.update()
                pygame.time.wait(1000 // TARGET_FPS - 1)

        """ Routine
        """
        drone.update()
        # print(drone, end="\r")
        if drone.is_started():
            omini.sync_state(drone.pos[drone.current_pos], drone.rot[drone.current_pos])
            vrcl.sync_aperture(drone.aperture)
            vrcl.sync_focus(drone.focus)
            vrcl.sync_zoom(drone.zoom)
            vrcl.sync_exposure(drone.exposure)

        """ Key Event
        """
        if drone.button_state["4"]:
            for button in drone.button_state:
                if (
                    drone.button_state[button]
                    and button_alt_func_map[button][0].__len__() > 0
                ):
                    for func in button_alt_func_map[button][0]:
                        func()
                elif (
                    not drone.button_state[button]
                    and button_alt_func_map[button][1].__len__() > 0
                ):
                    for func in button_alt_func_map[button][1]:
                        func()
        else:
            for button in drone.button_state:
                if (
                    drone.button_state[button]
                    and button_func_map[button][0].__len__() > 0
                ):
                    for func in button_func_map[button][0]:
                        if button == "0":
                            func(config["a_button_parameter"], "a")
                        elif button == "1":
                            func(config["b_button_parameter"], "b")
                        elif button == "2":
                            func(config["x_button_parameter"], "x")
                        elif button == "3":
                            func(config["y_button_parameter"], "y")
                        else:
                            func()
                elif (
                    not drone.button_state[button]
                    and button_func_map[button][1].__len__() > 0
                ):
                    for func in button_func_map[button][1]:
                        if button == "0":
                            func(config["a_button_parameter"], "a")
                        elif button == "1":
                            func(config["b_button_parameter"], "b")
                        elif button == "2":
                            func(config["x_button_parameter"], "x")
                        elif button == "3":
                            func(config["y_button_parameter"], "y")
                        else:
                            func()
        pygame.time.wait(1000 // TARGET_FPS - 1)
