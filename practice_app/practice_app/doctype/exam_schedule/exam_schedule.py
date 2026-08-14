# Copyright (c) 2026, Dharshan and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ExamSchedule(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from practice_app.practice_app.doctype.exam_schedule_item.exam_schedule_item import ExamScheduleItem

		academic_year: DF.Data | None
		department: DF.Link
		is_published: DF.Check
		schedule_items: DF.Table[ExamScheduleItem]
		semester: DF.Literal["Semester 1", "Semester 2", "Semester 3", "Semester 4", "Semester 5", "Semester 6", "Semester 7", "Semester 8"]
		title: DF.Data
	# end: auto-generated types

	_DOCTYPE_NAME = "Exam Schedule"
