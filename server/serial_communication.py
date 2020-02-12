import time
import status
import glob
import threading
import os
import sys

cnc_connected = threading.Event()

PRGPATH=os.path.abspath(os.path.dirname(__file__))
sys.path.append(PRGPATH)
bCNC_path = os.path.join(PRGPATH, 'bCNC')
sys.path.append(bCNC_path)
sys.path.append(os.path.join(bCNC_path, 'lib'))
sys.path.append(os.path.join(bCNC_path, 'plugins'))
sys.path.append(os.path.join(bCNC_path, 'controllers'))

from Sender import Sender

sender = None
def constant_read():
	global sender
	sender = Sender()

def write(text):
	sender.sendGCode(text)

def get_machine_state():
	global last_received

	write('?')
	match = re.search(r'<(.*?)\|', last_received[1])
	if match is not None:
		return match[1]

	return ''

def connect(port):
	sender.open(port, 115200)
	cnc_connected.set()

def disconnect():
	sender.close()
	cnc_connected.clear()

def poll_ok(): # Must be called from the same thread that calls write(text)
	while len(sender.sline) != 0 or not sender.queue.empty():
		time.sleep(0.1)

def terminate():
	sender.stopRun()