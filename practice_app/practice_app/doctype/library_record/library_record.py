# Copyright (c) 2026, Dharshan and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class LibraryRecord(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		author: DF.Data | None
		book_title: DF.Data
		due_date: DF.Date | None
		fine_amount: DF.Currency
		isbn: DF.Data | None
		issue_date: DF.Date | None
		return_date: DF.Date | None
		status: DF.Literal["Issued", "Returned", "Overdue"]
		student: DF.Link | None
		student_name: DF.Data | None
	# end: auto-generated types

	_DOCTYPE_NAME = "Library Record"
