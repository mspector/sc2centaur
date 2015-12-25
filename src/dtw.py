"""
==================================
Starcraft Assistive AI: dynamic time warping (DTW) implementation for classification
==================================

"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# Main DTW script. Not yet integrated with sc2centaur.
def dtw():
	
	# Creating two signals
	x = np.array([1,1,2,3,2,0])
	y = np.array([0,1,1,2,3,2,1])

	# Plotting the two signals
	plt.plot(x, 'r', label='x')
	plt.plot(y, 'g', label='y')
	plt.legend

	# Making a 2D matrix to compute distances between all pairs of x and y
	distances = np.zeros((len(y),len(x))
if __name__ == '__main__':
	dtw()