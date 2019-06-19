init();
animate();
load_svg();
check_for_conversion_on_start();

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
