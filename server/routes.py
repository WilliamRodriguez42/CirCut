from flask import Flask, Response, request, jsonify
from helper_functions import *
import threading
from gerber_to_gcode.gtg import GTG

# set the project root directory as the static folder
app = Flask(__name__)

@app.route('/<path:path>')
def send_whatever(path):
	print(path)
	if path[-3:] == 'ico':
		ico = open('../client/' + path, 'rb')
		content = ico.read()
		ico.close()
		return Response(content)

	elif path[-3:] == 'css':
		css = open('../client/' + path, 'r')
		content = css.read()
		css.close()
		return Response(content, mimetype="text/css")

	elif path[-3:] == 'svg':
		svg = open('../client/' + path, 'r')
		content = svg.read()
		svg.close()
		return Response(content, mimetype="image/svg+xml")

	else:
		html = open('../client/' + path, 'r')
		content = html.read()
		html.close()
		return Response(content)

@app.route('/')
def send_home():
	html = open('../client/index.html', 'r')
	content = html.read()
	html.close()

	return Response(content)

@app.route('/contours', methods=['GET'])
def receive_contours():
	return Response(gf_contours.content)

@app.route('/drills', methods=['GET'])
def receive_drills():
	return Response(gf_drills.content)

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

@app.route('/file-upload', methods=['POST'])
def file_upload():
	file = request.files['file']
	if file.filename[-3:] == 'gbr':
		file.save('resources/gerber.gbr')
	elif file.filename[-3:] == 'drl':
		file.save('resources/excellon.drl')
	return Response("OK")

@app.route('/convert', methods=['POST'])
def convert():
	global progress_text, progress_step, progress_load_svg

	gtg = GTG()
	progress_step = 0
	progress_load_svg = False

	progress_text = "Loading GCode file..."
	progress_step += 1
	print(progress_text)
	gtg.load_gerber(
		"resources/gerber.gbr",
		contour_distance=float(request.form['contour_distance']),
		contour_count=int(request.form['contour_count']),
		contour_step=float(request.form['contour_step']),
		buffer_resolution=int(request.form['buffer_resolution']),
		resolution=int(request.form['resolution']))

	progress_text = "Loading Excellon file..."
	progress_step += 1
	print(progress_text)
	gtg.load_excellon(
		"resources/excellon.drl",
		resolution=int(request.form['resolution']))

	progress_text = "Combining GCode and Excellon files..."
	progress_step += 1
	print(progress_text)
	gtg.update_translation()

	progress_text = "Writing result to SVG format..."
	progress_step += 1
	print(progress_text)
	gtg.write_svg("resources/test.svg")

	progress_load_svg = True

	progress_text = "Writing result to GCode format..."
	progress_step += 1
	print(progress_text)
	gtg.write_gcode(
		"resources/contours.gcode",
		"resources/drills.gcode",
		rapid_feedrate=float(request.form['rapid_feedrate']),
		pass_feedrate=float(request.form['pass_feedrate']),
		plunge_feedrate=float(request.form['plunge_feedrate']),
		plunge_depth=float(request.form['plunge_depth']),
		safe_height=float(request.form['safe_height']),
		contour_spindle_speed=int(request.form['contour_spindle']),
		drill_spindle_speed=int(request.form['drill_spindle']))

	progress_text = "Switching to new GCode files..."
	progress_step += 1
	print(progress_text)
	load_gcodes()

	progress_text = "Complete"
	progress_step += 1
	print(progress_text)

	return Response("OK")

@app.route('/convert_progress', methods=['GET'])
def convert_progress():
	return jsonify({
		'step': progress_step,
		'of': progress_total_steps,
		'text': progress_text,
		'load_svg': progress_load_svg
	})

@app.route('/svg', methods=['GET'])
def get_svg():
	svg = open('resources/test.svg', 'r')
	content = svg.read()
	svg.close()

	return Response(content)

commands = []
terminate = False

progress_text = ""
progress_step = 0
progress_total_steps = 7
progress_load_svg = False
