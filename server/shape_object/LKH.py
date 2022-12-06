import elkai
import numpy as np

def tsp(coords):
	coords_array = np.zeros((len(coords)+1, 2))
	coords_array[1:] = coords

	complex_coords = coords_array[:, 0] + coords_array[:, 1]*1j

	num_coords = complex_coords.shape[0]

	rows = np.repeat(complex_coords, complex_coords.shape[0])
	rows = rows.reshape(num_coords, num_coords)

	cols = rows.T

	M = np.abs(rows - cols)

	result = elkai.solve_float_matrix(M)

	return np.array(result[1:]) - 1