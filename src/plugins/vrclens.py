import time
from pythonosc import udp_client

def constrain(x: float, min_value: float = 0, max_value: float = 1) -> float:
    return max(min_value, min(max_value, x))

class VRCLens:
    def __init__(self, osc_client: udp_client.SimpleUDPClient):
        self.osc_client = osc_client

    def __feature(self, feature_number: int):
        # is integer assert
        assert isinstance(feature_number, int)
        self.osc_client.send_message(
            "/avatar/parameters/VRCLFeatureToggle", feature_number
        )
        time.sleep(0.1)
        self.osc_client.send_message("/avatar/parameters/VRCLFeatureToggle", 0)

    def start(self):
        self.__feature(254)
        print("vrclens: camera enabled.\n")

    def stop(self):
        self.osc_client.send_message("/avatar/parameters/VRCLFeatureToggle", 254)
        time.sleep(0.5)
        self.osc_client.send_message("/avatar/parameters/VRCLFeatureToggle", 0)
        print("vrclens: camera disabled.\n")

    def toggle_hud(self):
        self.__feature(226)
        print("vrclens: toggled hud\n")

    def toggle_avatar_focus(self):
        self.__feature(13)
        print("vrclens: toggled avatar focus\n")

    def toggle_focus_peak(self):
        self.__feature(1)
        self.__feature(51)
        print("vrclens: toggled focus peak\n")

    def toggle_direct_cast(self):
        self.__feature(224)
        print("vrclens: toggled direct cast\n")

    def toggle_portrait(self):
        self.__feature(222)
        print("vrclens: toggled portrait\n")

    def toggle_vr_mount(self):
        self.__feature(223)
        print("vrclens: toggled vr mount\n")

    def toggle_hide_camera(self):
        self.__feature(225)
        print("vrclens: toggled hide camera\n")

    def sync_zoom(self, value: float):
        value = constrain(value)
        self.osc_client.send_message(
            "/avatar/parameters/VRCLZoomRadial", value
        )
        # print("vrclens: zoom", value, "\n")

    def sync_exposure(self, value: float):
        value = constrain(value)
        self.osc_client.send_message(
            "/avatar/parameters/VRCLExposureRadial", value
        )
        # print("vrclens: exposure", value, "\n")

    def sync_aperture(self, value: float):
        value = constrain(value)
        self.osc_client.send_message(
            "/avatar/parameters/VRCLApertureRadial", value
        )
        # print("vrclens: aperture", value, "\n")

    def sync_focus(self, value: float):
        if value == 0:
            self.osc_client.send_message("/avatar/parameters/VRCLFocusRadial", False)
            # print("vrclens: autofocus")
        else:
            value = constrain(value)
            self.osc_client.send_message(
                "/avatar/parameters/VRCLFocusRadial", value
            )
            # print("vrclens: focus", value, "\n")
        
