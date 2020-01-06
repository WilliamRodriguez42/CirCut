var convert_progress_id = null;
var convert_prev_state = 0;
var convert_curr_state = 0;
var convert_prev_state_text = "";
var convert_curr_state_text = "";
var convert_svg_loaded = false;

function reset_conversion_state_values() {
	convert_prev_state = 0;
	convert_curr_state = 0;
	convert_prev_state_text = "";
	convert_curr_state_text = "";
	convert_svg_loaded = false;
}

function convert() {
	// Send form to server
	var shape_object_id = '';
	if (previously_selected_element != null) {
		shape_object_id = previously_selected_element.id;
	} else {
		console_display_message({
			type: "error",
			message: "Could not convert: no files have been uploaded / selected"
		});
		return;
	}
	layout = get_layout_for_id(previously_selected_element.id);
	reset_conversion_state_values();

	var contours = $.ajax({
		type: "POST",
		url: "/convert",
		data: JSON.stringify({
			shape_object_id: shape_object_id,
			layout: layout
		}),
		contentType: "text/plain",
		success: function() {
			load_gcodes();
		},
		error: function(err) {
		}
	});
}

function progress_move_frame() {
	var progress_fill_elem = document.getElementById("convert_progress_bar");

	progress_bar_pos += (progress_stop_pos - progress_bar_pos) / 10;
	progress_fill_elem.style.width = progress_bar_pos + '%';
}

function progress_move(start, stop, status) {
	if (progress_move_id !== null) clearInterval(progress_move_id);

	progress_stop_pos = stop;
	progress_move_id = setInterval(progress_move_frame, 10);

	var progress_text_elem = document.getElementById("convert_progress_text");
	progress_text_elem.textContent = status;
}

var progress_stop_pos = 0;
var progress_move_id = null;
var progress_bar_pos = 0;
