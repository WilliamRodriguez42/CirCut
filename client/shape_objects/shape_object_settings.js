function load_shape_object_settings_from_json(settings) {
	console.log(settings);
}

function update_html_for_layout(layout) {
	var values = Object.values(layout);

	// Hide all settings elements
	var elems = document.querySelectorAll("#convert_settings > tbody > *")
	for (var i = 0; i < elems.length; i ++) {
		elems[i].classList.add("removed");
	}

	for (var i = 0; i < values.length; i ++) {
		var setting = values[i];
		var elem = document.querySelector("#"+setting.html_id+"_row");
		elem.classList.remove("removed");
	}
}

function update_html_for_id(id) {
	for (var i = 0; i < active_shape_objects.length; i ++) {
		if (active_shape_objects[i].shape_object_id == id) {
			update_html_for_layout(active_shape_objects[i].layout);
			break;
		}
	}
}

function get_layout_for_id(id) {
	for (var i = 0; i < active_shape_objects.length; i ++) {
		if (active_shape_objects[i].shape_object_id == id) {
			return active_shape_objects[i].layout;
		}
	}
}