# Copyright (c) 2026, Dharshan and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ExamScheduleItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		course: DF.Link
		course_code: DF.Data | None
		course_name: DF.Data | None
		exam_date: DF.Date
		exam_time: DF.Literal["09:00 AM - 12:00 PM", "02:00 PM - 05:00 PM"]
		hall_no: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
	# end: auto-generated types

	_DOCTYPE_NAME = "Exam Schedule Item"
