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

function control_panel_send_command(command) {
	$.ajax({
		type: "POST",
		url:"/command",
		data: {
			command: command
		}
	});
	con.log("> " + command);
	scroll_to_bottom();
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
			message: "It is not recommended to move more than 1 mm at at time in the Z- axis"
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
	con.log(command);
	control_panel_send_command(command);
}
