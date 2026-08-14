# Copyright (c) 2026, Dharshan and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CourseFeedback(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		comments: DF.SmallText | None
		content_quality: DF.Int
		course: DF.Link
		course_name: DF.Data | None
		faculty_name: DF.Data | None
		rating: DF.Int
		semester: DF.Data | None
		student: DF.Link
		student_name: DF.Data | None
		submitted_on: DF.Date | None
		teaching_quality: DF.Int
	# end: auto-generated types

	_DOCTYPE_NAME = "Course Feedback"
