from flask import Flask, Response, request
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
	gtg = GTG()
	gtg.load_gerber("resources/gerber.gbr", contour_distance=0.099, contour_count=2, contour_step=0.15)
	gtg.load_excellon("resources/excellon.drl")
	gtg.update_translation()
	gtg.write_svg("../client/resources/test.svg")
	gtg.write_gcode("resources/contours.gcode", "../resources/drills.gcode")
	return Response("OK")
	
commands = []
terminate = False
