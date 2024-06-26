import CenterTwo
from matplotlib import pyplot as plt
import numpy as np
from datetime import datetime
from time import time

serial_port = "/dev/ttyUSB0"
sensor = CenterTwo.Controller()
sensor.connect(serial_port)

PERIOD = 2.0 # seconds
channel = 1
LENGTH = 400
pressure_array = np.ones(LENGTH)*np.nan
time_array = np.ones(LENGTH)*np.nan

path_to_logs = "/home/federico/Documents/GitHub/leybold_vacuum_controller/logs/"
logfile_name = datetime.now().strftime("%Y%d%m_%H%M%S")+".dat"
header = "time since epoch,pressure"

np.savetxt(path_to_logs+logfile_name, delimiter=',', comments='#', X=[])

fig = plt.figure()
ax = fig.gca()

start_time = time()/3600.0

while(True):
    # get pressure
    status, pressure = sensor.get_channel_pressure(channel)
    
    if status == CenterTwo.SENS_STATUS[0] or status == CenterTwo.SENS_STATUS[1] or status == CenterTwo.SENS_STATUS[2]:
        pressure_array = np.roll(pressure_array, -1)
        pressure_array[-1] = pressure
        time_array = np.roll(time_array, -1)
        time_array[-1] = time()/3600.0 - start_time
        
        with open(path_to_logs+logfile_name, 'a') as file:
            np.savetxt(file, X=[time_array[-1], pressure_array[-1]], delimiter=',', comments='#')
            
    if status == CenterTwo.SENS_STATUS[1] or status == CenterTwo.SENS_STATUS[2]:
        print(status)

    ax.clear()
    ax.set_ylabel("Pressure [mbar]")
    ax.set_xlabel("Time since acquisition started [h]")
    ax.plot(time_array, pressure_array)

    plt.pause(PERIOD)