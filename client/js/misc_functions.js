function sanitize_string(str){
    str = str.replace(/[^a-z0-9áéíóúñü \.,_-]/gim,"");
    return str.trim();
}

function invalid(elem_id) {
	$("#" + elem_id).css('background', 'var(--invalid-color)');
}

function valid(elem_id) {
	$("#" + elem_id).css('background', '');
}

function custom_resize() {
	svg_controller.resize();
	threejs_resize();

	svg_viewer_control_tab_resize();
	threejs_viewer_control_tab_resize();
}
