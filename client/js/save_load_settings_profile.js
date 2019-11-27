
function load_and_validate_convert_settings(convert_settings) {
	$('#rapid_feedrate').val(convert_settings.rapid_feedrate);
	$('#pass_feedrate').val(convert_settings.pass_feedrate);
	$('#plunge_feedrate').val(convert_settings.plunge_feedrate);
	$('#plunge_depth').val(convert_settings.plunge_depth);
	$('#safe_height').val(convert_settings.safe_height);
	$('#contour_spindle').val(convert_settings.contour_spindle);
	$('#drill_spindle').val(convert_settings.drill_spindle);
	$('#contour_distance').val(convert_settings.contour_distance);
	$('#contour_count').val(convert_settings.contour_count);
	$('#contour_step').val(convert_settings.contour_step);
	$("#resolution").val(convert_settings.resolution);
	$("#buffer_resolution").val(convert_settings.buffer_resolution);
	$("#calculate_origin").prop("checked", convert_settings.calculate_origin);
	$("#flip_x_axis").prop("checked", convert_settings.flip_x_axis);
	$("#x_offset").val(convert_settings.x_offset);
	$("#y_offset").val(convert_settings.y_offset);
	$("#nc_drill_x_offset").val(convert_settings.nc_drill_x_offset);
	$("#nc_drill_y_offset").val(convert_settings.nc_drill_y_offset);
	$("#connection_port").val(convert_settings.connection_port);

	get_and_validate_convert_settings();
}

function load_and_validate_settings_profile() {
	var selected_profile = $("#settings_profile_name").val();
	if (selected_profile.endsWith(".cnc_profile") === false) {
		selected_profile += ".cnc_profile";
	}

	$.ajax({
		type: 'GET',
		url: '/load-settings-profile/' + selected_profile,
		success: function(data) {
			data = JSON.parse(data);
			last_settings_profile = data;
			load_and_validate_convert_settings(data.convert_settings);
		}
	});

}

function get_settings_profile_name() {
	settings_profile_name = $("#settings_profile_name").val();

	if (settings_profile_name.endsWith(".cnc_profile") === false) {
		settings_profile_name += ".cnc_profile";
	}

	return settings_profile_name;
}

function get_convert_settings() {
	var convert_settings = {
		rapid_feedrate: +$('#rapid_feedrate').val(),
		pass_feedrate: +$('#pass_feedrate').val(),
		plunge_feedrate: +$('#plunge_feedrate').val(),
		plunge_depth: +$('#plunge_depth').val(),
		safe_height: +$('#safe_height').val(),
		contour_spindle: +$('#contour_spindle').val(),
		drill_spindle: +$('#drill_spindle').val(),
		contour_distance: +$('#contour_distance').val(),
		contour_count: +$('#contour_count').val(),
		contour_step: +$('#contour_step').val(),
		resolution: +$("#resolution").val(),
		buffer_resolution: +$("#buffer_resolution").val(),
		calculate_origin: $("#calculate_origin").is(":checked"),
		flip_x_axis: $("#flip_x_axis").is(":checked"),
		x_offset: +$("#x_offset").val(),
		y_offset: +$("#y_offset").val(),
		nc_drill_x_offset: +$("#nc_drill_x_offset").val(),
		nc_drill_y_offset: +$("#nc_drill_y_offset").val(),
		connection_port: $("#connection_port").val()
	};

	return convert_settings;
}

