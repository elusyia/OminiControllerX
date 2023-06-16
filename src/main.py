from drone import Drone
from plugins.vrclens import VRCLens
from plugins.omini_controller import OminiController
from plugins.user_avatar import Avatar
from pythonosc import udp_client
import time
import pygame
import json

config = json.load(open("src/config.json", "r"))
# config = json.load(open("config.json", "r"))
OSC_ADRESS = config["osc_adress"]
OSC_PORT = config["osc_port"]
TARGET_FPS = config["fps"]

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
        "0": [[drone.change_to_pos_0], []],  # A
        "1": [[drone.change_to_pos_1], []],  # B
        "2": [[drone.change_to_pos_2], []],  # X
        "3": [[drone.change_to_pos_3], []],  # Y
        "4": [[drone.start_lb_control], [drone.stop_lb_control]],  # LB
        "5": [[drone.start_rb_control], [drone.stop_rb_control]],  # RB
        "6": [[vrcl.toggle_hud], []],  # back
        "7": [[vrcl.toggle_vr_mount], []],  # start
        "8": [[drone.clear_pos_rot, omini.reset], []],  # left stick
        "9": [[drone.drop_collect_focus], []],  # right stick
        "10": [[vrcl.toggle_portrait], []],  # joyhat up
        "11": [
            [vrcl.toggle_hide_camera],
            [],
        ],  # joyhat down
        "12": [[vrcl.toggle_direct_cast], []],  # joyhat left
        "13": [[vrcl.toggle_direct_cast], []],  # joyhat right
    }
    button_lb_func_map = {
        "0": [[],[],],  # A
        "1": [[],[],],  # B
        "2": [[],[],],  # X
        "3": [[],[],],  # Y
        "4": [[drone.start_lb_control], [drone.stop_lb_control]],  # LB
        "5": [[], []],  # RB
        "6": [[vrcl.toggle_focus_peak], []],  # back
        "7": [[vrcl.toggle_avatar_focus], []],  # start
        "8": [[drone.clear_pos_rot, omini.reset], []],  # left stick
        "9": [[drone.drop_collect_focus], []],  # right stick
        "10": [[], []],  # joyhat up
        "11": [[], []],  # joyhat down
        "12": [[], []],  # joyhat left
        "13": [[], []],  # joyhat right
    }
    button_rb_func_map = {
        "0": [[avatar.user_defined_parameter_on], [avatar.user_defined_parameter_off]],  # A
        "1": [[avatar.user_defined_parameter_on], [avatar.user_defined_parameter_off]],  # B
        "2": [[avatar.user_defined_parameter_on], [avatar.user_defined_parameter_off]],  # X
        "3": [[avatar.user_defined_parameter_on], [avatar.user_defined_parameter_off]],  # Y
        "4": [[], []],  # LB
        "5": [[drone.start_rb_control], [drone.stop_rb_control]],  # RB
        "6": [[], []],  # back
        "7": [[], []],  # start
        "8": [[drone.clear_pos_rot, omini.reset], []],  # left stick
        "9": [[drone.drop_collect_focus],[],],  # right stick
        "10": [[],[],],  # joyhat up
        "11": [[],[],],  # joyhat down
        "12": [[],[],],  # joyhat left
        "13": [[],[],],  # joyhat right
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
                        omini.sync_state(
                            drone.pos[drone.current_pos], drone.rot[drone.current_pos]
                        )
                        drone.reset()
                        omini.reset()
                        drone.stop()
                        vrcl.sync_aperture(drone.aperture)
                        vrcl.sync_focus(drone.focus)
                        vrcl.sync_zoom(drone.zoom)
                        vrcl.sync_exposure(drone.exposure)
                    else:
                        drone.reset()
                        omini.sync_state(
                            drone.pos[drone.current_pos], drone.rot[drone.current_pos]
                        )
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
        if drone.button_state["4"]:  # LB control layer
            for button in drone.button_state:
                if (
                    drone.button_state[button]
                    and button_lb_func_map[button][0].__len__() > 0
                ):
                    for func in button_lb_func_map[button][0]:
                        func()
                elif (
                    not drone.button_state[button]
                    and button_lb_func_map[button][1].__len__() > 0
                ):
                    for func in button_lb_func_map[button][1]:
                        func()
        elif drone.button_state["5"]:  # RB control layer
            for button in drone.button_state:
                if (
                    drone.button_state[button]
                    and button_rb_func_map[button][0].__len__() > 0
                ):
                    for func in button_rb_func_map[button][0]:
                        if button == "0":
                            func(config["up_button_parameter"], "a")
                        elif button == "1":
                            func(config["down_button_parameter"], "b")
                        elif button == "2":
                            func(config["left_button_parameter"], "x")
                        elif button == "3":
                            func(config["right_button_parameter"], "y")
                        else:
                            func()
                elif (
                    not drone.button_state[button]
                    and button_rb_func_map[button][1].__len__() > 0
                ):
                    for func in button_rb_func_map[button][1]:
                        if button == "0":
                            func(config["up_button_parameter"], "a")
                        elif button == "1":
                            func(config["down_button_parameter"], "b")
                        elif button == "2":
                            func(config["left_button_parameter"], "x")
                        elif button == "3":
                            func(config["right_button_parameter"], "y")
                        else:
                            func()
        else:
            for button in drone.button_state:
                if (
                    drone.button_state[button]
                    and button_func_map[button][0].__len__() > 0
                ):
                    for func in button_func_map[button][0]:
                        func()
                elif (
                    not drone.button_state[button]
                    and button_func_map[button][1].__len__() > 0
                ):
                    for func in button_func_map[button][1]:
                        func()
        pygame.time.wait(1000 // TARGET_FPS - 1)
