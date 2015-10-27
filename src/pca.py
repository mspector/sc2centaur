import numpy as np

np.random.seed(1)

mu_vec1 = np.array([0,0,0])
cov_mat1 = np.array([1,0,0],[0,1,0],[0,0,1])
class1_sample = np.random.multivariate_normal(mu_vec1, cov_mat1, 20).T
assert class1_sample.shape == (3,20), "The matrix has not the dimensions 3x20"

mu_vec2 = np.array([1,1,1])
cov_mat2 = np.array([1,0,0],[0,1,0],[0,0,1])
class2_sample = np.random.multivariate_normal(mu_vec2, cov_mat2, 20).T
assert class2_sample.shape == (3,20), "The matrix has not the dimensions 3x20"

from matplotlib import pyplot as pyplot
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d import proj3d