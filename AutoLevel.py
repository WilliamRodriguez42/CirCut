from serial import Serial, SerialException
from threading import Thread
import time
import sys
import numpy as np
import re
import os
from GCode import GCodeFile
from scipy.interpolate import interp2d
import io
from importlib import reload

if os.name == 'nt':
	from WindowsInhibitor import WindowsInhibitor
	
from flask import Flask, Response, request
import os
import threading

#os.startfile("http://localhost:5000")

RX_BUFFER_SIZE = 64

ser = None
receive_ready = False

receive_buffer_size = 5
last_received = [''] * receive_buffer_size # Stores the last few commands
last_sent = []

def constant_read():
	global receive_ready, receiving, last_received, last_sent, ser
	result = ''

	while (ser == None):
		try:
			ser = Serial("COM9", 115200)
			time.sleep(0.1)
		except SerialException:
			sys.stdout.write("\rNo CNC machine found on COM7, please plug in or turn on machine.")
			sys.stdout.flush()

	while True:

		to_read = ser.inWaiting()
		if to_read:
			result += ser.read(to_read).decode('UTF-8')
			while '\r\n' in result:
				index = result.find('\r\n')

				last_complete_result = result[:index].strip()
				print(last_complete_result + '\n')

				last_received.insert(0, last_complete_result) # Put the new result at the front of the buffer
				last_received.pop() # Remove the last element of the buffer

				result = result[index+2:]

				if 'Grbl' in last_received[0]:
					receive_ready = True

				if last_received[0] == 'ok' or 'error' in last_received[0]:
					receive_ready = True
					del last_sent[0]

def get_machine_state():
	global last_received

	write('?')
	match = re.search(r'<(.*?)\|', last_received[1])
	if match is not None:
		return match[1]

	return ''

def write(text):
	global receive_ready, last_sent

	text = text.strip()

	while sum(last_sent) + len(text) + 1 > RX_BUFFER_SIZE:
		pass

	receive_ready = False
	print(text)

	last_sent.append(len(text) + 1)

	if ser == None:
		return

	ser.write((text + '\r').encode())
	ser.flush()

def poll_ok():
	global receive_ready
	while not receive_ready or len(last_sent) > 0:
		time.sleep(0.01)

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

y_points = np.loadtxt('y_points')
x_points = np.loadtxt('x_points')
z_points = np.loadtxt('z_points')
f = interp2d(x_points, y_points, z_points)
def probe_grid(dx, dy, dz):
	global x_points, y_points, z_points, f
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

	np.savetxt('y_points', y_points)
	np.savetxt('x_points', x_points)
	np.savetxt('z_points', z_points)
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

def start_receive_thread():
	global t
	t = Thread(target = constant_read)
	t.daemon = True
	t.start()

pygcode = None
def load_gcode(file_path, gf):
	global pygcode, f

	# Linearize the file
	"""print("Linearizing GCode file...")
	sys.argv = [sys.argv[0], '-s', '-f', '-rc', '-rb', '-al', '-ce', file_path]

	old_stdout = sys.stdout

	result = io.StringIO()
	sys.stdout = result

	if pygcode is None:
		pygcode = __import__('pygcode-norm')
	else:
		reload(pygcode)

	sys.stdout = old_stdout

	content = result.getvalue()

	result.close()"""

	temp_file = open(file_path, 'r')
	content = temp_file.read()
	temp_file.close()

	gf.load(content)
	gf.bisect_codes()

	return gf.get_content(f)

def write_contours():
	global gf_contours
	temp_file = open('contours.gcode', 'w')
	temp_file.write(request.form['contours'])
	temp_file.close()
	load_gcode('contours.gcode', gf_contours)

def write_drills():
	global gf_drills
	temp_file = open('drills.gcode', 'w')
	temp_file.write(request.form['drills'])
	temp_file.close()
	load_gcode('drills.gcode', gf_drills)

gf_contours = GCodeFile()
temp_file = open('contours.gcode', 'r')
gf_contours.load(temp_file.read())
temp_file.close()
gf_contours.bisect_codes();

gf_drills = GCodeFile()
temp_file = open('drills.gcode', 'r')
gf_drills.load(temp_file.read())
temp_file.close()
gf_drills.bisect_codes()

gf_drills.y_offset = 0.25 # Permenantly make the drills compensate for bit travelling

# set the project root directory as the static folder, you can set others.
app = Flask(__name__)

@app.route('/<path:path>')
def send_js(path):
	html = open(path, 'r')
	print(path)
	if path[-3:] == 'css':
		return Response(html.read(), mimetype="text/css")

	return Response(html.read())

@app.route('/')
def send_home():
	html = open('client/index.html', 'r')
	return Response(html.read())

@app.route('/contours', methods=['POST', 'GET'])
def receive_contours():
	if request.method == 'POST':
		write_contours()

	return Response(gf_contours.get_content(f))

@app.route('/drills', methods=['POST', 'GET'])
def receive_drills():
	if request.method == 'POST':
		write_drills()

	return Response(gf_drills.get_content(f))

