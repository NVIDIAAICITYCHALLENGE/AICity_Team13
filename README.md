# Introduction
We have proposed a solution that uses the footage of traffic cameras to train a neural network to decrease the response time of emergency vehicles within the Golden Hour with minimum disturbance in the traffic of all other vehicles. Our proposed solution is based on the SUMO simulator to generate a training set. This set is used to train a deep convolutional neural network which is then validated through simulations on SUMO.
# Software description
The following software components were developed as part of the challenge. Additional information and usage can be be found in their individual directories.
## SampleGenerator
Script used to run simulations and generate training samples.
## ModelDevelopment
Contains neural network models and training scripts.
## SimulationComparison
Script that runs two simulations simultaneously to compare traffic light outputs.