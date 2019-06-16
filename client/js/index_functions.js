var container;
var camera, scene, renderer, loader, g_object, d_object;
var controls;

function load_contour(gcode) {
	scene.remove(g_object);
	g_object = loader.parse(gcode);
	scene.add(g_object);
	animate();
}

function load_drill(gcode) {
	scene.remove(d_object);
	d_object = loader.parse(gcode);
	scene.add(d_object);
	animate();
}

function animate() {
	renderer.render( scene, camera );

	requestAnimationFrame( animate );
}

function load_gcodes() {
	var contours = $.ajax({
		type: "GET",
		url: "contours",
		success: function() {
			load_contour(contours.responseText);
		}
	});

	var drills = $.ajax({
		type: "GET",
		url: "drills",
		success: function() {
			load_drill(drills.responseText);
		}
	});
}

function init() {

	container = document.createElement( 'div' );
	document.getElementById("viewer-div").appendChild( container );

	camera = new THREE.PerspectiveCamera( 60, window.innerWidth / window.innerHeight, 0.1, 10000 );
	camera.position.set( 0, 100, 0 );

	controls = new THREE.OrbitControls( camera );
	controls.enabled = false;

	scene = new THREE.Scene();
	loader = new THREE.GCodeLoader();



	renderer = new THREE.WebGLRenderer();
	renderer.setPixelRatio( window.devicePixelRatio );
	renderer.setSize( window.innerWidth, window.innerHeight );
	container.appendChild( renderer.domElement );

	window.addEventListener( 'resize', resize, false );

	load_gcodes();
}

function resize(width, height) {
	var height = $('#top_panel').height();
	var width = $("#left_panel1").width() - $('#left_panel2').width();

	camera.aspect = width / height;
	camera.updateProjectionMatrix();

	renderer.setSize( width, height );
}

function enable_controls() {
	if (controls) controls.enabled = true;
	mouseOver = 1;
}

function disable_controls() {
	if (!mouseDown) {
		if (controls) controls.enabled = false;
	}
	mouseOver = 0;
}

var mouseDown = 0;
var mouseOver = 0;

Dropzone.options.gerberDropzone = {
	acceptedFiles: ".gbr",
	accept: function(file, done) {
		if (this.files.length > 1) {
			this.removeFile(this.files[0])
		}
		done();
	}
}

Dropzone.options.excellonDropzone = {
	acceptedFiles: ".drl",
	accept: function(file, done) {
		if (this.files.length > 1) {
			this.removeFile(this.files[0])
		}
		done();
	}
}

function convert() {
	// Send form to server
	convert_info = {
		rapid_feedrate: $('#rapid_feedrate_value').value,
		pass_feedrate: $('#pass_feedrate_value').value,
		plunge_feedrate: $('#plunge_feedrate_value').value,
		plunge_depth: $('#plunge_depth_value').value,
		safe_height: $('#safe_height_value').value,
		contour_spindle: $('#contour_spindle_value').value,
		drill_spindle: $('#drill_spindle_value').value
	};

	var contours = $.ajax({
		type: "POST",
		url: "convert",
		data: convert_info,
		complete: function(res) {
			if (res.status == 200) {
				load_gcodes();
			}
		}
	});

	var id = setInterval(frame, 500);
	var prev = 0;
	var curr = 0;
	var prev_text = ""
	var curr_text = ""
	var svg_loaded = false
	function frame() {
		$.ajax({
			type: "GET",
			url: "convert_progress",
			success: function(data) {
				curr_text = data.text;
				if (prev_text != curr_text) {
					curr = 100 / data.of * data.step;
					move(prev, curr, curr_text);
					prev = curr;

					prev_text = curr_text;

					if (data.load_svg && !svg_loaded) {
						load_svg();
						svg_loaded = true;
					}
				}

				if (curr >= 100) {
					clearInterval(id);
				}
			},
			error: function() {
				clearInterval(id);
			}
		})
	}
}

function svg_viewer_control_tab_resize() {
	var parent = $("#svg-viewer");
	var tab = $("#svg_viewer_control_tab");
	var x_pos = (parent.width() - tab.width()) / 2;

	tab = document.getElementById("svg_viewer_control_tab");
	tab.style.left = x_pos + "px";
	tab.style.visibility = "visible";
}

function custom_resize() {
	svg_controller.resize();
	svg_viewer_control_tab_resize();
}
