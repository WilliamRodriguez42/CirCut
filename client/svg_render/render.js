function inject_thumbnail_svg_for_id(id) {
	$.ajax({
		type: 'POST',
		url: '/get_thumbnail_svg_for_id',
		data: { shape_object_id: id },
		success: function(data) {
			var elem = document.querySelector('.svg-pan-zoom_viewport');
			var html = '<g id="' + id + '_svg"> \
			<g id="' + id + '_thumbnail">'
			+ data +
			'</g> \
			<g id="' + id + '_preview"> \
			</g> \
			</g>';
			elem.insertAdjacentHTML('beforeend', html);

			svg_controller.center();
			svg_controller.fit();

			custom_resize();
		}
	});
}

function position_svg_for_id(id, other_element_id) {
	var other_element = document.getElementById(other_element_id + '_svg');
	var elem = document.getElementById(id + '_svg');

	console.log(id, other_element_id);

	elem.parentElement.removeChild(elem);
	other_element.insertAdjacentElement('afterend', elem);
}

function update_thumbnail_svg_for_id(id) {
	console.log('HI');
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