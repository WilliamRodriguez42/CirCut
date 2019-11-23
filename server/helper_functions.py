from serial_communication import *
import numpy as np
from scipy.interpolate import interp2d
from GCodeLib.GCode import GCodeFile
import re
import json

def json_dumps(form):
	content = json.dumps(form, sort_keys=True, indent=4)
	content = re.sub('\n +', lambda match: '\n' + '\t' * (len(match.group().strip('\n')) // 3), content) # snake-case, hard-tabs, keep it together!
	return content

def sanitize_filename(filename):
	prev_filename = filename
	attempts = 0
	while True: # Sanitize until we know the name is clean
		filename = bleach.clean(filename)
		filename = sanitize_filename(filename)
		if prev_filename == filename:
			return filename
		prev_filename = filename

		attempts += 1
		if (attempts > 2): return False

def probez():
	poll_ok()
	write('G38.3 Z-100 F50')	 # Probe for contact
	poll_ok()

	write('G10 P0 L20 X0 Y0 Z0')	# Set current position as zero
	poll_ok()

	write('G1 Z1 F500')

def probe(dz, initial=False):
	poll_ok()
	write('G38.3 Z-100 F50')	 # Probe for contact
	poll_ok()

	write('G4 P0.01') # Wait for task to complete
	poll_ok()

	z_pos_match = re.match(r'.*,([^,]*?):.*', last_received[2]) # Get the result of the serial
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


def probe_grid(dx, dy, dz):
	global x_points, y_points, z_points, f, terminate
	write('G10 P0 L20 X0 Y0 Z0')	# Set current position as zero
	poll_ok()
	machine_z_zero = probe(dz, True)

	# Find nx and ny
	nx = int(gf_contours.rangex / dx + 1)
	ny = int(gf_contours.rangey / dy + 1)

	print("Number of samples in x: ", nx)
	print("Number of samples in y: ", ny)

	z_points = np.zeros((ny, nx))
	x_points = np.zeros(nx)
	y_points = np.zeros(ny)

	for (i, j) in make_grid(nx, ny):
		if terminate: break
		xp = i*dx + gf_contours.minx
		yp = j*dy + gf_contours.miny

		x_points[i] = xp
		y_points[j] = yp

		write('G1 X{} Y{} F500'.format(xp, yp)) # Move to point p
		poll_ok()
		z_pos = probe(dz) # Probe at that point
		if z_pos == -10000: # Error code
			return

		z_points[j, i] = z_pos - machine_z_zero # Find depth of this point relative to 0

		for y in reversed(range(ny)):
			row = ''
			for x in range(nx):
				row += '{0:.3f}'.format(z_points[y, x]) + '\t'
			print(row)

	np.savetxt('level/y_points', y_points)
	np.savetxt('level/x_points', x_points)
	np.savetxt('level/z_points', z_points)
	f = interp2d(x_points, y_points, z_points)

	write('G1 Z5 F500')	# Back up to safe height
	poll_ok()

	write('G1 X0 Y0 F500') # Goto 0 0
	poll_ok()

	return f

def draw_perimeter():
	global gf_contours
	write('G1 X{} Y{} Z20 F500'.format(gf_contours.minx, gf_contours.miny))
	write('G1 X{} Y{} Z20 F500'.format(gf_contours.minx, gf_contours.maxy))
	write('G1 X{} Y{} Z20 F500'.format(gf_contours.maxx, gf_contours.maxy))
	write('G1 X{} Y{} Z20 F500'.format(gf_contours.maxx, gf_contours.miny))
	write('G1 X{} Y{} Z20 F500'.format(gf_contours.minx, gf_contours.miny))
	write('G1 X0 Y0 Z1 F500')

def level_arg_error():
	print('You must have 2 arguments for the LEVEL command: \n\tstep size in X (mm) \n\tstep size in Y (mm)')

def predict_arg_error():
	print('You must have 2 arguments for the PREDICT command: \n\tposition in X (mm) \n\tposition in Y(mm)')

def raise_arg_error():
	print('There is one optional argument for the RAISE / R command: \n\t+Z offset increment in mm')

def lower_arg_error():
	print('There is one optional argument for the LOWER / L command: \n\t-Z offset increment in mm')

def warp_arg_error():
	print("You must have 3 arguments for the WARP command and an optional fourth argument: \n\tX, Y, Z the position you would like to travel to in mm\n\tF the feed rate (int)")

def up_arg_error():
	print("There is one optional argument for the UP / U command: \n\t+Y offset increment in mm")

def down_arg_error():
	print("There is one optional argument for the DOWN / D command: \n\t-Y offest increment in mm")

def load_gcodes():
	global gf_contours, gf_drills

	temp_file = open('resources/contours.gcode', 'r')
	gf_contours.load(temp_file.read(), f)
	temp_file.close()
	#gf_contours.bisect_codes()

	temp_file = open('resources/drills.gcode', 'r')
	gf_drills.load(temp_file.read(), f)
	temp_file.close()
	#gf_drills.bisect_codes()

	gf_drills.y_offset = 0.25 # Permenantly make the drills compensate for bit travelling

terminate = False
commands = []

gf_contours = GCodeFile()
gf_drills = GCodeFile()

y_points = np.loadtxt('level/y_points')
x_points = np.loadtxt('level/x_points')
z_points = np.loadtxt('level/z_points')
f = interp2d(x_points, y_points, z_points)

load_gcodes()
