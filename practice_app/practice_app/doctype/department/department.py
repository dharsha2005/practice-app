import frappe
from frappe.model.document import Document

class Department(Document):
	def validate(self):
		if self.department_code:
			self.department_code = self.department_code.upper().strip()
