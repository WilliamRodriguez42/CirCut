from shapely.geometry import Polygon
import ShapeObjectConversions.gerber as gerber
import shape_object.polygon_ops as po
import numpy as np
import math

def make_circle(pos, radius, resolution):
	points = []

	for i in range(resolution):
		angle = i / (resolution - 1) * 2 * math.pi
		points.append((radius * math.cos(angle) + pos[0], radius * math.sin(angle) + pos[1]))

	return Polygon(points)

def make_rect(start, end, radius):
	d = end - start
	d = d / math.sqrt(d[0]**2 + d[1]**2) * radius

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

def make_region_gbr(region, resolution=20):
	poly = Polygon()

	for prim in region.primitives:
		prim_t = type(prim)
		if prim_t in primitives_map:
			next_poly = primitives_map[prim_t](prim, resolution)
			poly = poly.union(next_poly)
		else:
			print("Unknown primitive type: ", prim_t)

	return Polygon(poly.exterior.coords)

primitives_map = {
	gerber.primitives.Rectangle : make_rect_gbr,
	gerber.primitives.Line : make_line_gbr,
	gerber.primitives.Obround : make_obround_gbr,
	gerber.primitives.Circle : make_circle_gbr,
	gerber.primitives.Region : make_region_gbr,
}
