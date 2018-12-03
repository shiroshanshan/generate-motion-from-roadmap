import numpy as np

def gaze_determinator(gaze_direction):

    left = gaze_direction['left_eye']
    right = gaze_direction['right_eye']
    vertical_vector = np.array([0, 0, -1])
    left = np.sum(left * vertical)
    right = np.sum(right * vertical)
    if left + right < 2 * np.cos(np.pi/9):
        return True
    else:
        return False
