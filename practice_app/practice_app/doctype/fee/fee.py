# Copyright (c) 2026, Dharshan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Fee(Document):
	def validate(self):
		self.total_amount = float(self.tuition_fee or 0) + float(self.hostel_fee or 0) + float(self.other_fee or 0)
		self.outstanding_amount = self.total_amount - float(self.paid_amount or 0)
		
		if self.outstanding_amount <= 0:
			self.status = "Paid"
			self.outstanding_amount = 0
		elif self.paid_amount > 0:
			self.status = "Partially Paid"
		else:
			self.status = "Unpaid"
