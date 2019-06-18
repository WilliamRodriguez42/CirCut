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
