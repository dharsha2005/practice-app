import frappe
from frappe.model.document import Document

class LeaveApplication(Document):
	def before_save(self):
		"""Auto-calculate number of days when dates are set."""
		if self.from_date and self.to_date:
			from frappe.utils import date_diff
			self.no_of_days = date_diff(self.to_date, self.from_date) + 1
