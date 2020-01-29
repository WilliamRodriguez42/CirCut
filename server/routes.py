from flask import Flask, Response, request, jsonify, abort, render_template, Markup
import helper_functions as hf
from helper_functions import *
import threading
from status import *
import bleach
from pathvalidate import sanitize_filename
import os
import glob
import time
import serial_communication as sc
from shape_object.convert_to_shape_object import conversion_map
from shape_object.shape_object import add_shape_object_to_list, remove_shape_object_from_list, find_shape_object_with_id, get_active_shape_objects, move_shape_object_after_id
from settings_management.defaults import extension_uses_profile, default_profile_layouts, iterable_default_layout

# set the project root directory as the static folder
app = Flask(__name__, template_folder='../client/templates')

@app.route('/<path:path>', methods=['GET'])
def send_whatever(path):
	ext = path[path.rfind('.')+1:]
	file = open('../client/' + path, 'rb')
	content = file.read()
	file.close()

	if ext == 'ico':
		response = Response(content, mimetype='image/vnd.microsoft.icon')

	elif ext == 'css':
		response = Response(content, mimetype="text/css")

	elif ext == 'svg':
		response = Response(content, mimetype="image/svg+xml")

	else:
		response = Response(content)

	return response

@app.route('/')
def send_home():
	return render_template('index.html', layout=iterable_default_layout, svg_element_content=Markup(open("../client/images/Origin.svg").read()))

@app.route('/contours', methods=['GET'])
def receive_contours():
	# gf_contours.update_content(hf.f)
	return Response('')

@app.route('/drills', methods=['GET'])
def receive_drills():
	# gf_drills.update_content(hf.f)
	return Response('')

@app.route('/command', methods=['POST'])
def receive_command():
	text = request.form['command'].strip()
	add_input_message(text)

	if not status.cnc_machine_connected:
		add_error_message(STATUS.CNC_MACHINE_NOT_CONNECTED)
		return Response("Ok")

	text = text.lower()
	if (text == 's' or text == 'stop'):
		hf.commands = []
		hf.terminate = True
		print("User interrupt... raising head and returning to zero in X and Y axis only")
		poll_ok()
		write('G1 Z3 F500')	# Back up to safe height
		write('G1 X0 Y0 F500')
		write('M5')
		poll_ok()

		while (hf.terminate):
			time.sleep(1)

		print("TERMINATED")
		return Response("Ok")

	hf.commands.append(text)
	return Response("Ok")

@app.route('/file_upload', methods=['POST'])
def file_upload():
	# Convert the input file into a shape object
	file = request.files['file']
	period_index = file.filename.rfind('.')
	extension = file.filename[period_index+1:]

	if extension in conversion_map:
		content = file.read().decode('UTF-8')

		shape_object = conversion_map[extension](content)
		if shape_object is None:
			add_error_message("There was an issue converting the file")
			abort(409) # Need better status (Could not convert)
			return

		profile_name = extension_uses_profile[extension]
		profile = default_profile_layouts[profile_name]

		shape_object.layout = profile['layout']
		shape_object.update_minor_settings()
		shape_object.name = file.filename
		add_shape_object_to_list(shape_object)

		return jsonify({
			'layout': shape_object.layout,
			'name': shape_object.name,
			'shape_object_id': shape_object.id
		})
	else:
		add_error_message("File type uknown: {}".format(extension))
		abort(409) # Need better status (Extension not supported)

@app.route('/delete_shape_object', methods=['POST'])
def delete_shape_object():
	shape_object_id = int(request.form['shape_object_id'][13:])
	remove_shape_object_from_list(shape_object_id)
	return Response("Ok")

@app.route('/get_uploaded_files', methods=['GET'])
def get_uploaded_files():
	result = []
	for shape_object in get_active_shape_objects():
		result.append({
			'layout': shape_object.layout,
			'name': shape_object.name,
			'shape_object_id': shape_object.id
		})
	return jsonify(result)

