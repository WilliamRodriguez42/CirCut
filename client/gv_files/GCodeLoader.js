'use strict';

/**
 * THREE.GCodeLoader is used to load gcode files usually used for 3D printing or CNC applications.
 *
 * Gcode files are composed by commands used by machines to create objects.
 *
 * @class THREE.GCodeLoader
 * @param {Manager} manager Loading manager.
 * @author tentone
 * @author joewalnes
 */
THREE.GCodeLoader = function ( manager ) {

	this.manager = ( manager !== undefined ) ? manager : THREE.DefaultLoadingManager;

	this.splitLayer = false;

};

THREE.GCodeLoader.prototype.load = function ( url, onLoad, onProgress, onError ) {

	var self = this;

	var loader = new THREE.FileLoader( self.manager );
	loader.setPath( self.path );
	loader.load( url, function ( text ) {

		onLoad( self.parse( text ) );

	}, onProgress, onError );

};

THREE.GCodeLoader.prototype.setPath = function ( value ) {

	this.path = value;
	return this;

};

THREE.GCodeLoader.prototype.parse = function ( data ) {

	var state = { x: 0, y: 0, z: 0, e: 0, f: 0, extruding: false, relative: false };
	var layers = [];

	var currentLayer = undefined;

	var pathMaterial = new THREE.LineBasicMaterial( { color: 0xFF0000 } );
	pathMaterial.name = 'path';

	var extrudingMaterial = new THREE.LineBasicMaterial( { color: 0x00FF00 } );
	extrudingMaterial.name = 'extruded';

	function newLayer( line ) {

		currentLayer = { vertex: [], pathVertex: [], z: line.z };
		layers.push( currentLayer );

	}

	//Create lie segment between p1 and p2
	function addSegment( p1, p2 ) {

		if ( currentLayer === undefined ) {

			newLayer( p1 );

		}

		if ( true ) {

			currentLayer.vertex.push( p1.x, p1.y, p1.z );
			currentLayer.vertex.push( p2.x, p2.y, p2.z );

		} else {

			currentLayer.pathVertex.push( p1.x, p1.y, p1.z );
			currentLayer.pathVertex.push( p2.x, p2.y, p2.z );

		}

	}

	function delta( v1, v2 ) {

		return state.relative ? v2 : v2 - v1;

	}

	function absolute( v1, v2 ) {

		return state.relative ? v1 + v2 : v2;

	}

	var lines = data.replace( /;.+/g, '' ).split( '\n' );

	for ( var i = 0; i < lines.length; i ++ ) {

		var tokens = lines[ i ].split( ' ' );
		var cmd = tokens[ 0 ].toUpperCase();

		//Argumments
		var args = {};
		tokens.splice( 1 ).forEach( function ( token ) {

			if ( token[ 0 ] !== undefined ) {

				var key = token[ 0 ].toLowerCase();
				var value = parseFloat( token.substring( 1 ) );
				args[ key ] = value;

			}

		} );

		//Process commands
		//G0/G1 – Linear Movement
		if ( cmd === 'G0' || cmd === 'G1' || cmd === 'G00' || cmd === 'G01' ) {

			var line = {
				x: args.x !== undefined ? absolute( state.x, args.x ) : state.x,
				y: args.y !== undefined ? absolute( state.y, args.y ) : state.y,
				z: args.z !== undefined ? absolute( state.z, args.z ) : state.z,
				e: args.e !== undefined ? absolute( state.e, args.e ) : state.e,
				f: args.f !== undefined ? absolute( state.f, args.f ) : state.f,
			};

			//Layer change detection is or made by watching Z, it's made by watching when we extrude at a new Z position
			if ( delta( state.e, line.e ) > 0 ) {

				line.extruding = delta( state.e, line.e ) > 0;

				if ( currentLayer == undefined || line.z != currentLayer.z ) {

					newLayer( line );

				}

			}

			addSegment( state, line );
			state = line;

		} else if ( cmd === 'G2' || cmd === 'G3' ) {

			//G2/G3 - Arc Movement ( G2 clock wise and G3 counter clock wise )
			console.warn( 'THREE.GCodeLoader: Arc command not supported' );

		} else if ( cmd === 'G90' ) {

			//G90: Set to Absolute Positioning
			state.relative = false;

		} else if ( cmd === 'G91' ) {

			//G91: Set to state.relative Positioning
			state.relative = true;

		} else if ( cmd === 'G92' ) {

			//G92: Set Position
			var line = state;
			line.x = args.x !== undefined ? args.x : line.x;
			line.y = args.y !== undefined ? args.y : line.y;
			line.z = args.z !== undefined ? args.z : line.z;
			line.e = args.e !== undefined ? args.e : line.e;
			state = line;

		} else {

			//console.warn( 'THREE.GCodeLoader: Command not supported:' + cmd );

		}

	}

	function addObject( vertex, extruding ) {

		var geometry = new THREE.BufferGeometry();
		geometry.addAttribute( 'position', new THREE.Float32BufferAttribute( vertex, 3 ) );

		var colors = new Uint8Array(vertex.length);
		var bounding_box = { min_x: Infinity, min_y: Infinity, min_z: Infinity, max_x: -Infinity, max_y: -Infinity, max_z: -Infinity };

		for (var i = 0; i < vertex.length; i ++) {
			if (i % 3 == 0) {
				var new_color = (vertex[i+2]) * 1000 + 127;
				if (new_color > 255) new_color = 255;
				if (new_color < 0) new_color = 0;

				colors[i] = new_color;

				if (vertex[i + 0] < bounding_box.min_x) {
					bounding_box.min_x = vertex[i + 0];
				}
				if (vertex[i + 0] > bounding_box.max_x) {
					bounding_box.max_x = vertex[i + 0];
				}
				if (-vertex[i + 1] < bounding_box.min_z) {
					bounding_box.min_z = -vertex[i + 1];
				}
				if (-vertex[i + 1] > bounding_box.max_z) {
					bounding_box.max_z = -vertex[i + 1];
				}
			} else {
				colors[i] = 127;
			}
		}

		geometry.addAttribute( 'color', new THREE.BufferAttribute( colors, 3, true ) );

		var material = new THREE.MeshBasicMaterial( {vertexColors: THREE.VertexColors, side: THREE.DoubleSide} );
		var segments = new THREE.LineSegments( geometry, material );
		segments.name = 'layer' + i;
		object.add( segments );
		object.bounding_box = bounding_box;

	}

	var object = new THREE.Group();
	object.name = 'gcode';

	if ( this.splitLayer ) {

		for ( var i = 0; i < layers.length; i ++ ) {

			var layer = layers[ i ];
			addObject( layer.vertex, true );
			//addObject( layer.pathVertex, false );

		}

	} else {

		var vertex = [], pathVertex = [];

		for ( var i = 0; i < layers.length; i ++ ) {

			var layer = layers[ i ];

			vertex = vertex.concat( layer.vertex );
			pathVertex = pathVertex.concat( layer.pathVertex );

		}

		addObject( vertex, true );
		//addObject( pathVertex, false );

	}

	object.quaternion.setFromEuler( new THREE.Euler( - Math.PI / 2, 0, 0 ) );

	return object;

};
