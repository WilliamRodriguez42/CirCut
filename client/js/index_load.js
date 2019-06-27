
window.onload = function() {
	init();
	animate();
	load_svg();
	start_server_polling();
	restore_from_auto_save();
	start_auto_save();

	$(".panel-top").resizable({
		handleSelector: ".splitter-horizontal",
		resizeWidth: false
	});

	$("#main_panel").resizable({
		handleSelector: "#main_vertical_splitter",
		resizeHeight: false
	});

	$("#svg_viewer_panel").resizable({
		handleSelector: "#view_panels_splitter",
		resizeHeight: false
	});

	$(window).resize(function() {
		custom_resize();
	});

	var settings_elems = document.getElementsByClassName("settings-input");

	for (var i = 0; i < settings_elems.length; i ++) {
		settings_elems[i].addEventListener(
			'input',
			function() {
				var profile_name = $("#settings_profile_name").val();
				if (profile_name !== "" && profile_name !== ".cnc_profile") {
					check_if_profile_name_exists();
					enable_save_settings_button();
				}
			}
		);
	}

	var collapse = $(".base-accordion");
	collapse[0].click();
	collapse[3].click();
}

window.onbeforeunload = function () {
	if (document.getElementById("save_settings_button").disabled === false) {
		return "The changes you made may not be saved";
	}
}
