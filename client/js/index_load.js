init();
animate();
load_svg();
start_server_polling();

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
