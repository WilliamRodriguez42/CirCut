from status import add_error_message

def is_integer(n):
	if isinstance(n, int):
		return True
	if isinstance(n, float):
		return n.is_integer()
	return False

def is_float(n):
	return isinstance(n, float) or isinstance(n, int)

def is_bool(b):
	return isinstance(n, bool)



settings_check_map = {
	"Buffer Resolution": check_buffer_resolution,
	"Calculate Origin": check_calculate_origin,
	"Contour Count": check_contour_count,
	"Contour Distance": check_contour_distance,
	"Spindle Speed": check_spindle_speed,
	"Contour Step": check_contour_step,
	"Flip X Axis": check_flip_x_axis,
	"Bit Travel X": check_bit_travel_x,
	"Bit Travel Y": check_bit_travel_y,
	"Pass Feedrate": check_pass_feedrate,
	"Plunge Depth": check_plunge_depth,
	"Plunge Feedrate": check_plunge_feedrate,
	"Rapid Feedrate": check_rapid_feedrate,
	"Resolution": check_resolution,
	"Safe Height": check_safe_height,
	"X Offset": check_x_offset,
	"Y Offset": check_y_offset,
}

def check_settings(settings):
	for setting, value in settings.items():
		settings_check_map[setting](value)

def check_buffer_resolution(buffer_resolution):
	flag = is_integer(buffer_resolution) and buffer_resolution > 0 and buffer_resolution < 20
	if not flag:
		add_error_message("Invalid buffer resolution: must be an integer greater than 0 and less than 20")
	return flag

def check_calculate_origin(calculate_origin):
	flag = is_bool(calculate_origin)
	if not flag:
		add_error_message("Invalid calculate origin: must be a boolean")
	return flag

def check_contour_count(contour_count):
	flag = is_integer(contour_count) and contour_count >= 0
	if not flag:
		add_error_message("Invalid contour count: must be an integer greater than or equal to 0")
	return flag

def check_contour_distance(contour_distance):
	flag = is_float(contour_count) and contour_distance >= 0
	if not flag:
		add_error_message("Invalid contour distance: must be a value greater than or equal to 0")
	return flag

def check_spindle_speed(spindle_speed):
	flag = is_integer(spindle_speed) and spindle_speed > 0 and spindle_speed < 1024
	if not flag:
		add_error_message("Invalid spindle speed: must be an integer greater than 0 and less than 1024")
	return flag

def check_contour_step(contour_step):
	flag = is_float(contour_step)
	if not flag:
		add_error_message("Invalid contour step: must be a number")
	return flag

def check_flip_x_axis(flip_x_axis):
	flag = is_bool(flip_x_axis)
	if not flag:
		add_error_message("Invalid flip x axis: must be a boolean")
	return flag

def check_bit_travel_x(bit_travel_x):
	flag = is_float(bit_travel_x)
	if not flag:
		add_error_message("Invalid bit travel x: must be a number")
	return flag

def check_bit_travel_y(bit_travel_y):
	flag = is_float(bit_travel_y)
	if not flag:
		add_error_message("Invalid bit travel y: must be a number")
	return flag

def check_pass_feedrate(pass_feedrate):
	flag = is_float(pass_feedrate) and pass_feedrate > 0
	if not flag:
		add_error_message("Invalid pass feedrate: must be a value greater than 0")
	return flag

def check_plunge_depth(plunge_depth):
	flag = is_float(plunge_depth) and plunge_depth < 0
	if not flag:
		add_error_message("Invalid plunge depth: must be a value less than 0")
	return flag

def check_plunge_feedrate(plunge_feedrate):
	flag = is_float(plunge_feedrate) and plunge_feedrate > 0
	if not flag:
		add_error_message("Invalid plunge feedrate: must be a value greater than 0")
	return flag

def check_rapid_feedrate(rapid_feedrate):
	flag = is_float(rapid_feedrate) and rapid_feedrate > 0
	if not flag:
		add_error_message("Invalid rapid feedrate: must be a value greater than 0")
	return flag

def check_resolution(resolution):
	flag = is_integer(resolution) and resolution >= 3 and resolution <= 60
	if not flag:
		add_error_message("Invalid resolution: must be an integer greater than or equal to 3 and less than or equal to 60")
	return flag

def check_safe_height(safe_height):
	flag = is_float(safe_height) and safe_height > 0
	if not flag:
		add_error_message("Invalid safe height: must be a value greater than 0")
	return flag

def check_x_offset(x_offset):
	flag = is_float(x_offset)
	if not flag:
		add_error_message("Invalid x offset: must be a number")
	return flag

def check_y_offset(y_offset):
	flag = is_float(y_offset)
	if not flag:
		add_error_message("Invalid y offset: must be a number")
	return flag
