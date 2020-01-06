function add_shape_object_to_list(shape_object_id, layout) {
	so = {
		shape_object_id: shape_object_id,
		layout: layout,
	}
	active_shape_objects.push(so);
	update_html_for_layout(layout);
}

active_shape_objects = [];