#cython: boundscheck=False, wraparound=False, nonecheck=False

from GCodeLib.pygcode import Line, Machine, GCodeRapidMove, GCodeLinearMove
from GCodeLib.pygcode.words import Word
import copy
# from libc cimport math
# cimport cython
import math
import helper_functions as hf

supported_moves = {GCodeRapidMove, GCodeLinearMove}

def make_word(name, value):
	return Word(name+str(value))

# @cython.cdivision(True)
def bisect_line(self, T, x1, y1, z1, x2, y2, z2, new_commands):
	hyp = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

	if hyp > 1: # Number of mm before we split
		mx = (x2 + x1) / 2
		my = (y2 + y1) / 2
		mz = (z2 + z1) / 2
		bisect_line(self, T, x1, y1, z1, mx, my, mz, new_commands)
		bisect_line(self, T, mx, my, mz, x2, y2, z2, new_commands)
	else:
		new_move = T()

		# dx = x2 - x1
		# dy = y2 - y1
		# hyp = math.sqrt(dx ** 2 + dy ** 2)

		# if hyp > 0:
		# 	dy /= hyp

		# 	# If the tip is moving in -y direction, lift the tip up a little, otherwise, dig it in a little
		# 	z_off = dy * 0.02

		# 	z2 -= z_off

		new_move.params['X'] = make_word('X', x2)
		new_move.params['Y'] = make_word('Y', y2)
		new_move.params['Z'] = make_word('Z', z2)
		new_commands.append(new_move)

# @cython.boundscheck(False)
def bisect_codes(self):
	print("Bisecting...")

	# Converts long lines into a bunch of small lines
	all_gcodes = []
	m = Machine()
	
	for i in range(len(self.all_gcodes)):
		gcode = self.all_gcodes[i]

		x1, y1, z1 = m.pos.vector
		m.process_gcodes(gcode)

		if type(gcode) in supported_moves:
			x2, y2, z2 = m.pos.vector
			bisect_line(self, type(gcode), x1, y1, z1, x2, y2, z2, all_gcodes)
		else:
			all_gcodes.append(gcode)

	self.all_gcodes = all_gcodes[1:]

	print("Bisected GCode file")

class GCodeFile:
	def load(self, content):
		self.bounds = [float('inf'), float('inf'), -float('inf'), -float('inf')]
		self.z_offset = 0.1

		lines = content.split('\n')

		self.all_gcodes = [] # Get all of the gcodes in the file
		for line_text in lines:
			line = Line(line_text)
			gcodes = line.block.gcodes
			self.all_gcodes.extend(gcodes)

		m = Machine() # Execute the gcodes 1 by 1 using a virtual machine

		for i, gcode in enumerate(self.all_gcodes):
			m.process_gcodes(gcode)

			x, y, z = m.pos.vector

			# Update min and max (if we are actually cutting)
			if z < 0:
				self.bounds[0] = min(self.bounds[0], x)
				self.bounds[1] = min(self.bounds[1], y)
				self.bounds[2] = max(self.bounds[2], x)
				self.bounds[3] = max(self.bounds[3], y)

			# if type(gcode) in supported_moves:
			# 	gcode.params['X'] = make_word('X', x)
			# 	gcode.params['Y'] = make_word('Y', y)
			# 	gcode.params['Z'] = make_word('Z', z)

	def enumerate_gcodes(self):
		for gcode in self.all_gcodes:
			
			gcode = copy.copy(gcode)
			gcode.params = copy.copy(gcode.params)

			if type(gcode) in supported_moves:
				x = gcode.params['X'].value
				y = gcode.params['Y'].value
				z = gcode.params['Z'].value

				z += hf.f(x, y)[0] + self.z_offset
				gcode.params['Z'] = make_word('Z', z)
				# gcode.params['Y'] = make_word('Y', y)
			yield str(gcode)

	def get_content(self):
		content = ""
		for gcode in self.enumerate_gcodes():
			content += gcode + "\n"
		return content

	def bisect_codes(self):
		bisect_codes(self)