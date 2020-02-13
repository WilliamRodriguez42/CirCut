#cython: boundscheck=False, wraparound=False, nonecheck=False, cdivision=True

# No cython 124 seconds
# Cython no labels 118 seconds
# Optimal result with cython optimization 111.47 seconds

from shapely.geometry import Polygon
from ShapeObjectConversions import gerber
from ShapeObjectConversions.primitives import primitives_map 
from status import add_error_message
from shape_object.shape_object import ShapeObject
import numpy as np
cimport numpy as np
from itertools import permutations, combinations
import min_distance_vertex_to_edge as mdve
import time
from ShapeObjectConversions.SparseMatrix import SparseMatrix

class GTSO(ShapeObject):
	def __init__(self, data, resolution=16):
		if type(data) != str:
			add_error_message("Attempted to interperet file as Gerber, but received a bytes object")
			return

		print("STARTING CONVERSION")

		start_time = time.time()
		gbr = gerber.rs274x.loads(data)
		gbr.to_metric()

		poly = Polygon()
		position_to_poly_map = []
		position_to_k_map = []
		cdef int poly_position = 0

		for prim in gbr.primitives:
			prim_t = type(prim)
			if prim_t in primitives_map:
				gerber.previous_net_name = prim.net_name

				next_poly = primitives_map[prim_t](prim, resolution)
				position_to_k_map.append(prim.net_name)
				position_to_poly_map.append(next_poly)
				poly_position += 1

				# poly = poly.union(next_poly)
			else:
				add_error_message("Unknown primitive type: {}".format(prim_t))
		
		cdef np.ndarray inter_poly_distance, position_to_buffer_map
		cdef int poly_position1, poly_position2, i, min_index
		cdef unsigned char poly_visited1, poly_visted2
		cdef double percent_step, min_distance, buffer_by

		if gerber.previous_net_name is None:
			for p in position_to_poly_map:
				poly = poly.union(p)
		else:
			ipd_sparse = SparseMatrix(poly_position)
			# inter_poly_distance = idp_sparse.mat

			for poly_position1 in range(poly_position):
				for poly_position2 in range(poly_position1):
					if position_to_k_map[poly_position1] == position_to_k_map[poly_position2]:
						continue # Skip polygons within the same netlist

					# Find the minimum distance between the two polygons
					# inter_poly_distance[poly_position1, poly_position2] = position_to_poly_map[poly_position1].distance(position_to_poly_map[poly_position2])
					ipd_sparse.add_point(poly_position1, poly_position2, position_to_poly_map[poly_position1].distance(position_to_poly_map[poly_position2]))

			# import pdb
			# pdb.set_trace()

			position_to_buffer_map = np.zeros(poly_position)
			poly_visited = np.zeros(poly_position, dtype=np.bool)

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

			for i in range(1):

				percent_step = 0.99

				while True:
					# min_index = np.argmin(inter_poly_distance * (1 - np.logical_and(visited_repeated, visited_tiled) * 0.5), axis=None)
					(poly_position1, poly_position2), min_distance = ipd_sparse.argmin_and_invalidate()
					# poly_position1 = min_index / poly_position
					# poly_position2 = min_index % poly_position

					# min_distance = inter_poly_distance[poly_position1, poly_position2]

					if min_distance == np.inf:
						break

					poly_visited1 = poly_visited[poly_position1]
					poly_visited2 = poly_visited[poly_position2]
					poly_visited[poly_position1] = True
					poly_visited[poly_position2] = True
					# inter_poly_distance[poly_position1, poly_position2] = np.inf

					if not poly_visited1 and not poly_visited2:
						buffer_by = min_distance / 2 * percent_step
						position_to_buffer_map[poly_position1] += buffer_by
						position_to_buffer_map[poly_position2] += buffer_by
						# inter_poly_distance[:, poly_position1] -= buffer_by
						# inter_poly_distance[poly_position1, :] -= buffer_by
						# inter_poly_distance[:, poly_position2] -= buffer_by
						# inter_poly_distance[poly_position2, :] -= buffer_by
						ipd_sparse.subtract_from_position(poly_position1, buffer_by)
						ipd_sparse.subtract_from_position(poly_position2, buffer_by)

					elif not poly_visited1:
						buffer_by = min_distance * percent_step
						position_to_buffer_map[poly_position1] += buffer_by
						# inter_poly_distance[:, poly_position1] -= buffer_by
						# inter_poly_distance[poly_position1, :] -= buffer_by
						ipd_sparse.subtract_from_position(poly_position1, buffer_by)

					elif not poly_visited2:
						buffer_by = min_distance * percent_step
						position_to_buffer_map[poly_position2] += buffer_by
						# inter_poly_distance[:, poly_position2] -= buffer_by
						# inter_poly_distance[poly_position2, :] -= buffer_by
						ipd_sparse.subtract_from_position(poly_position2, buffer_by)

			for i in range(poly_position):
				p = position_to_poly_map[i]
				poly = poly.union(p.buffer(position_to_buffer_map[i], resolution=5))

		stop_time = time.time()
		print("Gerber conversion time:", stop_time - start_time)
		super().__init__(poly, poly, None)

	def convert_vertices_to_edges(self, vertices):
		original = np.array(vertices)
		rolled = np.roll(original, 1, axis=0)
		result = np.append(original.reshape(-1, 1, 2), rolled.reshape(-1, 1, 2), axis=1)

		return result

FORCE_CLEARANCE = 0.01