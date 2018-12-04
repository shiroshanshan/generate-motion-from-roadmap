import numpy as np

def gaze_determinator(gaze_direction):

    left = gaze_direction['left_eye']
    right = gaze_direction['right_eye']
    vertical_vector = np.array([0, 0, -1])
    left = np.sum(left * vertical_vector)
    right = np.sum(right * vertical_vector)
    if left + right > 2 * np.cos(np.pi/12):
        return 1
    else:
        return 0
