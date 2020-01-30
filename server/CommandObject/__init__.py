import threading

class CommandObject():
	def __init__(self, text):
		self.text = text
		self.event = threading.Event()
		self.status = ""

	def wait_until_complete(self):
		self.event.wait()

	def set_complete(self):
		self.status = "Ok"
		self.event.set()

	def set_terminated(self):
		self.status = "Terminated"
		self.event.set()

class TerminateObject(CommandObject):
	def __init__(self):
		super().__init__("stop")
		self.event.set()

	def send_terminate_signal(self):
		self.event.clear()

	def wait_until_terminated(self):
		self.event.wait()

	def termination_pending(self):
		return self.event.is_set() == False

class CommandObjectList(list):
	def __init__(self):
		super().__init__([])
		self.event = threading.Event()

	def append(self, value):
		super().append(value)
		self.event.set()

	def __delitem__(self, index):
		super().__delitem__(index)
		if len(self) == 0:
			self.event.clear()

	def wait_until_populated(self):
		self.event.wait()

	def clear(self):
		super().clear()
		self.event.clear()

