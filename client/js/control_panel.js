function distance_pre_check() {
	var amount = parseFloat($('#move_distance').val());
	if (!(amount > 0)) {
		invalid('move_distance');
		console_display_message({
			type: "error",
			message: "Move distance must be a value greater than 0"
		});
		return -1;
	}
	return amount;
}

function control_panel_send_command(command, callback = function(command_entry, status){}) {
	con.enter_user_command(command, callback);
}

function move_Zp() {
	var amount = distance_pre_check();
	if (amount < 0) {
		return;
	}
	var command = "$J=G21G91 Z" + amount + " F500";
	control_panel_send_command(command);
}

function move_Zn() {
	var amount = distance_pre_check();
	if (amount < 0) return;

	if (amount > 1) {
		console_display_message({
			type: "error",
			message: "For the safety of your machine, please do not move more than 1 mm at at time in the Z- axis"
		});
		return;
	}
	var command = "$J=G21G91 Z-" + amount + " F500";
	control_panel_send_command(command);
}

function move_Yp() {
	var amount = distance_pre_check();
	if (amount < 0) return;

	var command = "$J=G21G91 Y" + amount + " F500";
	control_panel_send_command(command);
}

function move_Yn() {
	var amount = distance_pre_check();
	if (amount < 0) return;

	var command = "$J=G21G91 Y-" + amount + " F500";
	control_panel_send_command(command);
}

function move_Xp() {
	var amount = distance_pre_check();
	if (amount < 0) return;

	var command = "$J=G21G91 X" + amount + " F500";
	control_panel_send_command(command);
}

function move_Xn() {
	var amount = distance_pre_check();
	if (amount < 0) return;

	var command = "$J=G21G91 X-" + amount + " F500";
	control_panel_send_command(command);
}

function level_args_precheck() {
	var safety_height = parseFloat($('#leveling_safety_height').val());
	if (safety_height <= 0) {
		invalid('leveling_safety_height');
		console_display_message({
			type: "error",
			message: "Safety height must be a value greater than 0"
		});
		return [-1, -1, -1];
	}
	var x_axis_step = parseFloat($('#leveling_x_axis_step').val());
	if (x_axis_step <= 0) {
		invalid('leveling_safety_height');
		console_display_message({
			type: "error",
			message: "X axis step must be a value greater than 0"
		});
		return [-1, -1, -1];
	}
	var y_axis_step = parseFloat($('#leveling_y_axis_step').val());
	if (y_axis_step <= 0) {
		invalid('leveling_safety_height');
		console_display_message({
			type: "error",
			message: "Y axis step must be a value greater than 0"
		});
		return [-1, -1, -1];
	}
	return [safety_height, x_axis_step, y_axis_step];
}

function level() {
	var [safety_height, x_axis_step, y_axis_step] = level_args_precheck();
	if (safety_height < 0) return;

	var command = "level " + x_axis_step + " " + y_axis_step + " " + safety_height;
	control_panel_send_command(
		command, 
		function(command_entry, status){
			update_all_gcodes();
		}
	);
}

function terminate() {
	var command = "stop";
	control_panel_send_command(command);
}

function zero() {
	var command = "zero";
	control_panel_send_command(command);
}

function probez() {
	var command = "probez";
	control_panel_send_command(command);
}

function unlevel() {
	var command = "unlevel";
	control_panel_send_command(
		command, 
		function(command_entry, status){
			update_all_gcodes();
		}
	);
}

function send_gcode() {
	var command = "send_gcode";
	control_panel_send_command(command);
}

function z_height_precheck() {
	var z_height = parseFloat($("#change_z_height_by").val())
	if (z_height <= 0) {
		invalid('change_z_height_by');
		console_display_message({
			type: "error",
			message: "Change in Z height must be a value greater than 0"
		});
		return -1
	}
	return z_height;
}

function raise_z_height() {
	var dz = z_height_precheck()
	if (dz < 0) return;

	var command = "r " + dz;
	control_panel_send_command(
		command, 
		function(command_entry, status){
			update_all_gcodes();
		}
	);
}

function lower_z_height() {
	var dz = z_height_precheck()
	if (dz < 0) return;

	var command = "l " + dz;
	control_panel_send_command(
		command, 
		function(command_entry, status){
			update_all_gcodes();
		}
	);
}

function connect() {
	$.ajax({
		type: "POST",
		url:"/connect",
		data: {
			port: $("#connection_port").val()
		}
	});
}

function disconnect() {
	$.ajax({
		type: "POST",
		url:"/disconnect",
	});
}