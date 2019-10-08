from flask import Flask, Response, request, jsonify, abort
from helper_functions import *
import threading
from gerber_to_gcode.gtg import GTG, STATUS
from status import *
import bleach
from pathvalidate import sanitize_filename
import os
import glob

# set the project root directory as the static folder
app = Flask(__name__)

@app.route('/<path:path>', methods=['GET'])
def send_whatever(path):
	ext = path[path.rfind('.')+1:]
	file = open('../client/' + path, 'rb')
	content = file.read()
	file.close()

	if ext == 'ico':
		response = Response(content, mimetype='image/vnd.microsoft.icon')
		print("HI")

	elif ext == 'css':
		response = Response(content, mimetype="text/css")

	elif ext == 'svg':
		response = Response(content, mimetype="image/svg+xml")

	else:
		response = Response(content)

	return response

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

	text = request.form['command'].strip()
	add_input_message(text)

	if not status.cnc_machine_connected:
		add_error_message(STATUS.CNC_MACHINE_NOT_CONNECTED)
		return Response("Ok")

	text = text.lower()
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
	global progress_text, progress_step, progress_load_svg, gtg_status

	if progress_step != PROGRESS_TOTAL_STEPS:
		abort(409); # Conflict
		return;

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
	gtg.write_svg("resources/preview.svg")

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

	progress_text = "Ready to convert"
	progress_step += 1
	print(progress_text)

	return Response("OK")

@app.route('/status', methods=['GET'])
def convert_progress():
	return jsonify({
		'step': progress_step,
		'of': PROGRESS_TOTAL_STEPS,
		'text': progress_text,
		'load_svg': progress_load_svg,
		'status_messages': status_messages
	})

@app.route('/svg', methods=['GET'])
def get_svg():
	svg = open('resources/preview.svg', 'r')
	content = svg.read()
	svg.close()

	return Response(content)

@app.route('/archive-message', methods=['POST'])
def archive_message():
	type = request.form['type'].lower().strip()
	message = request.form['message']

	add_message(type, message)

	return Response("Ok")

@app.route('/save-settings-profile', methods=['POST'])
def save_settings_profile():
	form = json.loads(request.data)

	settings_profile_name = form['name']
	settings_profile_name = sanitize_filename(settings_profile_name)
	if not settings_profile_name: return
	form['name'] = settings_profile_name

	profile_path = os.path.join("settings_profiles", settings_profile_name);
	content = json_dumps(form)

	profile = open(profile_path, 'w+')
	profile.write(content)
	profile.close()

	return Response("Ok")

@app.route('/get-settings-profile-names', methods=['GET'])
def get_settings_profile_names():
	settings_profile_names = glob.glob('settings_profiles/*.cnc_profile')
	result = [s[len("settings_profiles/"):] for s in settings_profile_names]
	return Response(json_dumps(result))

@app.route('/load-settings-profile/<path:path>', methods=['GET'])
def load_settings_profile(path):
	path = os.path.join('settings_profiles', path)

	if not glob.glob(path):
		return Response("File does not exist")

	file = open(path, 'r')
	content = file.read()
	file.close()

	return Response(content)

@app.route('/auto_save', methods=['POST'])
def auto_save():
	form = json.loads(request.data)
	content = json_dumps(form)

	auto_save_file = open("auto_save_profile/.auto_save_cnc_profile", "w+")
	auto_save_file.write(content)
	auto_save_file.close()

	return Response("Ok")

@app.route('/restore_from_auto_save', methods=['GET'])
def restore_from_auto_save():
	path = os.path.join('auto_save_profile', '.auto_save_cnc_profile')

	if not glob.glob(path):
		return Response("File does not exist")

	file = open(path, 'r')
	content = file.read()
	file.close()

	return Response(content)

commands = []
terminate = False

# Start in the ready state
PROGRESS_TOTAL_STEPS = 7
progress_step = PROGRESS_TOTAL_STEPS
progress_text = "Ready to convert"
progress_load_svg = False
