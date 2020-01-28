function prevent_defaults(e) {
	e.preventDefault();
	e.stopPropagation();
}

function highlight(e) {
	drop_area.classList.add('highlight');
}

function unhighlight(e) {
	drop_area.classList.remove('highlight');
}

function handle_drop(e) {
	var dt = e.dataTransfer;
	var files = dt.files;

	handle_dropped_files(files);
}

function handle_dropped_files(files) {
	([...files]).forEach(upload_file);
}

function upload_file(file) {
	var data = new FormData();
	data.append('file', file);

	$.ajax({
		type: "POST",
		url: "/file_upload",
		processData: false,
		contentType: false,
		cache: false,
		data: data,
		enctype: 'multipart/form-data',
		success: function(result) {
			shape_object_response(result);
		}
	});
}

var drop_area = document.getElementById("drop_area");
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(event_name => {
	drop_area.addEventListener(event_name, prevent_defaults, false);
});

['dragenter', 'dragover'].forEach(event_name => {
	drop_area.addEventListener(event_name, highlight, false);
});

['dragleave', 'drop'].forEach(event_name => {
	drop_area.addEventListener(event_name, unhighlight, false);
});

drop_area.addEventListener('drop', handle_drop, false);