
var con = new SimpleConsole({
	handleCommand: handle_command,
	placeholder: "GCode or built in command",
	storageID: "simple-console gcode"
});

document.getElementById("console_window_panel").appendChild(con.element);

con.logHTML(
	"<h1>AutoLevel</h1>" +
	"<p>Enter GCode or built in command</p>"
);

function scroll_to_bottom() {
	setTimeout(
		function() {
			document.getElementById("console_window_panel").scrollTop = document.getElementById("console_window_panel").scrollHeight;
		},
		100);
}

function console_display_message(m) {
	if (m.type === "error") {
		con.error("ERROR: " + m.message);
	} else if (m.type === "warning") {
		con.warn("WARNING: " + m.message)
	} else if (m.type === "info") {
		con.log(m.message)
	} else if (m.type === "input") {
		con.log("> " + m.message)
	}

	scroll_to_bottom();
}

function handle_command(command){
	$.ajax({
		type: "POST",
		url:"/command",
		data: {
			command: command
		},
		success: function(responseText) {
				if (command.startsWith('level')) {
					load_gcodes();
				}

				scroll_to_bottom();
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
