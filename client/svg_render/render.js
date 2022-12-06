function inject_svg_for_id(id) {
	$.ajax({
		type: 'POST',
		url: '/get_svg_for_id',
		data: { shape_object_id: id },
		success: function(data) {
			var elem = document.querySelector('.svg-pan-zoom_viewport');
			var html = '<g id="' + id + '_svg"> \
			<g id="' + id + '_thumbnail">'
			+ data['thumbnail'] +
			'</g> \
			<g id="' + id + '_preview">'
			+ data['preview'] +
			'</g> \
			</g>';
			elem.insertAdjacentHTML('beforeend', html);

			// svg_controller.center();
			// svg_controller.fit();

			custom_resize();
		}
	});
}

function inject_gcode_for_id(shape_object_id) {
	var contours = $.ajax({
		type: "POST",
		url: "/get_gcode_for_id",
		data: { shape_object_id: shape_object_id },
		success: function(gcode_content) {
			var shape_object = get_shape_object_from_shape_object_id(shape_object_id);
			create_threejs_gcode_object(shape_object, gcode_content);
		}
	});
}

function update_gcode_for_id(shape_object_id) {
	var contours = $.ajax({
		type: "POST",
		url: "/get_gcode_for_id",
		data: { shape_object_id: shape_object_id },
		success: function(gcode_content) {
			var shape_object = get_shape_object_from_shape_object_id(shape_object_id);
			update_threejs_gcode_object(shape_object, gcode_content);
			// download_gcode("current_gcode.gcode", gcode_content);
		}
	});
}

function download_gcode(filename, text) {
	var element = document.createElement('a');
	element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
	element.setAttribute('download', filename);
  
	element.style.display = 'none';
	document.body.appendChild(element);
  
	element.click();
  
	document.body.removeChild(element);
  }

function update_all_gcodes() {
	for (var i = 0; i < active_shape_objects.length; i ++) {
		update_gcode_for_id(active_shape_objects[i].shape_object_id);
	}
}

function remove_gcode_for_id(shape_object_id) {
	var shape_object = get_shape_object_from_shape_object_id(shape_object_id);
	remove_threejs_gcode_object(shape_object);
}

function remove_svg_for_id(id) {
	var elem = document.getElementById(id + '_svg');
	elem.parentNode.removeChild(elem);
}

function position_svg_for_id(id, other_element_id) {
	var other_element = document.getElementById(other_element_id + '_svg');
	var elem = document.getElementById(id + '_svg');

	elem.parentElement.removeChild(elem);
	other_element.insertAdjacentElement('afterend', elem);
}

function update_thumbnail_svg_for_id(id) {
	$.ajax({
		type: 'POST',
		url: '/get_thumbnail_svg_for_id',
		data: { shape_object_id: id },
		success: function(data) {
			var elem = document.querySelector('#' + id + '_thumbnail');
			elem.innerHTML = data;

			// svg_controller.center();
			// svg_controller.fit();

			custom_resize();
		}
	});
}

function update_preview_svg_for_id(id) {
	$.ajax({
		type: 'POST',
		url: '/get_preview_svg_for_id',
		data: { shape_object_id: id },
		success: function(data) {
			var elem = document.querySelector('#' + id + '_preview');
			elem.innerHTML = data;

			// svg_controller.center();
			// svg_controller.fit();

			custom_resize();
		}
	});
}

function initialize_svg_viewer() {
	svg_controller = svgPanZoom('#svg_element', {
		zoomEnabled: true,
		panEnabled: true,
		controlIconsEnabled: false,
		zoomScaleSensitivity: 0.8,
		minZoom: 0,
		maxZoom: 100,
	});

	// svg_controller.center();
	// svg_controller.fit();

	custom_resize();
}