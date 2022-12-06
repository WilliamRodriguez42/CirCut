#cython: boundscheck=False, wraparound=False, nonecheck=False, cdivision=True
import numpy as np

class SparseMatrix:
	def __init__(self, size): # Assumes mat is square
		self.adjacency_list = np.zeros((size, size), dtype=np.uint)
		self.adjacency_list_lengths = np.zeros(size, dtype=np.uint)

		self.positions = np.zeros((size**2, 2), dtype=np.uint)
		self.values = np.zeros(size**2, dtype=np.float64)
		self.weights = np.ones(size**2, dtype=np.float64) * 0.5
		self.cache = np.zeros(size**2, dtype=np.float64)
		self.length = 0

	def add_point(self, i, j, v):
		length = self.adjacency_list_lengths[i]
		self.adjacency_list[i, length] = self.length
		self.adjacency_list_lengths[i] += 1

		length = self.adjacency_list_lengths[j]
		self.adjacency_list[j, length] = self.length
		self.adjacency_list_lengths[j] += 1

		self.positions[self.length] = (i, j)
		self.values[self.length] = v
		self.cache[self.length] = v * 0.5
		self.length += 1

	def argmin_and_invalidate(self):
		m = np.argmin(self.cache[:self.length])
		pos = self.positions[m]
		val = self.values[m]
		self.values[m] = np.inf
		self.cache[m] = np.inf
		return pos, val

	def subtract_from_position(self, pos, sub):
		length = self.adjacency_list_lengths[pos]
		positions = self.adjacency_list[pos, :length]
		self.values[positions] -= sub
		self.weights[positions] = 1
		self.cache[positions] = self.values[positions]
