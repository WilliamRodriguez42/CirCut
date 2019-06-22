from serial import Serial, SerialException
import time
import sys
import os
import threading
from serial_communication import *
from routes import *
from helper_functions import *

if os.name == 'nt':
	from windows_inhibitor import WindowsInhibitor

#os.startfile("http://localhost:5000")

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

					dz = sqrt(dx ** 2 + dy ** 2) * 0.1
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

def start_threads():
	global t
	t = threading.Thread(target = constant_read)
	t.daemon = True
	t.start()

	command_thread = threading.Thread(target = execute_commands)
	command_thread.daemon = True
	command_thread.start()

if __name__ == '__main__':
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
