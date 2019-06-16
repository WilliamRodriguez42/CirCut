init();
animate();
load_svg();

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

function move(start, stop, status) {
	var elem = document.getElementById("convert_progress_bar");
	var text_elem = document.getElementById("convert_progress_text");
	var width = start;
	var id = setInterval(frame, 10);
	function frame() {
		if (width >= stop) {
			clearInterval(id);
			text_elem.innerHTML = "Progress: " + status
		} else {
			width += (width - start) * (stop - width) / Math.pow((stop - start) / 2, 2) * 2 + 0.1;
			elem.style.width = width + '%';
			text_elem.innerHTML = "Progress: " + status
		}
	}
}

function load_svg() {
	$.ajax({
		type: 'GET',
		url: 'svg',
		success: function(data) {
			elem = document.getElementById('svg-viewer');
			elem.innerHTML = data;

			var svg_element = elem.getElementsByTagName('svg')[0]
			svg_element.id = "svg_element"
			svg_element.style = "width: 100%; height: 100%"

			window.zoomTiger = svgPanZoom('#svg_element', {
	          zoomEnabled: true,
			  panEnabled: true,
			  controlIconsEnabled: false,
			  fit: true,
			  center: true,
	          // viewportSelector: document.getElementById('demo-tiger').querySelector('#g4') // this option will make library to misbehave. Viewport should have no transform attribute
	        });
		}
	});
}
