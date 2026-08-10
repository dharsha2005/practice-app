# Copyright (c) 2026, Dharshan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Department(Document):
	def validate(self):
		if self.department_code:
			self.department_code = self.department_code.upper().strip()
