
// function load_and_validate_convert_settings(convert_settings) {
// 	$('#rapid_feedrate').val(convert_settings.rapid_feedrate);
// 	$('#pass_feedrate').val(convert_settings.pass_feedrate);
// 	$('#plunge_feedrate').val(convert_settings.plunge_feedrate);
// 	$('#plunge_depth').val(convert_settings.plunge_depth);
// 	$('#safe_height').val(convert_settings.safe_height);
// 	$('#contour_spindle').val(convert_settings.contour_spindle);
// 	$('#drill_spindle').val(convert_settings.drill_spindle);
// 	$('#contour_distance').val(convert_settings.contour_distance);
// 	$('#contour_count').val(convert_settings.contour_count);
// 	$('#contour_step').val(convert_settings.contour_step);
// 	$("#resolution").val(convert_settings.resolution);
// 	$("#buffer_resolution").val(convert_settings.buffer_resolution);
// 	$("#calculate_origin").prop("checked", convert_settings.calculate_origin);
// 	$("#flip_x_axis").prop("checked", convert_settings.flip_x_axis);
// 	$("#x_offset").val(convert_settings.x_offset);
// 	$("#y_offset").val(convert_settings.y_offset);
// 	$("#nc_drill_x_offset").val(convert_settings.nc_drill_x_offset);
// 	$("#nc_drill_y_offset").val(convert_settings.nc_drill_y_offset);
// 	$("#connection_port").val(convert_settings.connection_port);

// 	//get_and_validate_convert_settings();
// }

// function load_and_validate_settings_profile() {
// 	var selected_profile = $("#settings_profile_name").val();
// 	if (selected_profile.endsWith(".cnc_profile") === false) {
// 		selected_profile += ".cnc_profile";
// 	}

// 	$.ajax({
// 		type: 'GET',
// 		url: '/load-settings-profile/' + selected_profile,
// 		success: function(data) {
// 			data = JSON.parse(data);
// 			last_settings_profile = data;
// 			load_and_validate_convert_settings(data.convert_settings);
// 		}
// 	});

// }

function load_settings_profile() {
	var selected_profile = $("#settings_profile_name").val();

	$.ajax({
		type: 'POST',
		url: '/load_settings_profile',
		data: { profile_name: selected_profile },
		success: function(data) {
			layout = JSON.parse(data)
			update_html_from_layout(layout);
		}
	});
}

function save_settings_profile() {
	if (previously_selected_element == null) {
		alert("MORON");
		return;
	}

	update_layout_from_html_for_id(previously_selected_element.id);

	var selected_profile = $("#settings_profile_name").val();
	var shape_object_id = previously_selected_element.id;
	var layout = get_layout_for_shape_object_id(shape_object_id);

	$.ajax({
		type: 'POST',
		url: '/save_settings_profile',
		data: JSON.stringify({
			profile_name: selected_profile,
			layout: layout
		}),
		contentType: "text/plain",
		success: function (data) {
			enable_load_settings_button();
		}
	});
}

function get_settings_profile_name() {
	settings_profile_name = $("#settings_profile_name").val();
	return settings_profile_name;
}

// function get_convert_settings() {
// 	var shape_object_id = '';
// 	if (previously_selected_element != null) {
// 		shape_object_id = previously_selected_element.id;
// 	}
// 	var convert_settings = {
// 		shape_object_id: shape_object_id,
// 		rapid_feedrate: +$('#rapid_feedrate').val(),
// 		pass_feedrate: +$('#pass_feedrate').val(),
// 		plunge_feedrate: +$('#plunge_feedrate').val(),
// 		plunge_depth: +$('#plunge_depth').val(),
// 		safe_height: +$('#safe_height').val(),
// 		spindle_speed: +$('#spindle_speed').val(),
// 		contour_distance: +$('#contour_distance').val(),
// 		contour_count: +$('#contour_count').val(),
// 		contour_step: +$('#contour_step').val(),
// 		resolution: +$("#resolution").val(),
// 		buffer_resolution: +$("#buffer_resolution").val(),
// 		calculate_origin: $("#calculate_origin").is(":checked"),
// 		flip_x_axis: $("#flip_x_axis").is(":checked"),
// 		x_offset: +$("#x_offset").val(),
// 		y_offset: +$("#y_offset").val(),
// 		bit_travel_x: +$("#bit_travel_x").val(),
// 		bit_travel_y: +$("#bit_travel_y").val(),
// 		connection_port: $("#connection_port").val()
// 	};

