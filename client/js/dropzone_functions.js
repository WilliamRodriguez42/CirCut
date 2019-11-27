Dropzone.options.gerberDropzone = {
	acceptedFiles: ".gbr",
	createImageThumbnails: false,
	clickable: '#gerber-dropzone-div',
	accept: function(file, done) {
		if (this.files.length > 1) {
			this.removeFile(this.files[0])
		}
		done();
	}
}

Dropzone.options.excellonDropzone = {
	acceptedFiles: ".drl,.txt",
	createImageThumbnails: false,
	clickable: '#excellon-dropzone-div',
	accept: function(file, done) {
		if (this.files.length > 1) {
			this.removeFile(this.files[0])
		}
		done();
	}
}
