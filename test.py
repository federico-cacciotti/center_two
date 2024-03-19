import CenterTwo
from matplotlib import pyplot as plt
import numpy as np


serial_port = "/dev/ttyS3"
sensor = CenterTwo.Controller(serial_port)
channel = 1
LENGTH = 400
pressure_array = np.ones(LENGTH)*np.nan


fig = plt.figure()
ax = fig.gca()

while(True):
    status, pressure = sensor.getPressure(channel)
    if status == 0:
        pressure_array = np.roll(pressure_array, -1)
        pressure_array[-1] = pressure

    ax.clear()
    ax.set_ylabel("Pressure [mbar]")
    ax.set_xlabel("Index")
    ax.plot(pressure_array)

    plt.pause(2.0)