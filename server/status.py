class STATUS:
	OKAY = "Ok"
	CONTOUR_DISTANCE_TOO_LARGE = "Contour distance too large"
	CNC_MACHINE_NOT_CONNECTED = "No CNC machine is connected"

class MESSAGE_TYPE:
	INFO = "info"
	WARNING = "warning"
	ERROR = "error"
	INPUT = "input"

def add_message(type, message):
	global current_status_message_id

	m = {
		'id': current_status_message_id,
		'type': type,
		'message': message
	}
	status_messages.insert(0, m)

	if len(status_messages) > STATUS_MESSAGES_MAX_LENGTH:
		status_messages.pop()

	current_status_message_id += 1

def add_input_message(message):
	add_message(MESSAGE_TYPE.INPUT, message)

def add_error_message(message):
	add_message(MESSAGE_TYPE.ERROR, message)

def add_warning_message(message):
	add_message(MESSAGE_TYPE.WARNING, message)

def add_info_message(message):
	add_message(MESSAGE_TYPE.INFO, message)

current_status_message_id = 0
status_messages = []
STATUS_MESSAGES_MAX_LENGTH = 1000