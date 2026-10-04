import frappe
from frappe.model.document import Document

class Course(Document):
	def validate(self):
		if self.course_code:
			self.course_code = self.course_code.upper().strip()
