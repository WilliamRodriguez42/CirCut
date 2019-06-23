var svg_controller;

function svg_viewer_control_tab_resize() {
	var parent = $("#svg_viewer_div");
	var tab = $("#svg_viewer_control_tab");
	var x_pos = (parent.width() - tab.width()) / 2;

	tab = document.getElementById("svg_viewer_control_tab");
	tab.style.left = x_pos + "px";
	tab.style.visibility = "visible";
}

function load_svg() {
	$.ajax({
		type: 'GET',
		url: 'svg',
		success: function(data) {
			elem = document.getElementById('svg_viewer_div');
			elem.innerHTML = data;

			var svg_element = elem.getElementsByTagName('svg')[0]
			svg_element.id = "svg_element"
			svg_element.style = "width: 100%; height: 100%; will-change: transform;"

			svg_controller = svgPanZoom('#svg_element', {
        zoomEnabled: true,
			  panEnabled: true,
			  controlIconsEnabled: false,
      });
			svg_controller.center();
		  svg_controller.fit();

			custom_resize();
		}
	});
}
