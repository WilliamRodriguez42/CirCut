init();
animate();

document.body.onmousedown = function() {
	++mouseDown;
	if (!mouseOver) {
		controls.enabled = false;
	}
}
document.body.onmouseup = function() {
	--mouseDown;
	if (!mouseOver) {
		controls.enabled = false;
	}
}

document.body.onmousemove = function() {
	if (!mouseDown && !mouseOver) {
		controls.enabled = false;
	}
}

window.onload = function() {
	var svg_viewer = svgPanZoom('#svg-viewer', {
		zoomEnabled: true,
		panEnabled: true,
		controlIconsEnabled: false
	});
};

$(".panel-top").resizable({
	handleSelector: ".splitter-horizontal",
	resizeWidth: false
});

$("#left_panel1").resizable({
	handleSelector: "#v_splitter1",
	resizeHeight: false
});

$("#left_panel2").resizable({
	handleSelector: "#v_splitter2",
	resizeHeight: false
});
