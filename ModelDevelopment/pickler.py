from xml.dom import minidom
from os import listdir
from os.path import isfile, join
import pickle

print 'Hello World!'

mypath = 'demo/results'
output_path = 'demo/results'
files_list = [f for f in listdir(mypath) if isfile(join(mypath, f)) and '.xml' in f and 'res' in f]

index = 0
for file in files_list:
	file_to_open = mypath + '/' + file
	print file_to_open
	current_file = minidom.parse(file_to_open)

	current_score = current_file.getElementsByTagName('score')[0].attributes['value'].value
	current_score = float(current_score)

	global_average_speed = current_file.getElementsByTagName('score')[0].attributes['allAvgSpeed'].value
	global_average_speed = float(global_average_speed)

	ambulance_average_speed = current_file.getElementsByTagName('score')[0].attributes['ambAvgSpeed'].value
	ambulance_average_speed = float(ambulance_average_speed)

	input_list = []

	areas_list = current_file.getElementsByTagName('tArea')
	for area in areas_list:
		current_area_speed = area.attributes['avgSpeed'].value
		current_area_density = area.attributes['density'].value
		input_list.append(float(current_area_speed))
		input_list.append(float(current_area_density))

	semaphore_list = current_file.getElementsByTagName('tlLogic')
	for semaphore in semaphore_list:
		local_list = semaphore.getElementsByTagName('phase')
		for phase in local_list:
			current_phase = phase.attributes['duration'].value
			input_list.append(float(current_phase))

	object_to_pickle = {'score': current_score, 'global_average_speed': global_average_speed, 'ambulance_average_speed': ambulance_average_speed, 'input_data': input_list}
	pickel_file_name = file.split('.xml')[0]
	with open(output_path + '/' + pickel_file_name + '.pickle', 'wb') as f:
		pickle.dump(object_to_pickle, f)

	index = index + 1
	print 'Done ---- '
	print 'Total done - ' + str(index)
	print file
	print '-------------------------------------'



