
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

				if (data.load_svg && !convert_svg_loaded) {
					load_svg();
					convert_svg_loaded = true;

					console.log("HI");
				}
			}

			// Handle server messages
			if (status_first_load === true) {
				status_first_load = false;

				if (data.status_messages.length) status_latest_id = data.status_messages[0].id;

				for (var i = data.status_messages.length-1; i >= 0 ; i --) {
					console_display_message(data.status_messages[i]);
				}
			} else {
				if (data.status_messages.length !== 0 && data.status_messages[0].id !== status_latest_id) {
					status_latest_id = data.status_messages[0].id;

					if (data.status_messages[0].type !== "input") {
						console_display_message(data.status_messages[0]);
					}
				}
			}
		}
	})
}

var poll_server_status_id = null;
var status_latest_id = -1;
var status_first_load = true;