function get_and_validate_convert_settings() {
	var convert_settings = get_convert_settings();

	// Validate inputs (All values are good for contour_distance)
	var error_messages = "\n";
	if (!(convert_settings.rapid_feedrate > 0)) {
		error_messages += "Invalid rapid feedrate: must be a value greater than 0\n";
		invalid('rapid_feedrate');
	} else {
		valid('rapid_feedrate');
	}
	if (!(convert_settings.pass_feedrate > 0)) {
		error_messages += "Invalid pass feedrate: must be a value greater than 0\n";
		invalid('pass_feedrate');
	} else {
		valid('pass_feedrate');
	}
	if (!(convert_settings.plunge_feedrate > 0)) {
		error_messages += "Invalid plunge feedrate: must be a value greater than 0\n";
		invalid('plunge_feedrate');
	} else {
		valid('plunge_feedrate');
	}
	if (!(convert_settings.plunge_depth < 0)) {
		error_messages += "Invalid plunge depth: must be a value less than 0\n";
		invalid('plunge_depth');
	} else {
		valid('plunge_depth');
	}
	if (!(convert_settings.safe_height > 0)) {
		error_messages += "Invalid safe height: must be a value greater than or equal to 0\n";
		invalid('safe_height');
	} else {
		valid('safe_height');
	}
	if (!(convert_settings.contour_spindle > 0 && convert_settings.contour_spindle < 1024)) {
		error_messages += "Invalid contour spindle speed: must be a value greater than 0 and less than 1024\n";
		invalid('contour_spindle');
	} else {
		valid('contour_spindle');
	}
	if (!(convert_settings.drill_spindle > 0 && convert_settings.drill_spindle < 1024)) {
		error_messages += "Invalid drill spindle speed: must be a value greater than 0 and less than 1024\n";
		invalid('drill_spindle');
	} else {
		valid('drill_spindle');
	}
	if (!(convert_settings.contour_distance >= 0)) {
		error_messages += "Invalid contour distance: must be a value greater than or equal to 0\n";
		invalid('contour_distance');
	} else {
		valid('contour_distance');
	}
	if (!(convert_settings.contour_count >= 0 && Number.isInteger(convert_settings.contour_count))) {
		error_messages += "Invalid contour count: must be an integer greater than or equal to 0\n";
		invalid('contour_count');
	} else {
		valid('contour_count');
	}
	if (!(convert_settings.contour_step > 0)) {
		error_messages += "Invalid contour step: must be a value greater than 0\n";
		invalid('contour_step');
	} else {
		valid('contour_step');
	}
	if (!(convert_settings.resolution >= 3 && convert_settings.resolution <= 60 && Number.isInteger(convert_settings.resolution))) {
		error_messages += "Invalid resolution: must be an integer greater than or equal to 3 and less than or equal to 60\n";
		invalid('resolution');
	} else {
		valid('resolution');
	}
	if (!(convert_settings.buffer_resolution > 0 && convert_settings.buffer_resolution <= 20 && Number.isInteger(convert_settings.buffer_resolution))) {
		error_messages += "Invalid buffer resolution: must be an integer greater than 0 and less than or equal to 20\n";
		invalid('buffer_resolution');
	} else {
		valid('buffer_resolution');
	}
	valid('calculate_origin');
	valid('flip_x_axis');
	valid('x_offset');
	valid('y_offset');
	valid('nc_drill_x_offset');
	valid('nc_drill_y_offset');
	valid('connection_port');

	// Warn the user if there were any errors
	if (error_messages !== "\n") {
		error_messages = error_messages.substring(0, error_messages.length-1); // Truncate the last \n
		console_display_message({
			type: "error",
			message: error_messages
		});

		return null;
	}

	return convert_settings;
}

function get_settings_profile() {
	settings_profile_name = get_settings_profile_name();
	convert_settings = get_convert_settings();

	settings_profile = {
		name: settings_profile_name,
		convert_settings: convert_settings,
	}

	return settings_profile;
}

function get_and_validate_settings_profile() {
	settings_profile_name = get_settings_profile_name();

	convert_settings = get_and_validate_convert_settings();
	if (convert_settings === null) return null;

	settings_profile = {
		name: settings_profile_name,
		convert_settings: convert_settings,
	}

	return settings_profile;
}

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

function change_to_override_profile() {
	var save_button = document.getElementById("save_settings_button");
	save_button.textContent = "Override Profile";
	if (save_button.className.includes("evil-button") === false) {
		save_button.className += " evil-button";
	}
}

function change_to_save_profile() {
	var save_button = document.getElementById("save_settings_button");
	save_button.textContent = "Save Profile";

	while (save_button.className.includes("evil-button")) {
		save_button.className = save_button.className.replace(" evil-button", "");
	}
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

function save_profile() {
	data = get_and_validate_settings_profile();
	if (data === null) return;

	last_settings_profile = data;

	$.ajax({
		type: "POST",
		url: "/save-settings-profile",
		data: JSON.stringify(data),
		contentType: "text/plain",
		success: function() {
			console_display_message({
				type: "info",
				message: "Settings profile saved successfully"
			});
		},
		error: function() {
			console_display_message({
				type: "error",
				message: "Settings profile could not be saved"
			});
		}
	});
}

function disable_load_settings_button() {
	document.getElementById("load_settings_button").disabled = true;
}

function enable_load_settings_button() {
	document.getElementById("load_settings_button").disabled = false;
}

var last_settings_profile = null;
