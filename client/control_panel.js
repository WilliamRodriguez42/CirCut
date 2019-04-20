function distance_pre_check() {
	var amount = parseFloat($('#distance_value').val());
	if (isNaN(amount) || amount <= 0) {
		con.error("Distance not valid");
		scroll_to_bottom();
		return -1;
	}
	return amount;
}

function move_Zp() {
	var amount = distance_pre_check();
	if (amount < 0) {
		return;
	}
	var command = "$J=G21G91 Z" + amount + " F500";
	con.log(command);
	$.ajax({type: "POST", url:"/command", data: { command: command }, async: true, complete: function(res) {
		if (res.status == 200) {
			con.log(res.responseText);
			scroll_to_bottom();
		} else {
			error_message();
		}
	}});
	scroll_to_bottom();
}

function move_Zn() {
	var amount = distance_pre_check();
	if (amount < 0) {
		return;
	}
	if (amount > 1) {
		con.error("It is not recommended to move more than 1 mm at at time in the Z- axis");
		scroll_to_bottom();
		return;
	}
	var command = "$J=G21G91 Z-" + amount + " F500";
	con.log(command);
	$.ajax({type: "POST", url:"/command", data: { command: command }, async: true, complete: function(res) {
		if (res.status == 200) {
			con.log(res.responseText);
			scroll_to_bottom();
		} else {
			error_message();
		}
	}});
	scroll_to_bottom();
}

function move_Yp() {
	var amount = distance_pre_check();
	if (amount < 0) {
		return;
	}
	var command = "$J=G21G91 Y" + amount + " F500";
	con.log(command);
	$.ajax({type: "POST", url:"/command", data: { command: command }, async: true, complete: function(res) {
		if (res.status == 200) {
			con.log(res.responseText);
			scroll_to_bottom();
		} else {
			error_message();
		}
	}});
	scroll_to_bottom();
}

function move_Yn() {
	var amount = distance_pre_check();
	if (amount < 0) {
		return;
	}
	var command = "$J=G21G91 Y-" + amount + " F500";
	con.log(command);
	$.ajax({type: "POST", url:"/command", data: { command: command }, async: true, complete: function(res) {
		if (res.status == 200) {
			con.log(res.responseText);
			scroll_to_bottom();
		} else {
			error_message();
		}
	}});
	scroll_to_bottom();
}

function move_Xp() {
	var amount = distance_pre_check();
	if (amount < 0) {
		return;
	}
	var command = "$J=G21G91 X" + amount + " F500";
	con.log(command);
	$.ajax({type: "POST", url:"/command", data: { command: command }, async: true, complete: function(res) {
		if (res.status == 200) {
			con.log(res.responseText);
			scroll_to_bottom();
		} else {
			error_message();
		}
	}});
	scroll_to_bottom();
}

function move_Xn() {
	var amount = distance_pre_check();
	if (amount < 0) {
		return;
	}
	var command = "$J=G21G91 X-" + amount + " F500";
	con.log(command);
	$.ajax({type: "POST", url:"/command", data: { command: command }, async: true, complete: function(res) {
		if (res.status == 200) {
			con.log(res.responseText);
			scroll_to_bottom();
		} else {
			error_message();
		}
	}});
	scroll_to_bottom();
}
