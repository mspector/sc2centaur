"""
==================================
Starcraft Assistive AI: dynamic time warping (DTW) implementation used in KNN module
==================================

"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Important note: Indexing in numpy is based on [width,height], or [y,x]
# This is *against* typical scientific graphing convention [x,y]
# The correct index order will depend on the specific function calls
# For example, the graphing functions used in visualization will require the [x,y] format

def get_distance_matrix(a,b,distance_function):
	distances = np.zeros((len(a),len(b)))
	for i in range(len(a)):
		for j in range(len(b)):
			distances[i,j] = distance_function(a[i],b[j])
	return distances

def get_cost_matrix(distance_matrix):
	length_a = distance_matrix.shape[0]
	length_b = distance_matrix.shape[1]
	cost_matrix = np.zeros((length_a,length_b))

	for i in range(0, length_a):
		for j in range(0, length_b):
			
			if i==0 and j==0:
				min_cost = distance_matrix[i,j]
			if i==0:
				min_cost = distance_matrix[i,j] + cost_matrix[i,j-1]
			if j==0:
				min_cost = distance_matrix[i,j] + cost_matrix[i-1,j]
			if i>0 and j>0:
				min_cost = distance_matrix[i,j] + min(cost_matrix[i-1,j-1], cost_matrix[i,j-1], cost_matrix[i-1,j]) 
	
			cost_matrix[i,j] = min_cost
	return cost_matrix

def get_warp_path(cost_matrix):
	length_a = cost_matrix.shape[0]
	length_b = cost_matrix.shape[1]

	path = [[length_a-1, length_b-1]]

	i = length_a-1
	j = length_b-1

	while i>0 and j>0:
	    if i==0:
	        j = j-1
	    elif j==0:
	        i = i-1
	    else:
			if cost_matrix[i-1, j] == min(cost_matrix[i-1, j-1], cost_matrix[i-1, j], cost_matrix[i, j-1]): 
				i = i-1
			elif cost_matrix[i, j-1] == min(cost_matrix[i-1, j-1], cost_matrix[i-1, j], cost_matrix[i, j-1]):
				j = j-1 
			else:
				i = i-1
				j = j-1

	    path.append([i,j])
	path.append([0,0])
	return path

def get_cost(warp_path,distance_matrix):
	cost = 0
	for [x,y] in warp_path:
		cost = cost + distance_matrix[x,y]
	return cost

def visualize(matrix):
    im = plt.imshow(matrix, interpolation='nearest', cmap='Reds') 
    plt.ylabel("A")
    plt.xlabel("B")
    plt.grid()
    plt.colorbar();

# Main DTW script. Not yet integrated with sc2centaur.
#def dtw():


def main():	
	# Defining our (simple) distance function
	def scalar_euclidean_dist(a,b):
		return (a-b)**2

	# Creating two signals
	a = np.array([1,1,2,3,2,0])
	b = np.array([0,1,1,2,3,2,1])

	# Making a 2D matrix to compute distances between all pairs of x and y
	distance_matrix = get_distance_matrix(a,b,scalar_euclidean_dist)

	# Making a 2D matrix to hold the accumulated "cost" of each coordinate
	cost_matrix = get_cost_matrix(distance_matrix)

	# Generate the least costly (or shortest) path through the cost matrix
	warp_path = get_warp_path(cost_matrix)
	
	path_a = [point[0] for point in warp_path]
	path_b = [point[1] for point in warp_path]
	visualize(cost_matrix)
	
	# Remember: numpy indexing is based on [height,width], or [y,x]
	# The 'plot' function, however, is based on [x,y]
	# Since signal A is visualized on the Y axis, we need to call 'plot' with arguments reversed relative to the numpy calls
	plt.plot(path_b, path_a)
	print(warp_path)
	return [a,b,distance_matrix,cost_matrix,warp_path,path_a,path_b]

if __name__ == '__main__':
	main()