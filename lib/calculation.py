import numpy as np


def running_mean(xs, N):
    average_bins = [0] * N
    running_average = []
    for nx, x in enumerate(xs):
        average_bins.pop(0)
        average_bins.append(x)
        running_average.append(sum(average_bins) / N)
    for n in range(N):
        running_average[n] = running_average[N]
    return running_average
