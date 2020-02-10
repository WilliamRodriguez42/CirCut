from shapely.geometry import Polygon
from gerber_excellon_to_shape_object import gerber
from gerber_excellon_to_shape_object.primitives import primitives_map 
from status import add_error_message
from shape_object.shape_object import ShapeObject
import numpy as np
from itertools import permutations, combinations
import min_distance_vertex_to_edge as mdve

class GTSO(ShapeObject):
	def __init__(self, data, resolution=16):
		if type(data) != str:
			add_error_message("Attempted to interperet file as Gerber, but received a bytes object")
			return

		gbr = gerber.rs274x.loads(data)
		gbr.to_metric()

		poly = Polygon()
		position_to_poly_map = []
		position_to_k_map = []
		poly_position = 0

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

		if gerber.previous_net_name is None:
			for p in position_to_poly_map:
				poly = poly.union(p)
		else:
			ar = np.arange(poly_position)
			inter_poly_distance = np.zeros((poly_position, poly_position)) + np.inf
			poly_visited = np.zeros(poly_position, dtype=np.bool)

			for poly_position1 in range(poly_position):
				for poly_position2 in range(poly_position1):
					if position_to_k_map[poly_position1] == position_to_k_map[poly_position2]:
						continue # Skip polygons within the same netlist

					# Find the minimum distance between the two polygons
					inter_poly_distance[poly_position1][poly_position2] = position_to_poly_map[poly_position1].distance(position_to_poly_map[poly_position2])

			# import pdb
			# pdb.set_trace()

			while True:
				min_index = np.unravel_index(np.argmin(inter_poly_distance.flatten()), inter_poly_distance.shape)

				poly_position1, poly_position2 = min_index
				min_distance = inter_poly_distance[poly_position1, poly_position2]

				if min_distance == np.inf:
					break


				inter_poly_distance[poly_position1, poly_position2] = np.inf

				poly_visited1 = poly_visited[poly_position1]
				poly_visited2 = poly_visited[poly_position2]
				poly_visited[poly_position1] = True
				poly_visited[poly_position2] = True
				inter_poly_distance[poly_position1, poly_position2] = np.inf

				if not poly_visited1 and not poly_visited2:
					buffer_by = min_distance / 2 - FORCE_CLEARANCE
					p1 = position_to_poly_map[poly_position1].buffer(buffer_by, resolution=5)
					p2 = position_to_poly_map[poly_position2].buffer(buffer_by, resolution=5)
					poly = poly.union(p1)
					poly = poly.union(p2)
					inter_poly_distance[:, poly_position1] -= buffer_by
					inter_poly_distance[poly_position1, :] -= buffer_by
					inter_poly_distance[:, poly_position2] -= buffer_by
					inter_poly_distance[poly_position2, :] -= buffer_by

				elif not poly_visited1:
					buffer_by = min_distance - FORCE_CLEARANCE
					p = position_to_poly_map[poly_position1].buffer(buffer_by, resolution=5)
					poly = poly.union(p)
					inter_poly_distance[:, poly_position1] -= buffer_by
					inter_poly_distance[poly_position1, :] -= buffer_by

				elif not poly_visited2:
					buffer_by = min_distance - FORCE_CLEARANCE
					p = position_to_poly_map[poly_position2].buffer(buffer_by, resolution=5)
					poly = poly.union(p)
					inter_poly_distance[:, poly_position2] -= buffer_by
					inter_poly_distance[poly_position2, :] -= buffer_by

		import pdb
		pdb.set_trace()
		super().__init__(poly, poly, None)

	def convert_vertices_to_edges(self, vertices):
		original = np.array(vertices)
		rolled = np.roll(original, 1, axis=0)
		result = np.append(original.reshape(-1, 1, 2), rolled.reshape(-1, 1, 2), axis=1)

		return result

FORCE_CLEARANCE = 0.1