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
	document.getElementById("threejs_viewer_panel").appendChild( container );

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
	var height = $('#viewers_panel').height();
	var width = $("#main_panel").width() - $('#svg_viewer_panel').width();

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

function invalid(elem_id) {
	$("#" + elem_id).css('background', 'var(--invalid-color)');
}

function valid(elem_id) {
	$("#" + elem_id).css('background', '');
}

function convert() {
	// Send form to server
	convert_info = {
		rapid_feedrate: +$('#rapid_feedrate').val(),
		pass_feedrate: +$('#pass_feedrate').val(),
		plunge_feedrate: +$('#plunge_feedrate').val(),
		plunge_depth: +$('#plunge_depth').val(),
		safe_height: +$('#safe_height').val(),
		contour_spindle: +$('#contour_spindle').val(),
		drill_spindle: +$('#drill_spindle').val(),
		contour_distance: +$('#contour_distance').val(),
		contour_count: +$('#contour_count').val(),
		contour_step: +$('#contour_step').val(),
		resolution: +$("#resolution").val(),
		buffer_resolution: +$("#buffer_resolution").val()
	};

	// Validate inputs (All values are good for contour_distance)
	error_messages = "";
	if (!(convert_info.rapid_feedrate > 0)) {
		error_messages += "Invalid rapid feedrate: must be a value greater than 0\n";
		invalid('rapid_feedrate');
	} else {
		valid('rapid_feedrate');
	}
	if (!(convert_info.pass_feedrate > 0)) {
		error_messages += "Invalid pass feedrate: must be a value greater than 0\n";
		invalid('pass_feedrate');
	} else {
		valid('pass_feedrate');
	}
	if (!(convert_info.plunge_feedrate > 0)) {
		error_messages += "Invalid plunge feedrate: must be a value greater than 0\n";
		invalid('plunge_feedrate');
	} else {
		valid('plunge_feedrate');
	}
	if (!(convert_info.plunge_depth < 0)) {
		error_messages += "Invalid plunge depth: must be a value less than 0\n";
		invalid('plunge_depth');
	} else {
		valid('plunge_depth');
	}
	if (!(convert_info.safe_height > 0)) {
		error_messages += "Invalid safe height: must be a value greater than or equal to 0\n";
		invalid('safe_height');
	} else {
		valid('safe_height');
	}
	if (!(convert_info.contour_spindle > 0 && convert_info.contour_spindle < 1024)) {
		error_messages += "Invalid contour spindle speed: must be a value greater than 0 and less than 1024\n";
		invalid('contour_spindle');
	} else {
		valid('contour_spindle');
	}
	if (!(convert_info.drill_spindle > 0 && convert_info.drill_spindle < 1024)) {
		error_messages += "Invalid drill spindle speed: must be a value greater than 0 and less than 1024\n";
		invalid('drill_spindle');
	} else {
		valid('drill_spindle');
	}
	if (!(convert_info.contour_distance >= 0)) {
		error_messages += "Invalid contour distance: must be a value greater than or equal to 0\n";
		invalid('contour_distance');
	} else {
		valid('contour_distance');
	}
	if (!(convert_info.contour_count >= 0 && Number.isInteger(convert_info.contour_count))) {
		error_messages += "Invalid contour count: must be an integer greater than or equal to 0\n";
		invalid('contour_count');
	} else {
		valid('contour_count');
	}
	if (!(convert_info.contour_step > 0)) {
		error_messages += "Invalid contour step: must be a value greater than 0\n";
		invalid('contour_step');
	} else {
		valid('contour_step');
	}
	if (!(convert_info.resolution > 0 && Number.isInteger(convert_info.resolution))) {
		error_messages += "Invalid resolution: must be an integer greater than 0\n";
		invalid('resolution');
	} else {
		valid('resolution');
	}
	if (!(convert_info.buffer_resolution > 0 && Number.isInteger(convert_info.buffer_resolution))) {
		error_messages += "Invalid buffer resolution: must be an integer greater than 0\n";
		invalid('buffer_resolution');
	} else {
		valid('buffer_resolution');
	}

	// Warn the user if there were any errors
	if (error_messages !== "") {
		alert(error_messages.substring(0, error_messages.length-1)); // Truncate the last \n
		return;
	}

	var id = setInterval(frame, 500);
	var prev = 0;
	var curr = 0;
	var prev_text = ""
	var curr_text = ""
	var svg_loaded = false

	var contours = $.ajax({
		type: "POST",
		url: "convert",
		data: convert_info,
		success: function() {
			load_gcodes();
		},
		error: function(err) {
			clearInterval(id);
			if (err.status === 409) {
				alert("Conversion already in progress");
			}
		}
	});

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
	var parent = $("#svg_viewer_div");
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
