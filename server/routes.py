from flask import Flask, Response, request
from helper_functions import *
import threading

# set the project root directory as the static folder
app = Flask(__name__)

@app.route('/<path:path>')
def send_js(path):
	html = open('../' + path, 'r')
	print(path)
	if path[-3:] == 'css':
		return Response(html.read(), mimetype="text/css")
	content = html.read()
	html.close()

	return Response(content)

@app.route('/')
def send_home():
	html = open('../client/index.html', 'r')
	content = html.read()
	html.close()

	return Response(content)

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
