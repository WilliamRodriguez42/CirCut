var container;
var camera, scene, renderer, loader, g_object, d_object;
var controls;
var mouseDown = 0;
var mouseOver = 0;

// function load_contour(gcode) {
// 	scene.remove(g_object);
// 	g_object = loader.parse(gcode);
// 	scene.add(g_object);
// 	animate();
// }

// function load_drill(gcode) {
// 	scene.remove(d_object);
// 	d_object = loader.parse(gcode);
// 	scene.add(d_object);
// 	animate();
// }

function create_threejs_gcode_object(shape_object, gcode_content) {
	shape_object.gcode_object = loader.parse(gcode_content);
	scene.add(shape_object.gcode_object);
	animate();
}

function update_threejs_gcode_object(shape_object, gcode_content) {
	scene.remove(shape_object.gcode_object);
	shape_object.gcode_object = loader.parse(gcode_content);
	scene.add(shape_object.gcode_object);
	animate();
}

function remove_threejs_gcode_object(shape_object) {
	scene.remove(shape_object.gcode_object);
	animate();
}

function animate() {
	renderer.render( scene, camera );
	requestAnimationFrame( animate );
}

// function copy_position_scale_properties() {
// 	d_object.scale.set(
// 		g_object.scaling_factor,
// 		g_object.scaling_factor,
// 		g_object.scaling_factor);

// 	d_object.position.set(
// 		-g_object.center.x,
// 		-g_object.center.y,
// 		-g_object.center.z);
// }

// function load_gcodes() {
// 	var contours_loaded = false;
// 	var drills_loaded = false;
// 	var in_crit = false;

// 	var contours = $.ajax({
// 		type: "GET",
// 		url: "contours",
// 		success: function() {
// 			while (in_crit);
// 			in_crit = true;
// 			load_contour(contours.responseText);

// 			g_object.scale.set(
// 				g_object.scaling_factor,
// 				g_object.scaling_factor,
// 				g_object.scaling_factor);

// 			g_object.position.set(
// 				-g_object.center.x,
// 				-g_object.center.y,
// 				-g_object.center.z);

// 			if (drills_loaded) {
// 				copy_position_scale_properties();
// 			}

// 			contours_loaded = true;
// 			in_crit = false;
// 		}
// 	});

// 	var drills = $.ajax({
// 		type: "GET",
// 		url: "drills",
// 		success: function() {
// 			while (in_crit);
// 			in_crit = true;

// 			load_drill(drills.responseText);

// 			if (contours_loaded) {
// 				copy_position_scale_properties();
// 			}

// 			drills_loaded = true;
// 			in_crit = false;
// 		}
// 	});
// }

function init() {

	container = document.createElement( 'div' );
	document.getElementById("threejs_viewer_panel").appendChild( container );
	container.onmouseenter = function() { enable_controls(); }
	container.onmouseleave = function() { disable_controls(); }

	camera = new THREE.PerspectiveCamera( 60, window.innerWidth / window.innerHeight, 0.1, 10000 );
	camera.position.set( 0, 75, 0 );

	controls = new THREE.OrbitControls( camera );
	controls.enabled = false;

	scene = new THREE.Scene();
	scene.background = new THREE.Color( 0xeeeeee );

	loader = new THREE.GCodeLoader();

	renderer = new THREE.WebGLRenderer();
	renderer.setPixelRatio( window.devicePixelRatio );
	renderer.setSize( window.innerWidth, window.innerHeight );
	container.appendChild( renderer.domElement );
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

function threejs_viewer_control_tab_resize() {
	var parent = $("#threejs_viewer_panel");
	var tab = $("#threejs_viewer_control_tab");
	var x_pos = (parent.width() - tab.width()) / 2;

	tab = document.getElementById("threejs_viewer_control_tab");
	tab.style.left = x_pos + "px";
	tab.style.visibility = "visible";
}

function threejs_resize() {
	var height = $('#viewers_panel').height();
	var width = $("#main_panel").width() - $('#svg_viewer_panel').width();

	camera.aspect = width / height;
	camera.updateProjectionMatrix();

	renderer.setSize( width-18, height );
}
