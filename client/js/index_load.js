
window.onload = function() {
	init();
	animate();
	load_svg();
	start_server_polling();
	restore_from_auto_save();
	start_auto_save();

	$(".panel-top").resizable({
		handleSelector: "#main_horizontal_splitter",
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

	var collapse = $(".base-accordion");
	collapse[0].click();
	collapse[3].click();
}

window.onbeforeunload = function () {
	if (document.getElementById("save_settings_button").disabled === false) {
		return "The changes you made may not be saved";
	}
}
