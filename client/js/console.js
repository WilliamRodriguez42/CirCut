
var con = new SimpleConsole({
	handleCommand: handle_command,
	placeholder: "GCode or built-in command",
	storageID: "simple-console gcode"
});

document.getElementById("console_window_panel").appendChild(con.element);

con.logHTML(
	"<p>Enter GCode or built-in command</p>"
);

function scroll_to_bottom() {
	setTimeout(
		function() {
			document.getElementById("console_window_panel").scrollTop = document.getElementById("console_window_panel").scrollHeight;
		},
		100);
}

function console_display_message(m) {

	if (m.id === undefined) { // If this message was user generated, upload it to the server to archive it, we will display it when we read it back from the server
		$.ajax({
			type: "POST",
			url: "/archive-message",
			data: m
		});
		return;

	} else if (m.type === "error") {
		con.error("ERROR: " + m.message);
	} else if (m.type === "warning") {
		con.warn("WARNING: " + m.message);
	} else if (m.type === "info") {
		con.log("INFO: " + m.message);
	} else if (m.type === "input") {
		con.log("> " + m.message);
	}

	scroll_to_bottom();
}

function handle_command(command_entry, command){
	$.ajax({
		type: "POST",
		url:"/command",
		data: {
			command: command
		},
		success: function(status) {
			con.edit_status(command_entry, status);
		},
		error: function() {
			console_display_message({
				type: "error",
				message: "Could not connect to server"
			});
		}
	});

	scroll_to_bottom();
};
