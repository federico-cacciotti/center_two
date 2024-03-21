from leybold_vacuum_controller import CenterTwo
from matplotlib import pyplot as plt
import numpy as np
from datetime import datetime
from time import time

serial_port = "/dev/ttyS3"
sensor = CenterTwo.Controller(serial_port)

PERIOD = 2.0 # seconds
channel = 1
LENGTH = 400
pressure_array = np.ones(LENGTH)*np.nan
time_array = np.ones(LENGTH)*np.nan

path_to_logs = "/src/leybold_vacuum_controller/logs/"
logfile_name = datetime.now().strftime("%Y%d%m_%H%M%S")+".dat"
header = "time since epoch,pressure"

np.savetxt(path_to_logs+logfile_name, delimiter=',', comments='#', X=[])

fig = plt.figure()
ax = fig.gca()

while(True):
    # get pressure
    status, pressure = sensor.getChannelPressure(channel)
    
    if status == 0:
        pressure_array = np.roll(pressure_array, -1)
        pressure_array[-1] = pressure
        with open(path_to_logs+logfile_name) as file:
            np.savetxt(file, X=[time, pressure], delimiter=',', comments='#')

    ax.clear()
    ax.set_ylabel("Pressure [mbar]")
    ax.set_xlabel("Index")
    ax.plot(time_array, pressure_array)

    plt.pause(PERIOD)