import numpy as np
import time

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

	md = min_distances(vertices_strided, edges_strided)

	# Collapse for each vertex
	# md = md.reshape(-1, edges.shape[0])
	# md_index = np.argmin(md, axis=1)
	# return np.sqrt(md[np.arange(vertices.shape[0]), md_index]), md_index

	return np.sqrt(md)

if __name__ == '__main__':
		
	# edges = np.array([
	# 	[[0, 0], [0, 1]],
	# 	[[0, 0], [1, 0]],
	# 	[[1, 1], [0, 1]],
	# ], dtype=np.float64)

	# vertices = np.array([
	# 	[-0.6, 0.5],
	# 	[0.5, -0.5],
	# 	[0.3, 0.2],
	# 	[0.1, -0.3]
	# ], dtype=np.float64)

	# # edges = np.random.rand(10, 2, 2)
	# # vertices = np.random.rand(10, 2)

	# start = time.time()
	# min_distances = min_distances_all_combinations(vertices, edges)
	# end = time.time()
	# print(end - start)

	# print(min_distances)

	poly_visited = np.arange(5)

	visited_repeated = np.lib.stride_tricks.as_strided(
		poly_visited, 
		strides=(poly_visited.strides[0], 0), 
		shape=(poly_visited.shape[0], poly_visited.shape[0]), 
		writeable=False)


	visited_tiled = np.lib.stride_tricks.as_strided(
		poly_visited, 
		strides=(0, poly_visited.strides[0]), 
		shape=(poly_visited.shape[0], poly_visited.shape[0]), 
		writeable=False)


	print(visited_repeated * np.arange(25))

	print(visited_tiled)
