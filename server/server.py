from serial import Serial, SerialException
import time
import sys
import os
import threading
from serial_communication import *
import helper_functions as hf
from helper_functions import *
import routes
from routes import *
import status
import math

if os.name == 'nt':
	from windows_inhibitor import WindowsInhibitor

#os.startfile("http://localhost:5000")

def execute_commands():
	while (True):
		while (len(hf.commands) == 0):
			time.sleep(0.1) # Wait for command
			hf.terminate = False


		text = hf.commands[0]
		del hf.commands[0]

		poll_ok()

		parts = text.split()
		if len(parts) == 0: continue

		if parts[0] == 'level':
			if len(parts) < 3 or len(parts) > 4:
				level_arg_error()
			else:
				safety_height_multiplier = 1
				if len(parts) == 4:
					safety_height_multiplier = float(parts[3])
				try:
					dx = float(parts[1])
					dy = float(parts[2])
					dz = math.sqrt(dx ** 2 + dy ** 2) * 0.2 * safety_height_multiplier
					status.add_info_message("Safe height set to: {}".format(dz))

					hf.f = probe_grid(dx, dy, dz)
					routes.client_load_gcodes = True
				except ValueError:
					level_arg_error()

		elif parts[0] == 'zero':
			write('G10 P0 L20 X0 Y0 Z0')

		elif parts[0] == 'zone':
			write('G10 P0 L20 X0 Y0 Z1')

		elif parts[0] == 'predict':
			try:
				x = float(parts[1])
				y = float(parts[2])

				status.add_info_message('Depth at position ({0:.3f}, {0:.3f}): '.format(x, y) + str(hf.f(x, y)))
			except ValueError:
				predict_arg_error()

		elif parts[0] == 'show':
			status.add_info_message(hf.gf_drills.get_content(hf.f))

		elif parts[0] == 'contour':
			for gcode in hf.gf_contours.enumerate_gcodes(hf.f):
				if hf.terminate: break
				write(gcode)

		elif parts[0] == 'drill':
			for gcode in hf.gf_drills.enumerate_gcodes(hf.f):
				if hf.terminate: break
				write(gcode)

		elif parts[0] == 'unlevel':
			# Make a default hf.f function
			hf.f = lambda x, y: [0]
			status.add_info_message('Reset the level plane to zero')
			routes.client_load_gcodes = True

		elif parts[0] == 'r' or parts[0] == 'raise':
			# Raise the safety height
			if len(parts) == 2:
				try:
					amount = float(parts[1])
					hf.gf_contours.z_offset += amount
					routes.client_load_gcodes = True
					status.add_info_message('Z offset currently set to: {0:0.3f}'.format(hf.gf_contours.z_offset))
				except ValueError:
					raise_arg_error()

			elif len(parts) == 1:
				hf.gf_contours.z_offset += 0.02
				status.add_info_message('Z offset currently set to: {0:0.3f}'.format(hf.gf_contours.z_offset))
				routes.client_load_gcodes = True

			else:
				raise_arg_error()

		elif parts[0] == 'l' or parts[0] == 'lower':
			# lower the safety height
			if len(parts) == 2:
				try:
					amount = float(parts[1])
					hf.gf_contours.z_offset -= amount
					routes.client_load_gcodes = True
					status.add_info_message('Z offset currently set to: {0:0.3f}'.format(hf.gf_contours.z_offset))
				except ValueError:
					lower_arg_error()

			elif len(parts) == 1:
				hf.gf_contours.z_offset -= 0.02
				status.add_info_message('Z offset currently set to: {0:0.3f}'.format(hf.gf_contours.z_offset))
				routes.client_load_gcodes = True

			else:
				lower_arg_error()

		elif parts[0] == 'state':
			status.add_info_message(get_machine_state())
		elif parts[0] == 'probez':
			probez()
		elif parts[0] == 'perim':
			draw_perimeter()
		else:
			write(text)

		hf.terminate = False

def start_threads():
	global t
	t = threading.Thread(target = constant_read)
	t.daemon = True
	t.start()

	command_thread = threading.Thread(target = execute_commands)
	command_thread.daemon = True
	command_thread.start()

if __name__ == '__main__':
	import logging
	log = logging.getLogger('werkzeug')
	log.setLevel(logging.ERROR)

	if os.name == 'nt':
		wi = WindowsInhibitor()
		wi.inhibit()

	try:
		start_threads()
		#app.run(host='0.0.0.0', port=5000)
		app.run()
	except Exception as e:
		print(e)

	if os.name == 'nt':
		wi.uninhibit()
