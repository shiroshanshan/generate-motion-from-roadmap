import numpy as np

def discriminator(original_state, next_state, mean, std):
    maximum = [[[7, 10, 8], [8, 10, 10],
              [10, 10, 8], [10, 10, 8],
              [9, 10, 10], [9, 10, 10],
              [8, 9, 9], [9, 9, 8],
              [9, 10, 9], [9, 9, 8]],
              [[8, 10, 9], [8, 10, 10],
              [10, 10, 8], [10, 10, 9],
              [9, 10, 10], [9, 10, 10],
              [8, 9, 9], [9, 9, 8],
              [9, 10, 9], [9, 9, 8]]]

    maximum = np.array(maximum)
    minimum = -maximum

    dp = next_state[0] - original_state[0]
    dv = next_state[1] - original_state[1]
    difference = np.array([dp, dv])
    normlized_difference = (difference - mean) / std
    less = normlized_difference < maximum
    more = normlized_difference > minimum
    return np.all(less + more)