@app.route('/command', methods=['POST'])
def receive_command():
	global commands, terminate
	text = request.form['command'].lower().strip()
	if (text == 's' or text == 'stop'):
		commands = []
		terminate = True
		print("User interrupt... raising head and returning to zero in X and Y axis only")
		poll_ok()
		write('G1 Z3 F500')	# Back up to safe height
		write('G1 X0 Y0 F500')
		write('M5')
		poll_ok()

		while (terminate):
			pass

		print("TERMINATED")

	commands.append(text)
	return Response("Ok")

commands = []
terminate = False
def execute_commands():
	global f, gf_contours, gf_drills, terminate

	while (True):
		while (len(commands) == 0):
			time.sleep(0.1) # Wait for command

		text = commands[0]
		del commands[0]

		poll_ok()

		parts = text.split()
		if len(parts) == 0: return

		if parts[0] == 'level':
			if len(parts) != 3:
				level_arg_error()
				return
			else:
				try:
					mx = int(parts[1])
					my = int(parts[2])

					dx = gf_contours.rangex
					dy = gf_contours.rangey

					while(dx > mx):
						dx /= 2

					while(dy > my):
						dy /= 2

					dz = np.sqrt(dx ** 2 + dy ** 2) * 0.1
					print("Safe height set to: ", dz)

					f = probe_grid(dx, dy, dz)
				except ValueError:
					level_arg_error()
					return

		elif parts[0] == 'exit':
			ser.close()

		elif parts[0] == 'zero':
			write('G10 P0 L20 X0 Y0 Z0')

		elif parts[0] == 'zone':
			write('G10 P0 L20 X0 Y0 Z1')

		elif parts[0] == 'predict':
			try:
				x = float(parts[1])
				y = float(parts[2])

				print('Depth at position ({0:.3f}, {0:.3f}): '.format(x, y) + str(f(x, y)))
			except ValueError:
				predict_arg_error()

		elif parts[0] == 'show':
			print(gf_drills.get_content(f))

		elif parts[0] == 'contour':
			for gcode in gf_contours.enumerate_gcodes(f):
				if terminate: break
				write(gcode)

		elif parts[0] == 'drill':
			for gcode in gf_drills.enumerate_gcodes(f):
				if terminate: break
				write(gcode)

		elif parts[0] == 'unlevel':
			# Make a default f function
			f = lambda x, y: [0]
			print('Reset the level plane to zero')

		elif parts[0] == 'r' or parts[0] == 'raise':
			# Raise the safety height
			if len(parts) == 2:
				try:
					amount = float(parts[1])
					gf_contours.z_offset += amount
					print('Z offset currently set to: {0:0.3f}'.format(gf_contours.z_offset))
				except ValueError:
					raise_arg_error()

			elif len(parts) == 1:
				gf_contours.z_offset += 0.02
				print('Z offset currently set to: {0:0.3f}'.format(gf_contours.z_offset))

			else:
				raise_arg_error()

		elif parts[0] == 'l' or parts[0] == 'lower':
			# lower the safety height
			if len(parts) == 2:
				try:
					amount = float(parts[1])
					gf_contours.z_offset -= amount
					print('Z offset currently set to: {0:0.3f}'.format(gf_contours.z_offset))
				except ValueError:
					lower_arg_error()

			elif len(parts) == 1:
				gf_contours.z_offset -= 0.02
				print('Z offset currently set to: {0:0.3f}'.format(gf_contours.z_offset))

			else:
				lower_arg_error()

		elif parts[0] == 'u' or parts[0] == 'up':
			# lower the safety height
			if len(parts) == 2:
				try:
					amount = float(parts[1])
					gf_drills.y_offset += amount
					print('Y offset currently set to: {0:0.3f}'.format(gf_contours.y_offset))
				except ValueError:
					up_arg_error()

			elif len(parts) == 1:
				gf_drills.y_offset += 0.25
				print('Y offset currently set to: {0:0.3f}'.format(gf_contours.y_offset))

			else:
				up_arg_error()

		elif parts[0] == 'd' or parts[0] == 'down':
			# lower the safety height
			if len(parts) == 2:
				try:
					amount = float(parts[1])
					gf_drills.y_offset -= amount
					print('Y offset currently set to: {0:0.3f}'.format(gf_contours.y_offset))
				except ValueError:
					down_arg_error()

			elif len(parts) == 1:
				gf_drills.y_offset -= 0.25
				print('Y offset currently set to: {0:0.3f}'.format(gf_contours.y_offset))

			else:
				down_arg_error()
		elif parts[0] == 'state':
			print(get_machine_state())
		elif parts[0] == 'probez':
			probez()
		elif parts[0] == 'perim':
			draw_perimeter()
		else:
			write(text)

		terminate = False

command_thread = threading.Thread(target = execute_commands)
command_thread.daemon = True
command_thread.start()

if __name__ == '__main__':
	if os.name == 'nt':
		wi = WindowsInhibitor()
		wi.inhibit()

	try:
		start_receive_thread()
		app.run()
	except Exception as e:
		print(e)

	if os.name == 'nt':
		wi.uninhibit()
