from shapely.geometry import Polygon, LineString
from shapely.affinity import translate, scale
import numpy as np
import gerber_to_gcode.gerber as gerber
import gerber_to_gcode.christofides as christofides

def get_view_box(poly_bounds):
	margin = 1
	bounds = [
		poly_bounds[0] - margin,
		poly_bounds[1] - margin,
		poly_bounds[2] + margin,
		poly_bounds[3] + margin
	]

	bounds[2] -= bounds[0]
	bounds[3] -= bounds[1]

	str_bounds = []
	for b in bounds:
		str_bounds.append(str(b))

	return " ".join(str_bounds)
	#return "0,0,100,100"

def make_circle(pos, radius, resolution):
	points = []

	for i in range(resolution):
		angle = i / (resolution - 1) * 2 * np.pi
		points.append((radius * np.cos(angle) + pos[0], radius * np.sin(angle) + pos[1]))

	return Polygon(points)

def make_rect(start, end, radius):
	d = end - start
	d = d / np.sqrt(d[0]**2 + d[1]**2) * radius

	points = [
		(start[0] - d[1], start[1] + d[0]),
		(start[0] + d[1], start[1] - d[0]),
		(end[0] + d[1], end[1] - d[0]),
		(end[0] - d[1], end[1] + d[0])
	]

	return Polygon(points)

def make_cylinder(start, end, radius, resolution):
	if (resolution < 2): resolution = 2

	start = np.array(start, dtype=np.float32)
	end = np.array(end, dtype=np.float32)

	start_circle_points = make_circle(start, radius, resolution)
	end_circle_points = make_circle(end, radius, resolution)
	rect = make_rect(start, end, radius)

	return rect.union(start_circle_points).union(end_circle_points)

def make_rect_gbr(rect, resolution=20):
	lower_left = rect.lower_left
	upper_right = rect.upper_right
	upper_left = (lower_left[0], upper_right[1])
	lower_right = (upper_right[0], lower_left[1])
	return Polygon([
		lower_left,
		upper_left,
		upper_right,
		lower_right
	])

def make_line_gbr(line, resolution=20):
	start = line.start
	end = line.end
	radius = line.aperture.diameter / 2

	return make_cylinder(start, end, radius, resolution)

def make_obround_gbr(obround, resolution=20):
	pos = obround.position
	radius = obround.width / 2

	return make_circle(pos, radius, resolution)

def make_circle_gbr(circle, resolution=20):
	pos = circle.position
	radius = circle.radius

	return make_circle(pos, radius, resolution)

primitive_map = {
	gerber.primitives.Rectangle : make_rect_gbr,
	gerber.primitives.Line : make_line_gbr,
	gerber.primitives.Obround : make_obround_gbr,
	gerber.primitives.Circle : make_circle_gbr,
}
def gerber_to_poly(data, resolution):
	gbr = gerber.rs274x.loads(data)
	gbr.to_metric()

	poly = Polygon()

	for prim in gbr.primitives:
		prim_t = type(prim)
		if prim_t in primitive_map:
			next_poly = primitive_map[prim_t](prim, resolution)
			poly = poly.union(next_poly)
		else:
			print("Unknown primitive type: ", prim_t)

	#poly = scale(poly, -1.0, -1.0)
	return poly

def poly_to_svg(poly, stroke_width="0.05", stroke_color="#000000", fill_color="#66cc99"):
	return 	poly.svg() \
			    .replace('stroke-width="2.0"', 'stroke-width="{}"'.format(stroke_width)) \
				.replace('stroke="#555555"', 'stroke="{}"'.format(stroke_color)) \
				.replace('stroke="#66cc99"', 'stroke="{}"'.format(stroke_color)) \
				.replace('fill="#66cc99"', 'fill="{}"'.format(fill_color)) \
				.replace('opacity="0.6"', 'opacity="1.0"')

def initial_to_svg(poly, stroke_width="0.05", stroke_color="#000000", fill_color="#66cc99"):
	content = ""
	if type(poly) == Polygon:
		content += poly_to_svg(poly, stroke_width, stroke_color, fill_color)
	else:
		for geom in poly.geoms:
			content += poly_to_svg(geom, stroke_width, stroke_color, fill_color)
	return content

def gerber_poly_to_paths(poly, contour_distance=0.25, contour_count=1, contour_step=0.1, buffer_resolution=16):
	num_geoms = 0
	if type(poly) != Polygon:
		num_geoms = len(poly.geoms)

	paths = []
	for i in range(contour_count):
		contour = poly.buffer(contour_step*i + contour_distance, resolution=buffer_resolution)

		if type(contour) == Polygon:
			paths.extend(contour.interiors)
			paths.append(contour.exterior)

			if i == 0 and num_geoms != 0:
				print("Contour distance too large")
		else:
			if i == 0 and len(contour.geoms) != num_geoms:
				print("Contour distance too large")
			for geom in contour.geoms:
				paths.extend(geom.interiors)
				paths.append(geom.exterior)

	return paths

