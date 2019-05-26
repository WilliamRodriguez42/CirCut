from serial import Serial, SerialException
import time

RX_BUFFER_SIZE = 64

ser = None
receive_ready = False

receive_buffer_size = 5
last_received = [''] * receive_buffer_size # Stores the last few commands
last_sent = []

def constant_read():
	global receive_ready, receiving, last_received, last_sent, ser
	result = ''

	while (ser == None):
		try:
			ser = Serial("COM9", 115200)
		except SerialException:
			print("No CNC machine found on COM9, please plug in or turn on machine.")
			time.sleep(5)

	while True:
		to_read = ser.inWaiting()
		if to_read:
			result += ser.read(to_read).decode('UTF-8')
			while '\r\n' in result:
				index = result.find('\r\n')

				last_complete_result = result[:index].strip()
				print(last_complete_result + '\n')

				last_received.insert(0, last_complete_result) # Put the new result at the front of the buffer
				last_received.pop() # Remove the last element of the buffer

				result = result[index+2:]

				if 'Grbl' in last_received[0]:
					receive_ready = True

				if last_received[0] == 'ok' or 'error' in last_received[0]:
					receive_ready = True
					del last_sent[0]

def get_machine_state():
	global last_received

	write('?')
	match = re.search(r'<(.*?)\|', last_received[1])
	if match is not None:
		return match[1]

	return ''

def write(text):
	global receive_ready, last_sent

	text = text.strip()

	while sum(last_sent) + len(text) + 1 > RX_BUFFER_SIZE:
		pass

	receive_ready = False
	print(text)

	last_sent.append(len(text) + 1)

	if ser == None:
		return

	ser.write((text + '\r').encode())
	ser.flush()

def poll_ok():
	global receive_ready
	while not receive_ready or len(last_sent) > 0:
		time.sleep(0.01)
		
