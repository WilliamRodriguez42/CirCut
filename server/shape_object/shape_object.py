import shape_object.polygon_ops as po
import os
if os.name == 'nt':
	from GCodeLib.GCode_Win import GCodeFile
else:
	from GCodeLib.GCodeLib import GCodeFile


class ShapeObject:
	def __init__(self, svg_geom, geom, coords):
		self.svg_geom = svg_geom
		self.geom = geom
		self.coords = coords
		self.paths = None
		self.layout = None
		self.id = None
		self.gcode = None

	def calculate_paths(self):
		print(self.layout)
		if self.geom is not None:
			self.paths = po.geom_to_paths(
				self.geom,
				contour_distance=self.layout['Contour Distance']['value'],
				contour_count=self.layout['Contour Count']['value'],
				contour_step=self.layout['Contour Step']['value'],
				buffer_resolution=self.layout['Buffer Resolution']['value'])

	def get_thumbnail_svg(self):
		if self.geom is not None: # Render the shape we will cut paths around
			return po.geom_to_svg(self.svg_geom, stroke_width=0)
		else: # Render a bunch of circles representing drill areas
			return po.geom_to_svg(self.svg_geom, fill_color="#000000")

	def get_preview_svg(self):
		if self.geom is not None: # Render the paths that the CNC machine will take
			return po.paths_to_svg(self.paths, stroke_color="#000000")
		else: # Render a bunch of circles representing drill areas
			return po.geom_to_svg(self.svg_geom, fill_color="#000000")

	def calculate_gcode(self):
		if self.geom is not None: # Get g code of paths that the CNC machine will take
			gcode_content = po.paths_to_gcode(
				self.paths,
				rapid_feedrate=self.layout['Rapid Feedrate']['value'],
				pass_feedrate=self.layout['Pass Feedrate']['value'],
				safe_height=self.layout['Safe Height']['value'],
				spindle_speed=self.layout['Spindle Speed']['value'])
		else:
			gcode_content = po.coords_to_gcode(
				self.coords,
				rapid_feedrate=self.layout['Rapid Feedrate']['value'],
				plunge_feedrate=self.layout['Plunge Feedrate']['value'],
				plunge_depth=self.layout['Plunge Depth']['value'],
				safe_height=self.layout['Safe Height']['value'],
				spindle_speed=self.layout['Spindle Speed']['value'])

		self.gcode = GCodeFile()
		self.gcode.load(gcode_content)

	def bisect_codes(self):
		self.gcode.bisect_codes()

def add_shape_object_to_list(shape_object):
	global current_shape_object_id, active_shape_objects

	shape_object.id = current_shape_object_id
	active_shape_objects.append(shape_object)
	current_shape_object_id += 1

def remove_shape_object_from_list(id):
	for i in range(len(active_shape_objects)):
		if active_shape_objects[i].id == id:
			del active_shape_objects[i]
			break

def find_shape_object_with_id(id):
	for i in range(len(active_shape_objects)):
		if active_shape_objects[i].id == id:
			return active_shape_objects[i]

active_shape_objects = []
current_shape_object_id = 0