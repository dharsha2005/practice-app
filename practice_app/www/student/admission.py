import frappe

def get_context(context):
	context.title = "Admissions 2026-2027 - EduPortal"
	
	context.courses = frappe.get_all(
		"Course",
		fields=["name", "course_name", "department", "duration_years", "description", "credits"],
		order_by="department asc"
	)

	return context
