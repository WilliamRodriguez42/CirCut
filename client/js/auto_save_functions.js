function start_auto_save() {
	auto_save_id = setInterval(auto_save, 10000); // Auto save every 10 seconds
}

function auto_save() {
	var settings_profile = get_settings_profile();
	if (settings_profile === null) return "Cannot autosave, values invalid";

	$.ajax({
		type: 'POST',
		url: '/auto_save',
		data: JSON.stringify(settings_profile),
		contentType: "text/plain",
		success: function() {
			console.log("Successfully autosaved data");
		}
	});
}

function restore_from_auto_save() {
	$.ajax({
		type: 'GET',
		url: '/restore_from_auto_save',
		success: function(data) {
			var data = JSON.parse(data);
			load_and_validate_convert_settings(data.convert_settings);

			if (data.name !== ".cnc_profile") $("#settings_profile_name").val(data.name);

			check_if_profile_name_exists();

			console.log("Successfully restored values from auto save");
		},
		error: function() {
			console.log("Could not load from auto save, using default values instead");
		}
	});
}

var auto_save_id = null;
