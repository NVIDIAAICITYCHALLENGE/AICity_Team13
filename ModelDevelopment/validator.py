import xml.etree.ElementTree as ET
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from scipy import signal
from scipy import *
import time


def gauss_kern(size, sizey=None):
	size = int(size)
	if not sizey:
	    sizey = size
	else:
	    sizey = int(sizey)
	x, y = mgrid[-size:size+1, -sizey:sizey+1]
	g = exp(-(x**2/float(size)+y**2/float(sizey)))
	return g / g.sum()

def blur_image(im, n, ny=None) :
	g = gauss_kern(n, sizey=ny)
	improc = signal.convolve(im,g, mode='valid')
	return(improc)


raw_file_to_process = 'simulations/output_1500998128_922.xml'
# raw_file_to_process = 'v2.5/outputs/out_2cps_1step_1501534037431.xml'

image_filename = 'v2.5/images/big_map.png'
# image_filename = 'v2.5/images/out_2cps_1step_1501534037431-blur5.png'


start_time = time.time()

# XINIT = 0
# XEND = 2800
# YINIT = 0
# YEND = 2900
# AREASTEP = 20

XINIT = 0
XEND = 7000
YINIT = 0
YEND = 7000
AREASTEP = 20

x_list = []
y_list = []

current_x = XINIT
current_y = YINIT
while current_x < XEND:
	while current_y < YEND:
		y_list.append(0)
		current_y = current_y + AREASTEP

	current_y = YINIT
	x_list.append(y_list)
	y_list = []
	current_x = current_x + AREASTEP

picture_array = np.asarray(x_list)
pins_array = np.asarray(x_list)
print 'Mesh prepared!'

print 'Reading RAW file...'
# outputTree = ET.parse("output_test.xml")
# outputTree = ET.parse("output.xml")
outputTree = ET.parse(raw_file_to_process)
outputRoot = outputTree.getroot()

ambulance_speed = []
index = 0
last_time_step = 0
for timestep in outputRoot.iter('timestep'):
	last_time_step = timestep.get('time')
	for vehicle in timestep:
		current_x = float(vehicle.get('x'))
		mesh_x = current_x//AREASTEP
		mesh_x = int(mesh_x)

		current_y = float(vehicle.get('y'))
		mesh_y = current_y//AREASTEP
		mesh_y = int(mesh_y)

		current_speed = float(vehicle.get('speed'))

		index = index + 1
		print index
		print '-------'

		picture_array[mesh_x][mesh_y] = picture_array[mesh_x][mesh_y] + current_speed
		pins_array[mesh_x][mesh_y] = pins_array[mesh_x][mesh_y] + 1

last_time_step = float(last_time_step)
print last_time_step
average_speed_array = np.divide(picture_array, pins_array)
print average_speed_array.shape

print("--- %s seconds ---" % (time.time() - start_time))


new_Z = blur_image(average_speed_array, 5)

# plt.figure(figsize=(10,10), dpi=80)
# cax = plt.imshow(new_Z, interpolation='nearest')
# plt.colorbar(cax, orientation='horizontal')
# plt.savefig(image_filename)
# plt.show()





nx, ny = new_Z.shape[1], new_Z.shape[0] 
x = range(nx)
y = range(ny)

hf = plt.figure()
ha = hf.add_subplot(111, projection='3d')
X, Y = np.meshgrid(x, y)
ha.plot_surface(X, Y, new_Z, cmap=cm.coolwarm)
plt.show()





		