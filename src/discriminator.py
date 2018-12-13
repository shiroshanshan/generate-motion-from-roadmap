import numpy as np
import math

def discriminator(state_dp, state_dv, mean, std, threshold):

    difference = np.array([state_dp, state_dv])
    normalized_difference = (difference - mean) / std
    eva = 0
    for i in range(60):
        idx = i // 30
        row = i % 30 // 3
        column = i % 30 % 3
        tmp = abs(normalized_difference[idx,row,column])
        if tmp < std[idx,row,column]:
            eva += math.exp(-2.3 * tmp/std[idx,row,column])
        else:
            return 0

    return eva / 60.