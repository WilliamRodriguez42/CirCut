function add_shape_object_to_list(shape_object_id, layout) {
	so = {
		shape_object_id: shape_object_id,
		layout: layout,
	}
	active_shape_objects.push(so);
	update_html_for_layout(layout);
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
		<header style="float: right; text-align: right; width: 20%">' + result.shape_object_id + '</header>\
	</li>';
	var parent = document.getElementById("draggable_list");
	parent.insertAdjacentHTML('afterbegin', html)
	var elem = document.querySelector('#'+shape_object_id);
	addDnDHandlers(elem);
	select_element(elem);
	inject_thumbnail_svg_for_id(shape_object_id)

	// var settings_table = document.getElementById("convert_settings");
	// settings_table.innerHTML = '';
	// settings_table.insertAdjacentHTML('afterbegin', result.html);

	// Append a new shape object
	add_shape_object_to_list(shape_object_id, result.layout)
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
active_shape_objects = [];