function update_layout_from_html(shape_object_id, layout) {
	var values = Object.values(layout);

	for (var i = 0; i < values.length; i ++) {
		var setting = values[i];
		var elem = document.querySelector("#"+setting.html_id);
		if (setting.type == "checkbox") {
			setting.value = elem.checked.toString();
		} else {
			setting.value = elem.value;
		}
	}
}

function update_layout_from_html_for_id(shape_object_id) {
	// Get current settings for this id
	for (var i = 0; i < active_shape_objects.length; i ++) {
		if (active_shape_objects[i].shape_object_id == shape_object_id) {
			update_layout_from_html(shape_object_id, active_shape_objects[i].layout);
			break;
		}
	}
}

function sync_all_settings_with_server() {
	for (var i = 0; i < active_shape_objects.length; i ++) {
		$.ajax({
			type: "POST",
			url: "/update_shape_object_layout",
			async: false,
			data: JSON.stringify({
				shape_object_id: active_shape_objects[i].shape_object_id,
				layout: active_shape_objects[i].layout
			}),
			contentType: "text/plain"
		});
	}
}

function update_html_from_layout(layout) {
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

		var elem = elem.querySelector('input')
		if (setting.type == "checkbox") {
			elem.checked = setting.value.toString() == 'true';
		} else {
			elem.value = setting.value;
		}
	}
}

function update_html_for_id(id) {
	for (var i = 0; i < active_shape_objects.length; i ++) {
		if (active_shape_objects[i].shape_object_id == id) {
			update_html_from_layout(active_shape_objects[i].layout);
			break;
		}
	}
}