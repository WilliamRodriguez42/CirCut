var svg_controller;

function svg_viewer_control_tab_resize() {
	var parent = $("#svg_viewer_div");
	var tab = $("#svg_viewer_control_tab");
	var x_pos = (parent.width() - tab.width()) / 2;

	tab = document.getElementById("svg_viewer_control_tab");
	tab.style.left = x_pos + "px";
	tab.style.visibility = "visible";
}
