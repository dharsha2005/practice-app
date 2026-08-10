# Copyright (c) 2026, Dharshan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Faculty(Document):
	def validate(self):
		if self.employee_id:
			self.employee_id = self.employee_id.upper().strip()
