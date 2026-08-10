import frappe
from frappe import _

def execute(filters=None):
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	report_summary = get_report_summary(data)

	return columns, data, None, chart, report_summary

def get_columns():
	return [
		{"label": _("Student Name"), "fieldname": "student_name", "fieldtype": "Data", "width": 180},
		{"label": _("Register Number"), "fieldname": "register_number", "fieldtype": "Data", "width": 140},
		{"label": _("Department"), "fieldname": "department", "fieldtype": "Data", "width": 120},
		{"label": _("Year"), "fieldname": "year", "fieldtype": "Data", "width": 80},
		{"label": _("Semester"), "fieldname": "semester", "fieldtype": "Data", "width": 90},
		{"label": _("Phone Number"), "fieldname": "phone_number", "fieldtype": "Phone", "width": 130},
		{"label": _("CGPA"), "fieldname": "cgpa", "fieldtype": "Float", "width": 100}
	]

def get_data(filters):
	conditions = {}
	if filters.get("department"):
		conditions["department"] = filters.get("department")
	if filters.get("year"):
		conditions["year"] = filters.get("year")
	if filters.get("semester"):
		conditions["semester"] = filters.get("semester")

	return frappe.get_all(
		"Student-form",
		filters=conditions,
		fields=["student_name", "register_number", "department", "year", "semester", "phone_number", "cgpa"],
		order_by="department asc, student_name asc"
	)

def get_chart_data(data):
	dept_counts = {}
	for row in data:
		dept = row.get("department") or "Unassigned"
		dept_counts[dept] = dept_counts.get(dept, 0) + 1

	labels = list(dept_counts.keys())
	values = list(dept_counts.values())

	return {
		"data": {
			"labels": labels,
			"datasets": [{"name": _("Students"), "values": values}]
		},
		"type": "bar",
		"colors": ["#4f46e5"]
	}

def get_report_summary(data):
	total_students = len(data)
	cgpa_sum = sum(float(row.get("cgpa") or 0) for row in data)
	avg_cgpa = round(cgpa_sum / total_students, 2) if total_students > 0 else 0.0

	return [
		{
			"value": total_students,
			"indicator": "Blue",
			"label": _("Total Enrolled Students"),
			"datatype": "Int"
		},
		{
			"value": avg_cgpa,
			"indicator": "Green" if avg_cgpa >= 7.5 else "Orange",
			"label": _("Average CGPA"),
			"datatype": "Float"
		}
	]