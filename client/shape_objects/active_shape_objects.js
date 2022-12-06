function add_shape_object_to_list(shape_object_id, layout) {
	so = {
		shape_object_id: shape_object_id,
		layout: layout,
		gcode_object: null,
	}
	active_shape_objects.push(so);
	update_html_from_layout(layout);
}

function remove_shape_object_from_list(shape_object_id) {
	for (var i = 0; i < active_shape_objects.length; i ++) {
		if (active_shape_objects[i].shape_object_id == shape_object_id) {
			active_shape_objects.splice(i, 1);
			$.ajax({
				type: "POST",
				url: "/delete_shape_object",
				data: { shape_object_id: shape_object_id }
			});
			break;
		}
	}
}

function shape_object_response(result) {
	var font_size = 1/result.name.length * 300;
	if (font_size > 17.5) {
		font_size = 17.5;
	} else if (font_size < 6) {
		font_size = 6;
	}

	var shape_object_id = "shape_object_" + result.shape_object_id;

	var html = ' \
	<li id="' + shape_object_id + '" class="draggable_list_element" draggable="true"> \
		<header style="font-size:' + font_size + 'px; float: left; width: 80%">' + result.name + '</header> \
		<header style="float: left; text-align: left; width: 10%">' + result.shape_object_id + '</header> \
		<img src="images/delete_shape_object.png" onclick="delete_shape_object(this);"></img> \
	</li>';
	var parent = document.getElementById("draggable_list");
	parent.insertAdjacentHTML('afterbegin', html);
	var elem = document.querySelector('#'+shape_object_id);
	addDnDHandlers(elem);
	select_element(elem);
	inject_svg_for_id(shape_object_id);

	// Append a new shape object
	add_shape_object_to_list(shape_object_id, result.layout);
	inject_gcode_for_id(shape_object_id);
}

function get_uploaded_files() {
	$.ajax({
		type: "GET",
		url: "/get_uploaded_files",
		success: function(data) {
			for (var i = 0; i < data.length; i ++) {
				shape_object_response(data[i]);
			}
		}
	});
}

function get_layout_for_shape_object_id(shape_object_id) {
	for (var i = 0; i < active_shape_objects.length; i ++) {
		if (active_shape_objects[i].shape_object_id == shape_object_id) {
			return active_shape_objects[i].layout;
		}
	}
	return null;
}

function get_shape_object_from_shape_object_id(shape_object_id) {
	for (var i = 0; i < active_shape_objects.length; i ++) {
		if (active_shape_objects[i].shape_object_id == shape_object_id) {
			return active_shape_objects[i];
		}
	}
}

active_shape_objects = [];