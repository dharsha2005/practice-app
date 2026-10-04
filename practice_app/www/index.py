import frappe

def get_context(context):
	context.departments = frappe.get_all("Department", fields=["department_name", "department_code"])
	context.total_courses = frappe.db.count("Course")
	context.total_students = frappe.db.count("Student-form")
