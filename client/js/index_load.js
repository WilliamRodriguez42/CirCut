init();
animate();
load_svg();
start_server_polling();

window.onload = function() {
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
				enable_load_settings_button();
				enable_save_settings_button();
			}
		);
	}

}

window.onbeforeunload = function () {
	if (document.getElementById("save_settings_button").disabled === false) {
		return "The changes you made may not be saved";
	}
}
