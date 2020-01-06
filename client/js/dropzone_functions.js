Dropzone.options.customDropzone = {
	acceptedFiles: ".gbr",
	createImageThumbnails: false,
	clickable: '#custom-dropzone-div',
	accept: function(file, done) {
		while (this.files.length > 0) {
			var font_size = 1/this.files[0].name.length * 350;
			if (font_size > 17.5) {
				font_size = 17.5;
			} else if (font_size < 6) {
				font_size = 6;
			}
			var html = ' \
			<li class="draggable_list_element" draggable="true"> \
				<header style="font-size:' + font_size + 'px">' + this.files[0].name + '</header> \
			</li>';
			var parent = document.getElementById("draggable_list");
			parent.insertAdjacentHTML('afterbegin', html)
			var elem = document.querySelector('#draggable_list .draggable_list_element');
			addDnDHandlers(elem);
			select_element(elem);

			this.removeFile(this.files[0])
		}
		done();
	}
}