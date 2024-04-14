import numpy as np
import matplotlib.pyplot as plt
x = np.arange(-10,10,1)
y = np.arange(-10,10,1)
# print(x)

length = 10
width = 10
length_array = np.arange(-length//2, length//2)
width_array = np.arange(-width//2, width//2)
X, Y = np.meshgrid(length_array, width_array)
print(X)
print(Y)