import frappe

def get_context(context):
	context.courses = frappe.get_all("Course", fields=["course_name", "course_code", "department", "credits"])