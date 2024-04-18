import numpy as np
import matplotlib
import matplotlib.pyplot as plt

import csv
from multiprocessing import Pool

matplotlib.use('TkAgg')

#open file as reader
csv_file = open('User_Tracking_Data.csv', 'r', newline='')
csv_reader = csv.DictReader(csv_file, delimiter=',')
#csv_reader = csv.reader(csv_file, delimiter=',')

#set lists of variables
x_pos_actual = []
y_pos_actual = []
time_actual = []
x_pos_measured = []
y_pos_measured = []
tracking = []
out_of_range = []
distance_from_bot = []

#header = ['Actual X Pos', 'Actual Y Pos', 'Measured X Pos', 'Measured Y Pos', 'Timestep' 'Out_of_range', 'Tracking Flag']

names = csv_reader.fieldnames
print(names)

for row in csv_reader:
    #print(row)
    x_pos_actual.append(float(row['Actual X Pos']))
    y_pos_actual.append(float(row['Actual Y Pos']))
    time_actual.append(float(row['Timestep']))
    x_pos_measured.append(float(row['Measured X Pos']))
    y_pos_measured.append(float(row['Measured Y Pos']))
    tracking.append(float(row['Tracking_flag']))
    out_of_range.append(float(row['Out_of_range']))
    distance_from_bot.append(float(row['Distance']))


#convert to np arrays
x_pos_measured = np.array(x_pos_measured)
y_pos_measured = np.array(y_pos_measured)
time = np.array(time_actual)
x_pos_actual = np.array(x_pos_actual)
y_pos_actual = np.array(y_pos_actual)

x_error = x_pos_measured-x_pos_actual
x_zero_mean = x_error - np.mean(x_error)
y_error = y_pos_measured-y_pos_actual
y_zero_mean = y_error - np.mean(y_error)


#plotting
fig, (ax1, ax2) = plt.subplots(2,1)

ax1.plot(time_actual, x_zero_mean)
ax1.set_xlabel("Simulation Time")
ax1.set_ylabel("error (m)")
ax1.set_title("Position Estimation X Error vs Time")
ax2.plot(time_actual, x_pos_measured)
ax2.plot(time_actual, x_pos_actual)
ax2.plot(time_actual, tracking)
ax2.legend(["Measured Position", "Actual Position", "Tracking Flag"])
ax2.set_xlabel("Simulation Time")
ax2.set_ylabel("X Position (Meters)")
ax2.set_title("X position measurements vs time")
plt.show()

fig, (ax1, ax2) = plt.subplots(2,1)
ax1.plot(time_actual, y_zero_mean)
ax1.set_xlabel("Simulation Time")
ax1.set_ylabel("error (m)")
ax1.set_title("Position Estimation Y Error vs Time")
ax2.plot(time_actual, y_pos_measured)
ax2.plot(time_actual, y_pos_actual)
ax2.plot(time_actual, tracking)
ax2.set_xlabel("Simulation Time")
ax2.set_ylabel("Y Position (Meters)")
ax2.legend(["Measured Position", "Actual Position", "Tracking Flag"])
ax2.set_title("Y position measurements vs time")
plt.show()

plt.plot(time_actual,distance_from_bot)
plt.plot(time_actual,out_of_range)
plt.xlabel("Simulation Time")
plt.ylabel("Distance from Robot (Meters)")
plt.title("Distance from Robot vs Time")
plt.legend(["Measured Position", 'Out Of Range Flag'])
plt.show()