// 	return convert_settings;
// }

// function get_settings_profile() {
// 	settings_profile_name = get_settings_profile_name();
// 	convert_settings = get_convert_settings();

// 	settings_profile = {
// 		name: settings_profile_name,
// 		convert_settings: convert_settings,
// 	}

// 	return settings_profile;
// }

function get_settings_profile_names(callback) {
	$.ajax({
		type: 'GET',
		url: '/get-settings-profile-names',
		success: function(settings_profile_names) {
			settings_profile_names = JSON.parse(settings_profile_names);

			callback(settings_profile_names);
		}
	});
}

function display_settings_profile_names() {
	var callback = function(settings_profile_names) {
		var datalist_elem = document.getElementById("existing_settings_profile_names");
		datalist_elem.innerHTML = "";

		for (var i = 0; i < settings_profile_names.length; i ++) {
			var name = sanitize_string(settings_profile_names[i]);

			datalist_elem.innerHTML += `
			<div class="dropdown-content" onmousedown="dropdown_button_clicked(this)">
				<div style="display: table-cell; padding: 0px 5px; vertical-align: middle;">
					${name}
				</div>
			</div>
			`;
		}

		filter_settings_profile_names();
	};

	get_settings_profile_names(callback);
}

function settings_profile_name_keyup() {
	var search_term = document.getElementById("settings_profile_name").value;

	filter_settings_profile_names();
	check_if_profile_name_exists();
}

function filter_settings_profile_names() {
	var children = document.getElementById("existing_settings_profile_names").children;
	var search_term = document.getElementById("settings_profile_name").value;

	for (var i = 0; i < children.length; i ++) {
		var content = children[i].textContent.trim();
		if (!content.startsWith(search_term)) {
			children[i].style.height = "0px"; // Collapse content that doesn't match
		} else {
			children[i].style.height = "initial"; // Expand elements that do match
		}
	}
}

function dropdown_button_clicked(self) {
	var input_elem = document.getElementById("settings_profile_name");
	input_elem.value = self.textContent.trim();

	check_if_profile_name_exists();
}

function check_if_profile_name_exists() {
	var callback = function(settings_profile_names) {
		var search_term = document.getElementById("settings_profile_name").value;

		for (var i = 0; i < settings_profile_names.length; i ++) {
			if (settings_profile_names[i] === search_term) {
				enable_load_settings_button();
				return;
			}
		}

		disable_load_settings_button();
	}

	get_settings_profile_names(callback);
}

function hide_settings_profile_names() {
	var datalist_elem = document.getElementById("existing_settings_profile_names");
	datalist_elem.innerHTML = "";
}

// function save_profile() {
// 	data = get_settings_profile();
// 	last_settings_profile = data;

// 	$.ajax({
// 		type: "POST",
// 		url: "/save-settings-profile",
// 		data: JSON.stringify(data),
// 		contentType: "text/plain",
// 		success: function() {
// 			console_display_message({
// 				type: "info",
// 				message: "Settings profile saved successfully"
// 			});
// 		},
// 		error: function() {
// 			console_display_message({
// 				type: "error",
// 				message: "Settings profile could not be saved"
// 			});
// 		}
// 	});
// }

function disable_load_settings_button() {
	document.getElementById("load_settings_button").disabled = true;
}

function enable_load_settings_button() {
	document.getElementById("load_settings_button").disabled = false;
}

var last_settings_profile = null;
