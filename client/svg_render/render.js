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

			svg_controller.center();
			svg_controller.fit();

			custom_resize();
		}
	});
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

			svg_controller.center();
			svg_controller.fit();

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

			svg_controller.center();
			svg_controller.fit();

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

	svg_controller.center();
	svg_controller.fit();

	custom_resize();
}