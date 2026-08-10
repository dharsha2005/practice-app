import frappe

def get_context(context):
	context.title = "Faculty Directory - EduPortal"
	
	context.faculty = frappe.get_all(
		"Faculty",
		fields=["faculty_name", "designation", "department", "email", "qualification", "photo"],
		order_by="department asc, designation asc"
	)

	return context
