import frappe
from frappe import _

def execute(filters=None):
	columns = [
		{"label": _("Student Name"), "fieldname": "student_name", "fieldtype": "Data", "width": 200},
		{"label": _("Department"), "fieldname": "department", "fieldtype": "Data", "width": 120},
		{"label": _("Semester"), "fieldname": "semester", "fieldtype": "Data", "width": 100},
		{"label": _("CGPA"), "fieldname": "cgpa", "fieldtype": "Float", "width": 100}
	]

	data = frappe.get_all(
		"Student-form",
		fields=["student_name", "department", "semester", "cgpa"],
		order_by="cgpa desc"
	)

	chart = {
		"data": {
			"labels": [row["student_name"] for row in data[:10]],
			"datasets": [{"name": _("CGPA"), "values": [row["cgpa"] or 0 for row in data[:10]]}]
		},
		"type": "line",
		"colors": ["#10b981"]
	}

	return columns, data, None, chart
