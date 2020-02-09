
window.onload = function() {
	disable_load_settings_button();

	init();
	animate();
	start_server_polling();

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

	$(document).on("wheel", "input[type=number]", function (e) {
		$(this).blur();
	});

	this.initialize_svg_viewer();

	this.get_uploaded_files();
}

window.onbeforeunload = function () {

	if (previously_selected_element != null) {
		update_layout_from_html_for_id(previously_selected_element.id);
	}
	sync_all_settings_with_server();
}
