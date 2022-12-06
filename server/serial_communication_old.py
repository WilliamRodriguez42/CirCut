from serial import Serial, SerialException
import time
import status
import glob
import threading
import pdb

"""import serial.tools.list_ports
ports = list(serial.tools.list_ports.comports())
for p in ports:
	print(dir(p))
	print(p.usb_info())
	print(p.device_path)"""

RX_BUFFER_SIZE = 64

ser = None
cnc_connected = threading.Event()
receive_ready = False

receive_buffer_size = 5
last_received = [''] * receive_buffer_size # Stores the last few commands
last_sent = []

last_sent_lock = threading.Lock()

queue_is_empty = threading.Event()
queue_is_empty.set()

ser_result = ''
def constant_read():
	global receive_ready, receiving, last_received, last_sent, ser, ser_result


	while True:
		cnc_connected.wait()

		ser_result += ser.read(1).decode('UTF-8')
		if '\r\n' in ser_result:
			index = ser_result.find('\r\n')

			last_complete_result = ser_result[:index].strip()
			# print(last_complete_result)

			last_received.insert(0, last_complete_result) # Put the new ser_result at the front of the buffer
			last_received.pop() # Remove the last element of the buffer

			ser_result = ser_result[index+2:]

			# if 'Grbl' in last_received[0]:
			# 	receive_ready = True

			if last_received[0] == 'ok' or 'error' in last_received[0]:
				# receive_ready = True
				with last_sent_lock:
					if len(last_sent) > 0:
						del last_sent[0]
					# print("DELETING NEW SIZE", sum(last_sent))

					if len(last_sent) == 0:
						queue_is_empty.set()

def get_machine_state():
	global last_received

	write('?')
	match = re.search(r'<(.*?)\|', last_received[1])
	if match is not None:
		return match[1]

	return ''

def write(text):
	global receive_ready, last_sent, ser

	text = text.strip() + '\r'

	# print("Waiting for buffer", sum(last_sent) + len(text), RX_BUFFER_SIZE)
	start_time = time.time()
	while sum(last_sent) + len(text) > RX_BUFFER_SIZE:
		if time.time() - start_time > 10:
			print("WAITING FOR BUFFER TIMEOUT")
			pdb.set_trace()
	# print("SPACE IN BUFFER", sum(last_sent) + len(text), RX_BUFFER_SIZE)

	# receive_ready = False
	# print(text)

	with last_sent_lock:
		last_sent.append(len(text))
		queue_is_empty.clear()

		ser.write(text.encode())
		ser.flush()

def poll_ok(): # Must be called from the same thread that calls write(text)
	global receive_ready
	# while not receive_ready or len(last_sent) > 0:
	# 	time.sleep(0.01)
	queue_is_empty.wait()

def connect(port):
	global ser, cnc_connected
	ser = Serial(port, baudrate=115200, timeout=1, write_timeout=0)
	cnc_connected.set()

def disconnect():
	global ser, cnc_connected
	# ser.close()
	ser = None
	cnc_connected.clear()