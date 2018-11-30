import numpy as np

def discriminator(state_dp, state_dv, mean, std):
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
    maximum = maximum / 2.5
    minimum = -maximum

    difference = np.array([state_dp, state_dv])
    normlized_difference = (difference - mean) / std
    less = normlized_difference < maximum
    more = normlized_difference > minimum

    return np.all(more) and np.all(less)