def excellon_to_poly_coords(data, resolution=50):
	exc = gerber.excellon.loads(data)
	exc.to_inch()

	poly = Polygon()

	exc_coords = []
	for prim in exc.primitives:
		pos = prim.position
		exc_coords.append((pos[0]*-25.4, pos[1]*25.4))

		radius = prim.radius

		poly = poly.union(make_circle(pos, radius, resolution))

	return poly, exc_coords

def poly_paths_to_svg(gbr_poly, exc_poly, gbr_paths):
	bounds = [10000000, 1000000, 0, 0]
	paths = []

	# Scale and get bounds
	gbr_poly = scale(gbr_poly, 1, -1, origin=(0,0))
	if gbr_poly.bounds[0] < bounds[0]:
		bounds[0] = gbr_poly.bounds[0]
	if gbr_poly.bounds[1] < bounds[1]:
		bounds[1] = gbr_poly.bounds[1]
	if gbr_poly.bounds[2] > bounds[2]:
		bounds[2] = gbr_poly.bounds[2]
	if gbr_poly.bounds[3] > bounds[3]:
		bounds[3] = gbr_poly.bounds[3]
	exc_poly = scale(exc_poly, 1, -1, origin=(0,0))
	if exc_poly.bounds[0] < bounds[0]:
		bounds[0] = exc_poly.bounds[0]
	if exc_poly.bounds[1] < bounds[1]:
		bounds[1] = exc_poly.bounds[1]
	if exc_poly.bounds[2] > bounds[2]:
		bounds[2] = exc_poly.bounds[2]
	if exc_poly.bounds[3] > bounds[3]:
		bounds[3] = exc_poly.bounds[3]
	for i, path in enumerate(gbr_paths):
		path = scale(path, 1, -1, origin=(0,0))
		paths.append(path)
		if path.bounds[0] < bounds[0]:
			bounds[0] = path.bounds[0]
		if path.bounds[1] < bounds[1]:
			bounds[1] = path.bounds[1]
		if path.bounds[2] > bounds[2]:
			bounds[2] = path.bounds[2]
		if path.bounds[3] > bounds[3]:
			bounds[3] = path.bounds[3]

	content = """
	<svg xmlns="http://www.w3.org/2000/svg">
	""".format(get_view_box(bounds))

	content += initial_to_svg(gbr_poly)
	content += initial_to_svg(exc_poly, fill_color="#000000")
	for path in paths:
		content += poly_to_svg(path, stroke_color="#000000")

	content += """
	</svg>
	"""

	return content

def scale_paths(paths, scale_x, scale_y):
	new_paths = []
	for path in paths:
		new_paths.append(scale(path, scale_x, scale_y, origin=(0,0)))

	return new_paths

def paths_to_gcode(paths, rapid_feedrate=500, pass_feedrate=100, safe_height=1, spindle_speed=255):
	content = ""
	path_coords = []
	first_coord_in_paths = []
	for path in paths:
		x, y = path.coords.xy
		coords = list(zip(x, y))
		path_coords.append(coords)
		first_coord_in_paths.append(coords[0])

	# Order the coords here (christofide's algorithm)
	length, path = christofides.tsp(first_coord_in_paths)

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

def drills_to_gcode(coords, rapid_feedrate=500, plunge_feedrate=20, plunge_depth=-2.5, safe_height=1, spindle_speed=255):
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

	# Order the coords here (christofide's algorithm)
	length, path = christofides.tsp(coords)

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

