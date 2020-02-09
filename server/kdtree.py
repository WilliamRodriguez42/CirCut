import numpy as np
import time

# edges = np.array([
# 	[[0, 0], [0, 1]],
# 	[[0, 0], [1, 0]],
# 	[[1, 1], [0, 1]]
# ], dtype=np.float64)

# vertices = np.array([
# 	[-0.6, 0.5],
# 	[0.5, -0.5],
# 	[0.3, 0.2]
# ], dtype=np.float64)

edges = np.random.rand(10000, 2, 2)
vertices = np.random.rand(10000, 2)

def min_distances(vertex, edges):
	edge_vec = edges[:, 1] - edges[:, 0]
	edge_len_sq = np.sum(np.square(edge_vec), axis=1)
	
	vec_to_end = vertex - edges[:, 0]

	dot = vec_to_end[:, 0]*edge_vec[:, 0] + vec_to_end[:, 1]*edge_vec[:, 1]
	t = np.clip(dot / edge_len_sq, 0, 1)
	
	projection = edges[:, 0] + t[:, None] * edge_vec
	dist = np.sum(np.square(projection - vertex), axis=1)
	return dist

def min_distances_all_combinations(vertices, edges):
	vertices_strided = np.lib.stride_tricks.as_strided(
		vertices, 
		strides=(vertices.strides[0], 0, vertices.strides[1]), 
		shape=(vertices.shape[0], edges.shape[0], 2), 
		writeable=False).reshape(-1, 2)

	edges_strided = np.lib.stride_tricks.as_strided(
		edges, 
		strides=(0, edges.strides[0], edges.strides[1], edges.strides[2]), 
		shape=(vertices.shape[0], edges.shape[0], 2, 2), 
		writeable=False).reshape(-1, 2, 2)

	return min_distances(vertices_strided, edges_strided)

start = time.time()
print(min_distances_all_combinations(vertices, edges))
end = time.time()
print(end - start)
