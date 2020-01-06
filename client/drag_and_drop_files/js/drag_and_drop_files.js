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
			var font_size = 1/file.name.length * 300;
			if (font_size > 17.5) {
				font_size = 17.5;
			} else if (font_size < 6) {
				font_size = 6;
			}

			var shape_object_id = "shape_object_" + result.shape_object_id;

			var html = ' \
			<li id="' + shape_object_id + '" class="draggable_list_element" draggable="true"> \
				<header style="font-size:' + font_size + 'px; float: left; width: 80%">' + file.name + '</header> \
				<header style="float: right; text-align: right; width: 20%">' + result.shape_object_id + '</header>\
			</li>';
			var parent = document.getElementById("draggable_list");
			parent.insertAdjacentHTML('afterbegin', html)
			var elem = document.querySelector('#'+shape_object_id);
			addDnDHandlers(elem);
			select_element(elem);
			inject_thumbnail_svg_for_id(shape_object_id)

			// var settings_table = document.getElementById("convert_settings");
			// settings_table.innerHTML = '';
			// settings_table.insertAdjacentHTML('afterbegin', result.html);

			// Append a new shape object
			add_shape_object_to_list(shape_object_id, result.layout)
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