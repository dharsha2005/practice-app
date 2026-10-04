import frappe

def get_context(context):
	if frappe.session.user != "Guest":
		context.student = frappe.db.get_value("Student-form", {"email": frappe.session.user}, ["student_name", "register_number", "department", "gender"], as_dict=True)
