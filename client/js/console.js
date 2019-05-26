
var con = new SimpleConsole({
	handleCommand: handle_command,
	placeholder: "GCode or built in command",
	storageID: "simple-console gcode"
});

document.getElementById("console-window").appendChild(con.element);

con.logHTML(
	"<h1>AutoLevel</h1>" +
	"<p>Enter GCode or built in command</p>"
);

function scroll_to_bottom() {
	setTimeout(function() {
		document.getElementById("console-window").scrollTop = document.getElementById("console-window").scrollHeight;
	},100);
}

function error_message() {
	con.error("Could not reach server");
}

function handle_command(command){
	$.ajax({type: "POST", url:"/command", data: { command: command }, async: true, complete: function(res) {
		if (res.status == 200) {
			con.log(res.responseText);

			if (command.startsWith('level')) {
				load_gcodes();
			}

			scroll_to_bottom();
		} else {
			error_message();
		}
	}});

	scroll_to_bottom();
};
