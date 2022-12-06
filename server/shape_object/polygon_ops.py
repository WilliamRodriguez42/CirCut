from shapely.geometry import Polygon
from shapely.affinity import translate, scale
# import shape_object.christofides as christofides
import shape_object.LKH as LKH
import numpy as np
from status import add_warning_message, STATUS
import math

def poly_to_svg(
	poly,
	stroke_width="0.05",
	stroke_color="#000000",
	fill_color="#66cc99"
):
	poly = scale_poly(poly, 1, -1) # SVG renders upside down for no reason
	return 	poly.svg() \
				.replace('stroke-width="2.0"', 'stroke-width="{}"'.format(stroke_width)) \
				.replace('stroke="#555555"', 'stroke="{}"'.format(stroke_color)) \
				.replace('stroke="#66cc99"', 'stroke="{}"'.format(stroke_color)) \
				.replace('fill="#66cc99"', 'fill="{}"'.format(fill_color)) \
				.replace('opacity="0.6"', 'opacity="1.0"')

def geom_to_paths(
	poly,
	contour_distance=0.25,
	contour_count=1,
	contour_step=0.1,
	buffer_resolution=16,
	exterior_only=False,
):
	num_geoms = 0
	if type(poly) != Polygon:
		num_geoms = len(poly.geoms)

	paths = []
	for i in range(contour_count):
		contour = poly.buffer(contour_step*i + contour_distance, resolution=buffer_resolution)

		if type(contour) == Polygon:
			if not exterior_only: 
				paths.extend(contour.interiors)
			paths.append(contour.exterior)

			if i == 0 and num_geoms != 0:
				add_warning_message(STATUS.CONTOUR_DISTANCE_TOO_LARGE)
		else:
			if i == 0 and len(contour.geoms) != num_geoms:
				add_warning_message(STATUS.CONTOUR_DISTANCE_TOO_LARGE)

			for geom in contour.geoms:
				if not exterior_only:
					paths.extend(geom.interiors)
				paths.append(geom.exterior)

	return paths

def paths_to_svg(
	paths,
	stroke_color="#000000"
):
	content = ""
	for path in paths:
		content += poly_to_svg(path, stroke_color=stroke_color)
	return content

def geom_to_svg(
	poly,
	stroke_width="0.05",
	stroke_color="#000000",
	fill_color="#66cc99"
):
	content = ""
	if type(poly) == Polygon:
		content += poly_to_svg(poly, stroke_width, stroke_color, fill_color)
	else:
		for geom in poly.geoms:
			content += poly_to_svg(geom, stroke_width, stroke_color, fill_color)
	return content

def scale_paths(paths, scale_x, scale_y):
	new_paths = []
	for path in paths:
		new_paths.append(scale(path, scale_x, scale_y, origin=(0,0)))

	return new_paths

def optimize_coords(coords):
	coords = np.array(coords)

	closest_index = 0
	closest_distance = float('inf')
	for i, coord in enumerate(coords[:-1]): # The last element is a repeat of the first
		distance = math.sqrt(coord[0]**2 + coord[1]**2)
		if distance < closest_distance:
			closest_index = i
			closest_distance = distance

	coords[:-1] = np.roll(coords[:-1], -closest_index, axis=0)
	coords[-1] = coords[0]

	return coords

def paths_to_gcode(
	paths,
	rapid_feedrate=500,
	pass_feedrate=100,
	safe_height=1,
	spindle_speed=255
):
	content = ""
	path_coords = []
	first_coord_in_paths = []
	for path in paths:
		x, y = path.coords.xy
		coords = list(zip(x, y))
		coords = optimize_coords(coords)
		path_coords.append(coords)
		first_coord_in_paths.append(coords[0])

	# Order the coords here (LKH algorithm)
	path = LKH.tsp(first_coord_in_paths)

	path_coords = np.array(path_coords)
	path_coords = path_coords[path]

	content += """
	G00
	G17
	G21
	G40
	G49
	G54
	G80
	G90
	G94
	G00 F{} Z{}
	S{}
	M03
	""".format(rapid_feedrate, safe_height, spindle_speed)

	for coords in path_coords:
		content += "G0 F{} X{} Y{} Z{}\n".format(rapid_feedrate, *coords[0], safe_height)

		for coord in coords:
			content += "G1 F{} X{} Y{} Z{}\n".format(pass_feedrate, *coord, -0.02)

		content += "G0 F{} Z{}\n".format(rapid_feedrate, safe_height)

	content += """
	G00 F{} Z{}
	G00 F{} X0.000 Y0.000
	M05
	M30
	""".format(rapid_feedrate, safe_height, rapid_feedrate)
	return content

def coords_to_gcode(
	coords,
	rapid_feedrate=500,
	plunge_feedrate=20,
	plunge_depth=-2.5,
	safe_height=1,
	spindle_speed=255
):
	content = """
	G00
	G17
	G21
	G40
	G49
	G54
	G80
	G90
	G94
	G00 F{} Z{}
	S{}
	M03
	""".format(rapid_feedrate, safe_height, spindle_speed)

	# Order the coords here (LKH algorithm)
	path = LKH.tsp(coords)

	path_coords = np.array(coords)
	path_coords = path_coords[path]

	for coord in path_coords:
		content += "G00 F{} X{} Y{} Z{}\n".format(rapid_feedrate, *coord, safe_height)
		content += "G00 F{} X{} Y{} Z0\n".format(rapid_feedrate, *coord)
		content += "G01 F{} X{} Y{} Z{}\n".format(plunge_feedrate, *coord, plunge_depth)
		content += "G00 F{} Z{}\n".format(rapid_feedrate, safe_height)

	content += """
	G00 F{} Z{}
	G00 F{} X0.000 Y0.000
	M05
	M30
	""".format(rapid_feedrate, safe_height, rapid_feedrate)

	return content

def translate_poly(poly, x_offset, y_offset):
	return translate(poly, x_offset, y_offset)

def translate_coords(coords, x_offset, y_offset):
	translated_coords = []
	for coord in coords:
		translated_coords.append((coord[0]+x_offset, coord[1]+y_offset))
	return translated_coords

def scale_poly(poly, x_scale, y_scale):
	return scale(poly, x_scale, y_scale, origin=(0, 0))

def scale_coords(coords, x_scale, y_scale):
	scaled_coords = []
	for coord in coords:
		scaled_coords.append((coord[0]*x_scale, coord[1]*y_scale))
	return scaled_coords