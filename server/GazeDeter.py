import numpy as np

class GazeDeter:

    def deter(self, gaze_direction):
        self.left = gaze_direction['left_eye']
        self.right = gaze_direction['right_eye']
        vertical_vector = np.array([0, 0, -1])
        left = np.sum(self.left * vertical_vector)
        right = np.sum(self.right * vertical_vector)
        if self.left + self.right > 2 * np.cos(np.pi/12):
            return 1
        else:
            return 0

gazedeter = GazeDeter()
