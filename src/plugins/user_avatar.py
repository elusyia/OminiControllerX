from pythonosc import udp_client
import time

class Avatar:
    def __init__(self, osc_client: udp_client.SimpleUDPClient):
        self.osc_client = osc_client
        self.a_state = False
        self.b_state = False
        self.x_state = False
        self.y_state = False

    def user_defined_parameter_on(self, parameter_name: str, key: str):
        if key == "a" and not self.a_state: 
            self.a_state = True
            self.osc_client.send_message(f"/avatar/parameters/{parameter_name}", True)
            print(f"avatar: {parameter_name} on\n")
        if key == "b" and not self.b_state:
            self.b_state = True
            self.osc_client.send_message(f"/avatar/parameters/{parameter_name}", True)
            print(f"avatar: {parameter_name} on\n")
        if key == "x" and not self.x_state:
            self.x_state = True
            self.osc_client.send_message(f"/avatar/parameters/{parameter_name}", True)
            print(f"avatar: {parameter_name} on\n")
        if key == "y" and not self.y_state:
            self.y_state = True
            self.osc_client.send_message(f"/avatar/parameters/{parameter_name}", True)
            print(f"avatar: {parameter_name} on\n")

    def user_defined_parameter_off(self, parameter_name: str, key: str):
        if key == "a" and self.a_state:
            self.a_state = False
            self.osc_client.send_message(f"/avatar/parameters/{parameter_name}", False)
            print(f"avatar: {parameter_name} off\n")
        if key == "b" and self.b_state:
            self.b_state = False
            self.osc_client.send_message(f"/avatar/parameters/{parameter_name}", False)
            print(f"avatar: {parameter_name} off\n")
        if key == "x" and self.x_state:
            self.x_state = False
            self.osc_client.send_message(f"/avatar/parameters/{parameter_name}", False)
            print(f"avatar: {parameter_name} off\n")
        if key == "y" and self.y_state:
            self.y_state = False
            self.osc_client.send_message(f"/avatar/parameters/{parameter_name}", False)
            print(f"avatar: {parameter_name} off\n")

