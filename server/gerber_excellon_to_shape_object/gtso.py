from shapely.geometry import Polygon
from gerber_excellon_to_shape_object import gerber
from gerber_excellon_to_shape_object.primitives import primitives_map 
from status import add_error_message
from shape_object.shape_object import ShapeObject

def gerber_to_shape_object(data, resolution=16):
	if type(data) != str:
		add_error_message("Attempted to interperet file as Gerber, but received a bytes object")
		return

	gbr = gerber.rs274x.loads(data)
	gbr.to_metric()

	poly = Polygon()

	for prim in gbr.primitives:
		prim_t = type(prim)
		if prim_t in primitives_map:
			next_poly = primitives_map[prim_t](prim, resolution)
			poly = poly.union(next_poly)
		else:
			print("Unknown primitive type: ", prim_t)

	return ShapeObject(poly, poly, None)

'''
def gerber_excellon_to_svg(gbr_poly, exc_poly, gbr_paths):

	# Scale and get bounds
	gbr_poly = scale(gbr_poly, 1, -1, origin=(0,0))
	exc_poly = scale(exc_poly, 1, -1, origin=(0,0))
	gbr_paths = po.scale_paths(gbr_paths, 1, -1)

	bounds = get_bounds(gbr_poly, exc_poly, gbr_paths)

	content = """
	<svg xmlns="http://www.w3.org/2000/svg">
	<polygon points="-0.5,0 -0.5,-20 -0.7,-20 -0.25,-22 0.2,-20, 0,-20 0,0" style="fill:green; stroke-opacity:0"/>
	<polygon points="0,0.5 20,0.5 20,0.7 22,0.25 20,-0.2 20,0 0,0" style="fill:red; stroke-opacity:0"/>
	<polygon points="0,0 0,0.5 -0.5,0.5 -0.5,0" style="fill:black; stroke-opacity:0"/>
	"""
	content += po.poly_geom_to_svg(gbr_poly, stroke_width=0)
	content += po.poly_geom_to_svg(exc_poly, fill_color="#000000")
	for path in gbr_paths:
		content += po.poly_to_svg(path, stroke_color="#000000")

	content += """
	</svg>
	"""

	return content
'''