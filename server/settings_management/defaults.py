from collections import OrderedDict 

default_layout = OrderedDict()
default_layout["Rapid Feedrate"] = {
	'value': 500,
	'units': 'mm/min',
	'type': 'number',
}
default_layout["Pass Feedrate"] = {
	'value': 200,
	'units': 'mm/min',
	'type': 'number',
}
default_layout["Plunge Feedrate"] = {
	'value': 20,
	'units': 'mm/min',
	'type': 'number',
}
default_layout["Plunge Depth"] = {
	'value': -2.5,
	'units': 'mm',
	'type': 'number',
}
default_layout["Safe Height"] = {
	'value': 1,
	'units': 'mm',
	'type': 'number',
}
default_layout["Spindle Speed"] = {
	'value': 255,
	'units': '',
	'type': 'number',
}
default_layout["Contour Distance"] = {
	'value': 0.15,
	'units': 'mm',
	'type': 'number',
}
default_layout["Contour Count"] = {
	'value': 1,
	'units': '',
	'type': 'number',
}
default_layout["Contour Step"] = {
	'value': 0.15,
	'units': 'mm',
	'type': 'number',
}
default_layout["Resolution"] = {
	'value': 32,
	'units': '',
	'type': 'number',
}
default_layout["Buffer Resolution"] = {
	'value': 5,
	'units': '',
	'type': 'number',
}
default_layout["X Offset"] = {
	'value': 1,
	'units': 'mm',
	'type': 'number',
}
default_layout["Y Offset"] = {
	'value': 1,
	'units': 'mm',
	'type': 'number',
}
default_layout["Bit Travel X"] = {
	'value': 0.1,
	'units': 'mm',
	'type': 'number',
}
default_layout["Bit Travel Y"] = {
	'value': -0.1,
	'units': 'mm',
	'type': 'number',
}
default_layout["Calculate Origin"] = {
	'value': False,
	'units': '',
	'type': 'checkbox',
}
default_layout["Flip X Axis"] = {
	'value': False,
	'units': '',
	'type': 'checkbox',
}





required_path_vars = [
	"Rapid Feedrate",
	"Pass Feedrate",
	"Safe Height",
	"Spindle Speed",
	"Contour Distance",
	"Contour Count",
	"Contour Step",
	"Resolution",
	"Buffer Resolution",
	"X Offset",
	"Y Offset",
	"Calculate Origin",
	"Flip X Axis"
]

required_coord_vars = [
	"Rapid Feedrate",
	"Plunge Feedrate",
	"Plunge Depth",
	"Safe Height",
	"Spindle Speed",
	"Resolution",
	"Buffer Resolution",
	"X Offset",
	"Y Offset",
	"Bit Travel X",
	"Bit Travel Y",
	"Calculate Origin",
	"Flip X Axis"
]

default_profile_layouts = {
	'path_cnc_profile': {
		'required_vars': required_path_vars
	},
	'coord_cnc_profile': {
		'required_vars': required_coord_vars
	},
}

iterable_default_layout = []

# Generate default layout and values
def convert_to_snake_case(name):
	return name.lower().replace(' ', '_')

for key, layout in default_layout.items():
	classes=""
	if layout['type'] == 'number':
		classes = "base-input settings-input"

	html_id = convert_to_snake_case(key)
	layout['html_id'] = html_id
	idl = {
		"name": key,
		"html_id": html_id,
		"value": layout['value'],
		"units": layout['units'],
		"type": layout['type'],
		"classes": classes
	}
	iterable_default_layout.append(idl)

for key in default_profile_layouts:
	required_vars = default_profile_layouts[key]['required_vars']

	layout = {}
	for required_var in required_vars:
		layout[required_var] = default_layout[required_var]

	default_profile_layouts[key]['layout'] = layout

extension_uses_profile = {
	'gbr': 'path_cnc_profile',
	'drl': 'coord_cnc_profile',
	'txt': 'coord_cnc_profile'
}