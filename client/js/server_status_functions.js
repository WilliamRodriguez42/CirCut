
function start_server_polling() {
	poll_server_status_id = setInterval(get_server_status, 500);
}

function get_server_status() {
	$.ajax({
		type: "GET",
		url: "status",
		success: function(data) {
			// Handle convert status
			convert_curr_state_text = data.text;
			if (convert_prev_state_text != convert_curr_state_text) {
				convert_curr_state = 100 / data.of * data.step;
				progress_move(convert_prev_state, convert_curr_state, convert_curr_state_text);
				convert_prev_state = convert_curr_state;

				convert_prev_state_text = convert_curr_state_text;
			}

			// Handle server messages
			if (status_first_load === true) {
				status_first_load = false;

				if (data.status_messages.length) status_latest_id = data.status_messages[0].id;

				for (var i = data.status_messages.length-1; i >= 0 ; i --) {
					console_display_message(data.status_messages[i]);
				}

				con.log("^^^^^^^^^^^^^^^^ END OF RESTORED LOG ^^^^^^^^^^^^^^^^");
			} else {
				if (data.status_messages.length !== 0 && data.status_messages[0].id !== status_latest_id) {
					var num_to_load = data.status_messages[0].id - status_latest_id;
					status_latest_id = data.status_messages[0].id;

					for (var i = num_to_load-1; i >= 0; i --) {
						if (data.status_messages[i].type !== "input") {
							console_display_message(data.status_messages[i]);
						}
					}
				}
			}

		}
	})
}

var poll_server_status_id = null;
var status_latest_id = -1;
var status_first_load = true;
