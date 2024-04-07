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

header = ['Actual X Pos', 'Actual Y Pos', 'Timestep', 'Measured X Pos', 'Measured Y Pos', 'Timestep']

names = csv_reader.fieldnames
print(names)

for row in csv_reader:
    print(row)
    x_pos_actual.append(float(row['Actual X Pos']))
    y_pos_actual.append(float(row['Actual Y Pos']))
    time_actual.append(float(row['Timestep']))
    x_pos_measured.append(float(row['Measured X Pos']))
    y_pos_measured.append(float(row['Measured Y Pos']))

#convert to np arrays
x_pos_measured = np.array(x_pos_measured)
y_pos_measured = np.array(y_pos_measured)
time = np.array(time_actual)
x_pos_actual = np.array(x_pos_actual)
y_pos_actual = np.array(y_pos_actual)

x_error = np.divide(x_pos_measured-x_pos_actual, x_pos_actual) * 100
y_error = np.divide(y_pos_measured-y_pos_actual, y_pos_actual) * 100

plt.plot(time_actual, x_error)
plt.plot(time_actual, y_error)
plt.xlabel("Simulation Time")
plt.ylabel("error (%)")
plt.legend(["X Error", "Y Error"])
plt.title("Position Estimation Error vs Time")
plt.show()

plt.plot(time_actual, x_pos_measured)
plt.plot(time_actual, x_pos_actual)
plt.legend(["Measured Position", "Actual Position"])
plt.xlabel("Simulation Time")
plt.ylabel("X Position (Meters)")
plt.title("X position measurements vs time")
plt.show()

plt.plot(time_actual, y_pos_measured)
plt.plot(time_actual, y_pos_actual)
plt.xlabel("Simulation Time")
plt.ylabel("Y Position (Meters)")
plt.legend(["Measured Position", "Actual Position"])
plt.title("Y position measurements vs time")
plt.show()


