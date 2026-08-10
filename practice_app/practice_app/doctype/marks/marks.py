# Copyright (c) 2026, Dharshan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Marks(Document):
	def validate(self):
		if float(self.obtained_marks or 0) > float(self.total_marks or 100):
			frappe.throw("Obtained marks cannot exceed total marks.")
		
		pct = (float(self.obtained_marks or 0) / float(self.total_marks or 100)) * 100
		if pct >= 90:
			self.grade = "O (Outstanding)"
		elif pct >= 80:
			self.grade = "A+ (Excellent)"
		elif pct >= 70:
			self.grade = "A (Very Good)"
		elif pct >= 60:
			self.grade = "B+ (Good)"
		elif pct >= 50:
			self.grade = "B (Above Average)"
		elif pct >= 40:
			self.grade = "C (Pass)"
		else:
			self.grade = "F (Fail)"

	def on_update(self):
		self.update_student_cgpa()

	def on_trash(self):
		self.update_student_cgpa()

	def update_student_cgpa(self):
		if not self.student:
			return
		all_marks = frappe.get_all(
			"Marks",
			filters={"student": self.student},
			fields=["obtained_marks", "total_marks"]
		)
		if all_marks:
			total_gpa_points = sum((float(m.get("obtained_marks") or 0) / float(m.get("total_marks") or 100)) * 10 for m in all_marks)
			cgpa = round(total_gpa_points / len(all_marks), 2)
			frappe.db.set_value("Student-form", self.student, "cgpa", cgpa)
