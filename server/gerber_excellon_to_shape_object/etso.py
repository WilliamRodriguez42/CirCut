from shapely.geometry import Polygon
from gerber_excellon_to_shape_object.primitives import make_circle 
from gerber_excellon_to_shape_object import gerber
from shape_object.shape_object import ShapeObject
from status import add_error_message

class ETSO(ShapeObject):
	def __init__(self, data, resolution=16):
		if type(data) != str:
			add_error_message("Attempted to interperet file as Excellon, but received a bytes object")
			return

		exc = gerber.excellon.loads(data)
		poly = Polygon()

		coords = []
		for prim in exc.primitives:
			prim.to_metric()
			pos = prim.position

			coords.append(pos)

			radius = prim.radius

			poly = poly.union(make_circle(pos, radius, resolution))

		super().__init__(poly, None, coords)