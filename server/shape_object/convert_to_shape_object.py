from gerber_excellon_to_shape_object.gtso import GTSO
from gerber_excellon_to_shape_object.etso import ETSO

conversion_map = {
	'gbr': GTSO,
	'drl': ETSO,
	'txt': ETSO
}