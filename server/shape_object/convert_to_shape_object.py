from gerber_excellon_to_shape_object.gtso import gerber_to_shape_object
from gerber_excellon_to_shape_object.etso import excellon_to_shape_object

conversion_map = {
	'gbr': gerber_to_shape_object,
	'drl': excellon_to_shape_object,
	'txt': excellon_to_shape_object
}