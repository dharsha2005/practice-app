# Copyright (c) 2026, Dharshan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Course(Document):
	def validate(self):
		if self.course_code:
			self.course_code = self.course_code.upper().strip()
