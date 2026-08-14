import frappe

def get_context(context):
	context.title = "Student & Portal Login - EduPortal"
	context.no_cache = 1

	# If already logged in, redirect based on user role
	if frappe.session.user != "Guest":
		roles = frappe.get_roles(frappe.session.user)
		if "Student" in roles:
			frappe.redirect("/student")
			return context
		else:
			frappe.redirect("/app")
			return context

	return context
