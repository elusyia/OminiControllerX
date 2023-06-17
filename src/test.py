import numpy as np
class Gamepad:
    class SamplePoint:
        def __init__(self, pos, rot):
            self.pos = pos
            self.rot = rot
    def __init__(self):
        self.tape = []
        self.tape.append(self.SamplePoint(np.array([1, 2, 3]), np.array([4, 5, 6])))

        self.pos = np.zeros(3)
        self.pos = self.tape[0].pos
        print(self.pos)
        self.rot = np.zeros(3)
        self.rot = self.tape[0].rot
        print(self.rot)

game = Gamepad()