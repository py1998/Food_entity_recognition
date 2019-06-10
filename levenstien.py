import json
import csv
import numpy as np

def leven(source, target):
    if len(source) < len(target):
        return leven(target, source)
    if len(target) == 0:
        return len(source)

    source = np.array(tuple(source))
    target = np.array(tuple(target))

    previous_row = np.arange(target.size + 1)
    for s in source:
        current_row = previous_row + 1
        current_row[1:] = np.minimum(
            current_row[1:],
            np.add(previous_row[:-1], target != s))
        current_row[1:] = np.minimum(
            current_row[1:],
            current_row[0:-1] + 1)

        previous_row = current_row
    tolerance = previous_row[-1]*1.0 / min(len(source), len(target))*1.0
    return tolerance


if __name__=='__main__':
    print(leven("chiken","paneer"))