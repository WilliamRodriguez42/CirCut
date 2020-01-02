from shapely.geometry import Polygon
from shapely.affinity import translate, scale
import numpy as np
import gerber_to_gcode.gerber as gerber
import gerber_to_gcode.polygon_ops as po
from status import *

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
	subshapes = obround.subshapes
	circle1 = subshapes['circle1']
	circle2 = subshapes['circle2']
	rectangle = subshapes['rectangle']

	c1 = make_circle_gbr(circle1)
	c2 = make_circle_gbr(circle2)
	r = make_rect_gbr(rectangle)

	return c1.union(c2).union(r)

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

def excellon_to_poly_coords(data, resolution=50):
	exc = gerber.excellon.loads(data)
	poly = Polygon()

	exc_coords = []
	for prim in exc.primitives:
		prim.to_metric()
		pos = prim.position
		#exc_coords.append((pos[0]*-25.4, pos[1]*25.4))
		exc_coords.append(pos)

		radius = prim.radius

		poly = poly.union(make_circle(pos, radius, resolution))

	return poly, exc_coords

def get_bounds(gbr_poly, exc_poly, gbr_paths):
	bounds = [10000000, 1000000, 0, 0]

	# Scale and get bounds
	if gbr_poly.bounds[0] < bounds[0]:
		bounds[0] = gbr_poly.bounds[0]
	if gbr_poly.bounds[1] < bounds[1]:
		bounds[1] = gbr_poly.bounds[1]
	if gbr_poly.bounds[2] > bounds[2]:
		bounds[2] = gbr_poly.bounds[2]
	if gbr_poly.bounds[3] > bounds[3]:
		bounds[3] = gbr_poly.bounds[3]
	if exc_poly.bounds[0] < bounds[0]:
		bounds[0] = exc_poly.bounds[0]
	if exc_poly.bounds[1] < bounds[1]:
		bounds[1] = exc_poly.bounds[1]
	if exc_poly.bounds[2] > bounds[2]:
		bounds[2] = exc_poly.bounds[2]
	if exc_poly.bounds[3] > bounds[3]:
		bounds[3] = exc_poly.bounds[3]
	for path in gbr_paths:
		if path.bounds[0] < bounds[0]:
			bounds[0] = path.bounds[0]
		if path.bounds[1] < bounds[1]:
			bounds[1] = path.bounds[1]
		if path.bounds[2] > bounds[2]:
			bounds[2] = path.bounds[2]
		if path.bounds[3] > bounds[3]:
			bounds[3] = path.bounds[3]

	return bounds

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

class GTG:
	def __init__(self):
		self.gbr_poly = Polygon()
		self.exc_poly = Polygon()
		self.gbr_paths = []
		self.bounds = [0, 0, 0, 0]

		self.translated_gbr_poly = Polygon()
		self.translated_exc_poly = Polygon()
		self.translated_gbr_paths = []

	def load_gerber(
		self,
		filename,
		contour_distance=0.2,
		contour_count=1,
		contour_step=0.2,
		buffer_resolution=5,
		resolution=16,
		flip_x_axis=True
	):
		file = open(filename, "r")
		gbr_data = file.read()
		file.close()

		# Get polygon from the gerber files
		self.gbr_poly = gerber_to_poly(gbr_data, resolution=resolution)

		# Translate and modify those polygons before futher interpretation
		if flip_x_axis:
			self.gbr_poly = scale(self.gbr_poly, -1, 1, origin = (0, 0))

		# Convert the gerber polygon to contour paths
		self.gbr_paths = po.poly_to_paths(self.gbr_poly,
					contour_distance=contour_distance,
					contour_count=contour_count,
					contour_step=contour_step,
					buffer_resolution=buffer_resolution)

	def load_excellon(self, filename, resolution=16, flip_x_axis=True):
		file = open(filename, "r")
		exc_data = file.read()
		file.close()

		print(filename)

		# Get polygon from the excellon files
		self.exc_poly, self.exc_coords = excellon_to_poly_coords(exc_data, resolution=resolution)

		# Translate and modify those polygons before futher interpretation
		#self.exc_poly = scale(self.exc_poly, -25.4, 25.4, origin = (0, 0))
		if flip_x_axis:
			self.exc_poly = scale(self.exc_poly, -1, 1, origin = (0, 0))
			exc_coords = self.exc_coords
			self.exc_coords = []

			for coord in exc_coords:
				self.exc_coords.append((coord[0]*-1, coord[1]))

	def update_translation(
		self,
		calculate_origin=False,
		flip_x_axis=True,
		x_offset=0,
		y_offset=0,
		nc_drill_x_offset=0,
		nc_drill_y_offset=0,
	):
		self.bounds = get_bounds(self.gbr_poly, self.exc_poly, self.gbr_paths)

		if flip_x_axis and not calculate_origin:
			x_offset *= -1

		if calculate_origin:
			x_offset -= self.bounds[0]
			y_offset -= self.bounds[1]

		nc_drill_x_offset += x_offset
		nc_drill_y_offset += y_offset

		# Translate everything to start at zero
		self.translated_gbr_poly = translate(self.gbr_poly, x_offset, y_offset)
		self.translated_exc_poly = translate(self.exc_poly, nc_drill_x_offset, nc_drill_y_offset)
		self.translated_gbr_paths = []
		for path in self.gbr_paths:
			self.translated_gbr_paths.append(translate(path, x_offset, y_offset))

		self.translated_exc_coords = []
		for coord in self.exc_coords:
			self.translated_exc_coords.append((coord[0]+nc_drill_x_offset, coord[1]+nc_drill_y_offset))

	def svg(self):
		return gerber_excellon_to_svg(self.translated_gbr_poly, self.translated_exc_poly, self.translated_gbr_paths)

	def gcode(
		self,
		rapid_feedrate=500,
		pass_feedrate=100,
		plunge_feedrate=20,
		plunge_depth=-2.5,
		safe_height=1,
		contour_spindle_speed=255,
		drill_spindle_speed=255):

		return (
			po.paths_to_gcode(self.translated_gbr_paths,
				rapid_feedrate=rapid_feedrate,
				pass_feedrate=pass_feedrate,
				safe_height=safe_height,
				spindle_speed=contour_spindle_speed),
				
			po.coords_to_gcode(self.translated_exc_coords,
				rapid_feedrate=rapid_feedrate,
				plunge_feedrate=plunge_feedrate,
				plunge_depth=plunge_depth,
				safe_height=safe_height,
				spindle_speed=drill_spindle_speed)
		)

	def write_svg(self, filename):
		file = open(filename, 'w+')
		file.write(self.svg())
		file.close()

	def write_gcode(
		self,
		gerber_filename,
		excellon_filename,
		rapid_feedrate=500,
		pass_feedrate=100,
		plunge_feedrate=20,
		plunge_depth=-2.5,
		safe_height=1,
		contour_spindle_speed=255,
		drill_spindle_speed=255):

		gerber_gcode, excellon_gcode = self.gcode(
			rapid_feedrate=rapid_feedrate,
			pass_feedrate=pass_feedrate,
			plunge_feedrate=plunge_feedrate,
			plunge_depth=plunge_depth,
			safe_height=safe_height,
			contour_spindle_speed=contour_spindle_speed,
			drill_spindle_speed=drill_spindle_speed)

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
