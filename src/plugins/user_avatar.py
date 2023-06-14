from pythonosc import udp_client
import time

class Avatar:
    def __init__(self, osc_client: udp_client.SimpleUDPClient):
        self.osc_client = osc_client
    
    def user_defined_parameter_on(self, parameter_name: str):
        self.osc_client.send_message(f"/avatar/parameters/{parameter_name}", True)
        time.sleep(0.1)
        print(f"avatar: {parameter_name} on\n")

    def user_defined_parameter_off(self, parameter_name: str):
        self.osc_client.send_message(f"/avatar/parameters/{parameter_name}", False)
        time.sleep(0.1)
        # print(f"avatar: {parameter_name} off\n")

