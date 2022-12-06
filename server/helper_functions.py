from serial_communication import *
import serial_communication as sc
import numpy as np
from scipy.interpolate import interp2d

import os
from GCodeLib.GCode import GCodeFile

import re
import json
import status
from shape_object.shape_object import get_shape_objects_gcode_bounding_box

from CommandObject import TerminateObject, CommandObjectList

def json_dumps(form):
	content = json.dumps(form, sort_keys=True, indent=4)
	content = re.sub('\n +', lambda match: '\n' + '\t' * (len(match.group().strip('\n')) // 3), content) # snake-case, hard-tabs, keep it together!
	return content

# def sanitize_filename(filename):
# 	prev_filename = filename
# 	attempts = 0
# 	while True: # Sanitize until we know the name is clean
# 		filename = bleach.clean(filename)
# 		filename = sanitize_filename(filename)
# 		if prev_filename == filename:
# 			return filename
# 		prev_filename = filename

# 		attempts += 1
# 		if (attempts > 2): return False

def probez():
	poll_ok()
	write('G38.2 Z-100 F50')	 # Probe for contact
	poll_ok()

	write('G10 P0 L20 X0 Y0 Z0')	# Set current position as zero
	poll_ok()

	write('G1 Z1 F500')

def probe(dz, initial=False):
	poll_ok()
	write('G38.2 Z-100 F50')	 # Probe for contact
	poll_ok()

	write('G4 P0.01') # Wait for task to complete
	poll_ok()

	print(sc.sender.last_received)
	print(sc.sender.last_sent)

	z_pos_match = re.match(r'.*,([^,]*?):.*', sc.sender.last_received[2]) # Get the result of the serial
	z_pos = 0

	if z_pos_match:
		z_pos = float(z_pos_match[1])
	else:
		print('There was an issue, please refer to previous output')
		return -10000

	if initial:
		write('G10 P0 L20 X0 Y0 Z0')	# Set current position as Z zero
		poll_ok()

		print('Position set as new zero')

	write('$J=G21G91 Z{} F500'.format(dz))	# Back up to safe height
	poll_ok()

	return z_pos

def make_grid(nx, ny):
	xcoords = np.arange(0, nx)
	ycoords = np.arange(0, ny)

	for i in xcoords:
		for j in ycoords:
			yield (i, j)
		ycoords = ycoords[::-1] # Reverse direction so we go up and down the columns

def unlevel():
	global x_points, y_points, z_points, f
	x_points = np.arange(2)
	y_points = np.arange(2)
	z_points = np.zeros((2, 2))
	np.savetxt('level/y_points', y_points)
	np.savetxt('level/x_points', x_points)
	np.savetxt('level/z_points', z_points)

	f = interp2d(x_points, y_points, z_points)
	status.add_info_message('Reset the level plane to zero')

def probe_grid(dx, dy, dz):
	global x_points, y_points, z_points, f, terminate
	bounds = get_shape_objects_gcode_bounding_box()
	rangex = bounds[2] - bounds[0]
	rangey = bounds[3] - bounds[1]

	print(bounds)

	write('G10 P0 L20 X0 Y0 Z0')	# Set current position as zero
	poll_ok()
	machine_z_zero = probe(dz, True)
	print(machine_z_zero)

	# Find nx and ny
	nx = int(rangex / dx + 1)
	ny = int(rangey / dy + 1)

	print("Number of samples in x: ", nx)
	print("Number of samples in y: ", ny)

	z_points = np.zeros((ny, nx))
	x_points = np.arange(nx)*dx + bounds[0]
	y_points = np.arange(ny)*dy + bounds[1]

	print(x_points.min(), x_points.max())
	print(y_points.min(), y_points.max())
	current = 0

	for (i, j) in make_grid(nx, ny):
		print("0")
		if terminator.termination_pending(): 
			print("BYE")
			unlevel()
			return f

		print("1")
		write('G1 X{} Y{} F500'.format(x_points[i], y_points[j])) # Move to point p
		print("2")
		poll_ok()
		print("3")

		z_pos = probe(dz) # Probe at that point
		print("4")
		if z_pos == -10000: # Error code
			print("BYE")
			unlevel()
			return f
		print("5")

		z_points[j, i] = z_pos - machine_z_zero # Find depth of this point relative to 0
		print("6")
		current += 1
		print("7")
		status.add_info_message('Leveling {0:.2f}% complete'.format(current / (nx*ny) * 100))
		print("8")

	np.savetxt('level/y_points', y_points)
	np.savetxt('level/x_points', x_points)
	np.savetxt('level/z_points', z_points)
	f = interp2d(x_points, y_points, z_points)

	write('G1 Z5 F500')	# Back up to safe height
	poll_ok()

	write('G1 X0 Y0 F500') # Goto 0 0
	poll_ok()

	print("BYE")

	return f

def draw_perimeter(gcode_object):
	write('G1 X{} Y{} Z20 F500'.format(gcode_object.bounds[0], gcode_object.bounds[1]))
	write('G1 X{} Y{} Z20 F500'.format(gcode_object.bounds[0], gcode_object.bounds[3]))
	write('G1 X{} Y{} Z20 F500'.format(gcode_object.bounds[2], gcode_object.bounds[3]))
	write('G1 X{} Y{} Z20 F500'.format(gcode_object.bounds[2], gcode_object.bounds[1]))
	write('G1 X{} Y{} Z20 F500'.format(gcode_object.bounds[0], gcode_object.bounds[1]))
	write('G1 X0 Y0 Z1 F500')

def level_arg_error():
	status.add_error_message('You must have 2 arguments for the LEVEL command and an optional third argument: \n\tstep size in X (mm) \n\tstep size in Y (mm) \n\tsafety height multiplier')

def predict_arg_error():
	status.add_error_message('You must have 2 arguments for the PREDICT command: \n\tposition in X (mm) \n\tposition in Y(mm)')

def raise_arg_error():
	status.add_error_message('There is one optional argument for the RAISE / R command: \n\t+Z offset increment in mm')

def lower_arg_error():
	status.add_error_message('There is one optional argument for the LOWER / L command: \n\t-Z offset increment in mm')

def warp_arg_error():
	status.add_error_message("You must have 3 arguments for the WARP command and an optional fourth argument: \n\tX, Y, Z the position you would like to travel to in mm\n\tF the feed rate (int)")

# def load_gcodes():
# 	global gf_contours, gf_drills

# 	temp_file = open('resources/contours.gcode', 'r')
# 	gf_contours.load(temp_file.read())
# 	temp_file.close()
# 	gf_contours.bisect_codes()

# 	temp_file = open('resources/drills.gcode', 'r')
# 	gf_drills.load(temp_file.read())
# 	temp_file.close()
# 	gf_drills.bisect_codes()

# 	#gf_drills.y_offset = 0.25 # Permenantly make the drills compensate for bit travelling

terminator = TerminateObject()
commands = CommandObjectList()

# gf_contours = GCodeFile()
# gf_drills = GCodeFile()

y_points = np.loadtxt('level/y_points')
x_points = np.loadtxt('level/x_points')
z_points = np.loadtxt('level/z_points')

f = interp2d(x_points, y_points, z_points)

# load_gcodes()
