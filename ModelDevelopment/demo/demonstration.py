import numpy as np
from os import listdir
from os.path import isfile, join
import pickle
import tflearn
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.conv import conv_2d, max_pool_2d
from tflearn.layers.estimator import regression
import tensorflow as tf
from random import shuffle
import time
import gzip
import matplotlib.pyplot as plt

start_time = time.time()

print 'Hi there!'

big_data_pickle = 'random_configurations' #folter with the pickles containing all the necessary data

NAME_total = []
X_total = []
Y_total = []
big_data_pickle_list = [f for f in listdir(big_data_pickle) if isfile(join(big_data_pickle, f)) and '.pickle' in f]
index = 0
for file in big_data_pickle_list:
	index = index + 1
	print '-----'
	print 'Now processing - ' + str(index)
	with open(big_data_pickle + '/' + file, 'rb') as current_pickle:
		data_object = pickle.load(current_pickle)

	NAME_total.append(file)
	X_total.append(data_object['x'])
	current_score = np.argmax(data_object['y'])
	Y_total.append(np.asarray([current_score]))

my_net = input_data(shape=X_total[0].shape, name='input')

my_net = conv_2d(my_net, 32, 2, activation='relu')
my_net = max_pool_2d(my_net, 2)

my_net = fully_connected(my_net, 100, activation='relu')

my_net = fully_connected(my_net, 100, activation='relu')

my_net = dropout(my_net, 0.8)

my_net = fully_connected(my_net, 1, activation='linear')
my_net = regression(my_net, optimizer='sgd', learning_rate=0.01, loss='mean_square', name='targets')

model = tflearn.DNN(my_net)

model.load('convnet_model/model_1_0_3_new_linear.model')

neural_net_score_list = []
for index in xrange(0,len(X_total)):
	possible_result = model.predict([X_total[index]])[0]
	expected = Y_total[index]

	possible_result = np.asscalar(possible_result)
	expected = np.asscalar(expected)

	neural_net_score_list.append(possible_result)
	
	print '------'
	print 'Filename'
	print big_data_pickle_list[index]
	print 'Prediction Result'
	print round(possible_result,2)
	# print 'Expected'
	# print expected

max_score = max(neural_net_score_list)
file_with_best_config = big_data_pickle_list[neural_net_score_list.index(max_score)].split('.pickle')[0] + '.xml'
print '----------- The best config for the traffic lights is: -----------'
print '\n'
print 'Max score: ' + str(round(max_score,2))
print '\n'
print 'File with the traffic lights configuration: ' + file_with_best_config
print '\n'



