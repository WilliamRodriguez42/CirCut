
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

function error_message() {
	con.error("Could not reach server");
}

function handle_command(command){
	$.ajax({
		type: "POST",
		url:"/command",
		data: {
			command: command
		},
		success: function() {
				con.log(res.responseText);

				if (command.startsWith('level')) {
					load_gcodes();
				}

				scroll_to_bottom();
		},
		error: function() {
			error_message();
		}
	});

	scroll_to_bottom();
};