class GTG():
	def __init__(self):
		self.gbr_poly = Polygon()
		self.exc_poly = Polygon()
		self.gbr_paths = []
		self.bounds = [0, 0, 0, 0]

		self.translated_gbr_poly = Polygon()
		self.translated_exc_poly = Polygon()
		self.translated_gbr_paths = []

	def load_gerber(self, filename, contour_distance=0.2, contour_count=1, contour_step=0.2, buffer_resolution=5, resolution=16):
		file = open(filename, "r")
		gbr_data = file.read()
		file.close()

		# Get polygon from the gerber files
		self.gbr_poly = gerber_to_poly(gbr_data, resolution=resolution)

		# Translate and modify those polygons before futher interpretation
		self.gbr_poly = scale(self.gbr_poly, -1, 1, origin = (0, 0))

		# Convert the gerber polygon to contour paths
		self.gbr_paths = gerber_poly_to_paths(self.gbr_poly,
					contour_distance=contour_distance,
					contour_count=contour_count,
					contour_step=contour_step,
					buffer_resolution=buffer_resolution)

	def load_excellon(self, filename, resolution=16):
		file = open(filename, "r")
		exc_data = file.read()
		file.close()

		# Get polygon from the excellon files
		self.exc_poly, self.exc_coords = excellon_to_poly_coords(exc_data, resolution=resolution)

		# Translate and modify those polygons before futher interpretation
		self.exc_poly = scale(self.exc_poly, -25.4, 25.4, origin = (0, 0))

	def update_translation(self):
		self.bounds = list(self.gbr_poly.bounds)

		# Get bounds of paths
		if self.exc_poly.bounds[0] < self.bounds[0]:
			self.bounds[0] = self.exc_poly.bounds[0]
		if self.exc_poly.bounds[1] < self.bounds[1]:
			self.bounds[1] = self.exc_poly.bounds[1]
		if self.exc_poly.bounds[2] > self.bounds[2]:
			self.bounds[2] = self.exc_poly.bounds[2]
		if self.exc_poly.bounds[3] > self.bounds[3]:
			self.bounds[3] = self.exc_poly.bounds[3]
		for i, path in enumerate(self.gbr_paths):
			self.gbr_paths[i] = path
			if path.bounds[0] < self.bounds[0]:
				self.bounds[0] = path.bounds[0]
			if path.bounds[1] < self.bounds[1]:
				self.bounds[1] = path.bounds[1]
			if path.bounds[2] > self.bounds[2]:
				self.bounds[2] = path.bounds[2]
			if path.bounds[3] > self.bounds[3]:
				self.bounds[3] = path.bounds[3]

		self.bounds[0] -= 1 # Add 1 mm space for wiggle room
		self.bounds[1] -= 1

		# Translate everything to start at zero
		self.translated_gbr_poly = translate(self.gbr_poly, -self.bounds[0], -self.bounds[1])
		self.translated_exc_poly = translate(self.exc_poly, -self.bounds[0], -self.bounds[1])
		self.translated_gbr_paths = []
		for path in self.gbr_paths:
			self.translated_gbr_paths.append(translate(path, -self.bounds[0], -self.bounds[1]))

		self.translated_exc_coords = []
		for coord in self.exc_coords:
			self.translated_exc_coords.append((coord[0]-self.bounds[0], coord[1]-self.bounds[1]))

	def svg(self):
		return poly_paths_to_svg(self.translated_gbr_poly, self.translated_exc_poly, self.translated_gbr_paths)

	def gcode(self, rapid_feedrate=500, pass_feedrate=100, plunge_feedrate=20, plunge_depth=-2.5, safe_height=1, contour_spindle_speed=255, drill_spindle_speed=255):
		return (
			paths_to_gcode(self.translated_gbr_paths, rapid_feedrate=rapid_feedrate, pass_feedrate=pass_feedrate, safe_height=safe_height, spindle_speed=contour_spindle_speed),
			drills_to_gcode(self.translated_exc_coords, rapid_feedrate=rapid_feedrate, plunge_feedrate=plunge_feedrate, plunge_depth=plunge_depth, safe_height=safe_height, spindle_speed=drill_spindle_speed)
		)

	def write_svg(self, filename):
		file = open(filename, 'w+')
		file.write(self.svg())
		file.close()

	def write_gcode(self, gerber_filename, excellon_filename, rapid_feedrate=500, pass_feedrate=100, plunge_feedrate=20, plunge_depth=-2.5, safe_height=1, contour_spindle_speed=255, drill_spindle_speed=255):
		gerber_gcode, excellon_gcode = self.gcode(rapid_feedrate=rapid_feedrate, pass_feedrate=pass_feedrate, plunge_feedrate=plunge_feedrate, plunge_depth=plunge_depth, contour_spindle_speed=contour_spindle_speed, drill_spindle_speed=drill_spindle_speed)
		file = open(gerber_filename, 'w+')
		file.write(gerber_gcode)
		file.close()

		file = open(excellon_filename, 'w+')
		file.write(excellon_gcode)
		file.close()

if __name__ == '__main__':
	gtg = GTG()
	gtg.load_gerber("../resources/CNC_CALIBRATION_TEST-F.Cu.gbr", contour_distance=0.099, contour_count=2, contour_step=0.15, buffer_resolution=2, resolution=2)
	gtg.load_excellon("../resources/CNC_CALIBRATION_TEST-PTH.drl")
	gtg.update_translation()
	gtg.write_svg("index.html")
	gtg.write_gcode("../resources/contours.gcode", "../resources/drills.gcode")
