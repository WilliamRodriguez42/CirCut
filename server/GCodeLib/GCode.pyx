#cython: boundscheck=False, wraparound=False, nonecheck=False

from GCodeLib.pygcode import Line, Machine, GCodeRapidMove, GCodeLinearMove, GCodeArcMoveCW, GCodeArcMoveCCW, GCodeIncrementalDistanceMode
from GCodeLib.pygcode.words import Word
import copy
from libc cimport math
cimport cython

supported_moves = {GCodeRapidMove, GCodeLinearMove}

def make_word(name, value):
	return Word(name+str(value))

@cython.cdivision(True)
cdef bisect_line(self, T, float x1, float y1, float z1, float x2, float y2, float z2, new_commands):
	cdef float hyp = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

	cdef float mx, my, mz, dx, dy, z_off
	if hyp > 1: # Number of mm before we split
		mx = (x2 + x1) / 2
		my = (y2 + y1) / 2
		mz = (z2 + z1) / 2
		bisect_line(self, T, x1, y1, z1, mx, my, mz, new_commands)
		bisect_line(self, T, mx, my, mz, x2, y2, z2, new_commands)
	else:
		new_move = T()

		dx = x2 - x1
		dy = y2 - y1
		hyp = math.sqrt(dx ** 2 + dy ** 2)

		if hyp > 0:
			dy /= hyp

			# If the tip is moving in -y direction, lift the tip up a little, otherwise, dig it in a little
			z_off = dy * 0.02

			z2 -= z_off

		new_move.params['X'] = make_word('X', x2)
		new_move.params['Y'] = make_word('Y', y2)
		new_move.params['Z'] = make_word('Z', z2)
		new_commands.append(new_move)

@cython.boundscheck(False)
cdef bisect_codes(self):
	print("Bisecting...")

	# Converts long lines into a bunch of small lines
	all_gcodes = []
	m = Machine()
	
	cdef int i
	cdef float x1, y1, z1, x2, y2, z2
	for i in range(len(self.all_gcodes)):
		gcode = self.all_gcodes[i]

		x1, y1, z1 = m.pos.vector
		m.process_gcodes(gcode)

		if type(gcode) in supported_moves:
			x2, y2, z2 = m.pos.vector
			bisect_line(self, type(gcode), x1, y1, z1, x2, y2, z2, all_gcodes)
		else:
			all_gcodes.append(gcode)

	self.all_gcodes = all_gcodes

	print("Bisected GCode file")

class GCodeFile:
	def load(self, content, f):
		self.minx = 10000000
		self.maxx = -1
		self.miny = 10000000
		self.maxy = -1
		self.rangex = 0
		self.rangey = 0

		self.all_gcodes = None
		self.z_offset = 0.1
		self.y_offset = 0

		lines = content.split('\n')

		all_gcodes = [] # Get all of the gcodes in the file
		for line_text in lines:
			line = Line(line_text)
			gcodes = line.block.gcodes
			all_gcodes.extend(gcodes)

		minx = 10000000
		maxx = -1
		miny = 10000000
		maxy = -1

		m = Machine() # Execute the gcodes 1 by 1 using a virtual machine

		for i, gcode in enumerate(all_gcodes):
			m.process_gcodes(gcode)

			x, y, z = m.pos.vector

			# Update min and max (if we are actually cutting)
			if z < 0:
				minx = min(minx, x)
				maxx = max(maxx, x)
				miny = min(miny, y)
				maxy = max(maxy, y)

			if type(gcode) in supported_moves:
				gcode.params['X'] = make_word('X', x)
				gcode.params['Y'] = make_word('Y', y)
				gcode.params['Z'] = make_word('Z', z)

		self.minx = minx
		self.maxx = maxx
		self.miny = miny
		self.maxy = maxy
		self.rangex = maxx - minx
		self.rangey = maxy - miny

		self.all_gcodes = all_gcodes # Should never write to all_gcodes
		self.content = ''
		self.update_content(f)

	def update_content(self, f):
		self.content = ''
		for gcode in self.enumerate_gcodes(f):
			self.content += gcode + '\n'

	def enumerate_gcodes(self, f):
		for gcode in self.all_gcodes:
			
			gcode = copy.copy(gcode)
			gcode.params = copy.copy(gcode.params)

			if type(gcode) in supported_moves:
				x = gcode.params['X'].value
				y = gcode.params['Y'].value + self.y_offset
				z = gcode.params['Z'].value

				z += f(x, y)[0] + self.z_offset
				gcode.params['Z'] = make_word('Z', z)
				gcode.params['Y'] = make_word('Y', y)
			yield str(gcode)

	def bisect_codes(self):
		bisect_codes(self)