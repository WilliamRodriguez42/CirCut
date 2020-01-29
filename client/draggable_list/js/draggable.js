var dragSrcEl = null;

function handleDragStart(e) {
	// Target (this) element is the source node.
	dragSrcEl = this;

	e.dataTransfer.effectAllowed = 'move';
	e.dataTransfer.setData('text/html', this.outerHTML);

	this.classList.add('dragElem');
}
function handleDragOver(e) {
	if (e.preventDefault) {
		e.preventDefault(); // Necessary. Allows us to drop.
	}
	this.classList.add('over');

	e.dataTransfer.dropEffect = 'move';  // See the section on the DataTransfer object.

	return false;
}

function handleDragEnter(e) {
	// this / e.target is the current hover target.
}

function handleDragLeave(e) {
	this.classList.remove('over');  // this / e.target is previous target element.
}

function handleDrop(e) {
	// this/e.target is current target element.
	if (e.stopPropagation) {
		e.stopPropagation(); // Stops some browsers from redirecting.
	}

	// Don't do anything if dropping the same column we're dragging.
	if (dragSrcEl != this) {

		if (this.id == 'non_draggable_list_element') {
			position_svg_for_id(dragSrcEl.id, "top");
			$.ajax({
				type: "POST",
				url: "/reorder_shape_objects",
				data: {shape_object_id: dragSrcEl.id, inject_before_id: "shape_object_-1"},
			});
		} else {
			position_svg_for_id(dragSrcEl.id, this.id);
			$.ajax({
				type: "POST",
				url: "/reorder_shape_objects",
				data: {shape_object_id: dragSrcEl.id, inject_before_id: this.id},
			});
		}

		this.parentNode.removeChild(dragSrcEl);
		var dropHTML = e.dataTransfer.getData('text/html');
		this.insertAdjacentHTML('beforebegin', dropHTML);
		var dropElem = this.previousSibling;
		addDnDHandlers(dropElem);

		if (dragSrcEl.classList.contains('chosen')) {
			previously_selected_element = dropElem;
		}

	}
	this.classList.remove('over');
	return false;
}

function handleDragEnd(e) {
	// this/e.target is the source node.
	this.classList.remove('over');
	this.classList.remove('dragElem');

	/*[].forEach.call(elements, function (col) {
		col.classList.remove('over');
	});*/
}

function select_element(elem) {
	if (previously_selected_element != elem) {
		if (previously_selected_element !== null) {
			update_shape_object_settings_from_html(previously_selected_element.id);
		}

		elem.classList.add('chosen');
		if (previously_selected_element != null) {
			previously_selected_element.classList.remove('chosen');
		}
		
		previously_selected_element = elem;

		// Update selected file text
		var selected_file_text_element = document.querySelector("#selected_file_text");
		selected_file_text_element.innerText = elem.querySelector("header").innerText;

		update_html_for_id(elem.id);
	}
}

function handleClick(e) {
	select_element(this);
}

function addNonSelectHandlers(elem) {
	elem.addEventListener('dragstart', handleDragStart, false);
	elem.addEventListener('dragenter', handleDragEnter, false)
	elem.addEventListener('dragover', handleDragOver, false);
	elem.addEventListener('dragleave', handleDragLeave, false);
	elem.addEventListener('drop', handleDrop, false);
	elem.addEventListener('dragend', handleDragEnd, false);
}
function addDnDHandlers(elem) {
	addNonSelectHandlers(elem);
	elem.addEventListener('click', handleClick, false);
}

function delete_shape_object(elem) {
	var parent = elem.parentNode;
	var grand_parent = parent.parentNode;
	grand_parent.removeChild(parent);

	remove_svg_for_id(parent.id);
	remove_shape_object_from_list(parent.id);
}

var element = document.querySelector('#draggable_list .draggable_list_element');
addNonSelectHandlers(element);
var previously_selected_element = null;