@app.route('/get_svg_for_id', methods=['POST'])
def get_svg_for_id():
	shape_object_id = int(request.form['shape_object_id'][13:])
	shape_object = find_shape_object_with_id(shape_object_id)
	return {
		'thumbnail': shape_object.get_thumbnail_svg(),
		'preview': shape_object.get_preview_svg()
	}

@app.route('/get_thumbnail_svg_for_id', methods=['POST'])
def get_thumbnail_svg_for_id():
	shape_object_id = request.form['shape_object_id']
	shape_object_id = int(shape_object_id[13:])

	shape_object = find_shape_object_with_id(shape_object_id)
	return shape_object.get_thumbnail_svg()

@app.route('/get_preview_svg_for_id', methods=['POST'])
def get_preview_svg_for_id():
	shape_object_id = request.form['shape_object_id']
	shape_object_id = int(shape_object_id[13:])

	shape_object = find_shape_object_with_id(shape_object_id)
	return shape_object.get_preview_svg()

@app.route('/update_shape_object_layout', methods=['POST'])
def update_shape_object_layout():
	form = json.loads(request.data)

	shape_object_id = form['shape_object_id'][13:]
	shape_object_id = int(shape_object_id)

	shape_object = find_shape_object_with_id(shape_object_id)
	if shape_object is None:
		add_error_message('Could not update shape object layout: specified file not found, server out of sync')
		abort(400)
		return

	shape_object.update_layout(form['layout'])

	return Response('Ok')

@app.route('/convert', methods=['POST'])
def convert():
	global progress_text, progress_step, gtg_status
	form = json.loads(request.data)

	if progress_step != PROGRESS_TOTAL_STEPS:
		add_error_message('Could not convert: another conversion is already in progress')
		abort(409) # Conflict
		return

	shape_object_id = form['shape_object_id'][13:]
	shape_object_id = int(shape_object_id)

	shape_object = find_shape_object_with_id(shape_object_id)
	if shape_object is None:
		add_error_message('Could not convert: specified file not found, server out of sync')
		abort(400)
		return

	shape_object.update_layout(form['layout'])

	progress_step = 0

	progress_text = "Calculating paths..."
	progress_step += 1
	print(progress_text)
	shape_object.calculate_paths()

	progress_text = "Converting to SVG..."
	progress_step += 1
	print(progress_text)
	svg = shape_object.get_preview_svg()

	progress_text = "Converting to G Code..."
	progress_step += 1
	print(progress_text)
	shape_object.calculate_gcode()

	progress_text = "Adjusting G Code to bed level..."
	progress_step += 1
	print(progress_text)
	shape_object.bisect_codes()

	progress_text = "Ready to convert"
	progress_step += 1
	print(progress_text)

	return Response("OK")

@app.route('/status', methods=['GET'])
def convert_progress():
	result = jsonify({
		'step': progress_step,
		'of': PROGRESS_TOTAL_STEPS,
		'text': progress_text,
		'status_messages': status_messages,
	})
	return result

@app.route('/reorder_shape_objects', methods=['POST'])
def reorder_shape_objects():
	shape_object_id = int(request.form['shape_object_id'][13:])
	inject_before_id = int(request.form['inject_before_id'][13:])
	move_shape_object_after_id(shape_object_id, inject_before_id)
	return Response("Ok")

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

	profile_path = os.path.join("settings_profiles", settings_profile_name)
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

@app.route('/connect', methods=['POST'])
def connect():
	port = request.form['port']

	try:
		sc.ser = Serial(port, 115200)
	except:
		sc.ser = None

	return Response("Ok")

@app.route('/disconnect', methods=['POST'])
def disconnect():
	sc.ser = None
	return Response("Ok")

# Start in the ready state
PROGRESS_TOTAL_STEPS = 5
progress_step = PROGRESS_TOTAL_STEPS
progress_text = "Ready to convert"
