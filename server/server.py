import time
import sys
import os
import threading
from serial_communication import *
import serial_communication as sc
import helper_functions as hf
from helper_functions import *
import routes
from routes import *
import status
import math

if os.name == 'nt':
	from windows_inhibitor import WindowsInhibitor

import getopt
import socket
import traceback
from datetime import datetime
import serial

PRGPATH=os.path.abspath(os.path.dirname(__file__))
sys.path.append(PRGPATH)
sys.path.append(os.path.join(PRGPATH, 'lib'))
sys.path.append(os.path.join(PRGPATH, 'plugins'))
sys.path.append(os.path.join(PRGPATH, 'controllers'))

# Load configuration before anything else
# and if needed replace the  translate function _()
# before any string is initialized
import Utils
Utils.loadConfiguration()

import rexx
import tkExtra
import Updates
import bFileDialog
import tkDialogs

from CNC import WAIT, CNC, GCode
import Ribbon
import Pendant
from Sender import Sender, NOT_CONNECTED, STATECOLOR, STATECOLORDEF

import CNCCanvas
import webbrowser

from CNCRibbon    import Page
from ToolsPage    import Tools, ToolsPage
from FilePage     import FilePage
from ControlPage  import ControlPage
from TerminalPage import TerminalPage
from ProbePage    import ProbePage
from EditorPage   import EditorPage

PRGPATH=os.path.abspath(os.path.dirname(__file__))
sys.path.append(PRGPATH)
bCNC_path = os.path.join(PRGPATH, 'bCNC')
sys.path.append(bCNC_path)
sys.path.append(os.path.join(bCNC_path, 'lib'))
sys.path.append(os.path.join(bCNC_path, 'plugins'))
sys.path.append(os.path.join(bCNC_path, 'controllers'))

#os.startfile("http://localhost:5000")

def execute_commands():
	while (True):
		hf.commands.wait_until_populated()
		text = hf.commands[0].text
		gcode_object = hf.commands[0].gcode_object

		parts = text.split()
		if len(parts) == 0: 
			hf.commands[0].set_complete()
			del hf.commands[0]

		# poll_ok()

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

		elif parts[0] == 'show_contour':
			content = ""
			status.add_info_message(gcode_object.get_content())
			print(content)

		elif parts[0] == 'send_gcode':
			for gcode in gcode_object.enumerate_gcodes():
				if hf.terminator.termination_pending(): break
				write(gcode)

		elif parts[0] == 'unlevel':
			# Make a default hf.f function
			hf.unlevel()

		elif parts[0] == 'r' or parts[0] == 'raise':
			# Raise the safety height
			if len(parts) == 2:
				try:
					amount = float(parts[1])
					gcode_object.z_offset += amount
					status.add_info_message('Z offset currently set to: {0:0.3f}'.format(gcode_object.z_offset))
				except ValueError:
					raise_arg_error()

			elif len(parts) == 1:
				gcode_object.z_offset += 0.02
				status.add_info_message('Z offset currently set to: {0:0.3f}'.format(gcode_object.z_offset))

			else:
				raise_arg_error()

		elif parts[0] == 'l' or parts[0] == 'lower':
			# lower the safety height
			if len(parts) == 2:
				try:
					amount = float(parts[1])
					gcode_object.z_offset -= amount
					status.add_info_message('Z offset currently set to: {0:0.3f}'.format(gcode_object.z_offset))
				except ValueError:
					lower_arg_error()

			elif len(parts) == 1:
				gcode_object.z_offset -= 0.02
				status.add_info_message('Z offset currently set to: {0:0.3f}'.format(gcode_object.z_offset))

			else:
				lower_arg_error()

		elif parts[0] == 'state':
			status.add_info_message(get_machine_state())
		elif parts[0] == 'probez':
			probez()
		elif parts[0] == 'perim':
			draw_perimeter(gcode_object)
		elif parts[0] == 'overload_test':
			import random
			for i in range(10000):
				if hf.terminator.termination_pending():
					break
				write('G1 Z0 X{} Y{} F500'.format(random.random()*0.1, random.random()*0.1))
		elif parts[0] == 'debug':
			import pdb
			pdb.set_trace()
		else:
			write(text)

		if hf.commands[0] == hf.terminator:
			print("STOP COMMAND RECEIVED")
			sc.terminate()
			write('G1 Z3 F500')	# Back up to safe height
			write('G1 X0 Y0 F500')
			write('M5')

		hf.commands[0].set_complete()
		del hf.commands[0]

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
