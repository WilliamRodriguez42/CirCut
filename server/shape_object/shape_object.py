import shape_object.polygon_ops as po
from shapely.geometry import Polygon
from settings_management.defaults import default_requirements
import os
if os.name == 'nt':
	from GCodeLib.GCode_Win import GCodeFile
else:
	from GCodeLib.GCodeLib import GCodeFile
from status import add_error_message

class ShapeObject:
	def __init__(self, svg_geom, geom, coords):
		self.svg_geom = svg_geom
		self.geom = geom
		self.coords = coords

		if self.svg_geom is not None:
			self.svg_geom_original = type(self.svg_geom)(self.svg_geom)
		if self.geom is not None:
			self.geom_original = type(self.geom)(self.geom)
		if self.coords is not None:
			self.coords_original = type(self.coords)(self.coords)

		self.paths = None
		self.layout = None
		self.id = None
		self.gcode = None
		self.name = None

	def calculate_paths(self):
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
		elif self.svg_geom is not None: # Render a bunch of circles representing drill areas
			return po.geom_to_svg(self.svg_geom, fill_color="#000000")
		return ""

	def get_preview_svg(self):
		if self.geom is not None and self.paths is not None: # Render the paths that the CNC machine will take
			return po.paths_to_svg(self.paths, stroke_color="#000000")
		# elif self.geom is None and self.svg_geom is not None: # Render a bunch of circles representing drill areas
		# 	return po.geom_to_svg(self.svg_geom, fill_color="#000000")
		return ""

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

	def get_gcodes(self, f):
		if self.gcode is not None:
			return self.gcode.get_content(f)
		return ""

	def update_layout(self, layout):
		message = ""

		for key, value in layout.items():
			setting_type = value['type']
			setting_value = value['value']
			if setting_type == 'number':
				setting_value = float(setting_value)
				df = default_requirements[key]

				valid = True
				if df['min'] is not None:
					if df['min_inclusive']:
						if setting_value < df['min']:
							valid = False
					else:
						if setting_value <= df['min']:
							valid = False
				if df['max'] is not None:
					if df['max_inclusive']:
						if setting_value > df['max']:
							valid = False
					else:
						if setting_value >= df['max']:
							valid = False
				if df['integer']:
					if int(setting_value) != setting_value:
						valid = False
					setting_value = int(setting_value)

				if not valid:
					message += "Invalid value for {}: must be".format(key)
					if df['integer']:
						message += " an integer"
					if df['min'] is not None:
						if df['min_inclusive']:
							message += " greater than or equal to {}".format(df['min'])
						else:
							message += " greater than {}".format(df['min'])
					if df['min'] is not None and df['max'] is not None:
						message += " and"
					if df['max']:
						if df['max_inclusive']:
							message += " less than or equal to {}".format(df['max'])
						else:
							message += " less than {}".format(df['max'])
				else:
					self.layout[key]['value'] = setting_value
			elif setting_type == 'checkbox':
				self.layout[key]['value'] = setting_value == 'true'

		if message != "":
			add_error_message(message)

	def update_minor_settings(self):
		# Perform minor changes to objects such as the svg_geom, geom, and coords
		x_scale = 1
		if self.layout['Flip X Axis']['value']:
			x_scale = -1
		self.svg_geom = po.scale_poly(self.svg_geom_original, x_scale, 1)
		if self.geom is not None:
			self.geom = po.scale_poly(self.geom_original, x_scale, 1)
			self.svg_geom = po.translate_poly(self.svg_geom, self.layout['X Offset']['value'], self.layout['Y Offset']['value'])
			self.geom = po.translate_poly(self.geom, self.layout['X Offset']['value'], self.layout['Y Offset']['value'])
		if self.coords is not None:
			self.coords = po.scale_coords(self.coords_original, x_scale, 1)
			self.svg_geom = po.translate_poly(self.svg_geom, self.layout['X Offset']['value'] - self.layout['Bit Travel X']['value'], self.layout['Y Offset']['value'] - self.layout['Bit Travel Y']['value'])
			self.coords = po.translate_coords(self.coords, self.layout['X Offset']['value'] - self.layout['Bit Travel X']['value'], self.layout['Y Offset']['value'] - self.layout['Bit Travel Y']['value'])

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
	print(active_shape_objects)

def find_shape_object_with_id(id):
	for i in range(len(active_shape_objects)):
		if active_shape_objects[i].id == id:
			return active_shape_objects[i]

def get_active_shape_objects():
	return active_shape_objects

def move_shape_object_after_id(shape_object_id, inject_before_id):
	for old_position in range(len(active_shape_objects)):
		if active_shape_objects[old_position].id == shape_object_id:
			break

	shape_object = active_shape_objects.pop(old_position)
	if inject_before_id != -1:
		for i in range(len(active_shape_objects)):
			if active_shape_objects[i].id == inject_before_id:
				active_shape_objects.insert(i+1, shape_object)
				break
	else:
		active_shape_objects.insert(0, shape_object)

active_shape_objects = []
current_shape_object_id = 0