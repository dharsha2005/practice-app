import frappe

def get_context(context):
	context.title = "Notifications & Downloads - EduPortal"
	user = frappe.session.user
	
	if user == "Guest":
		frappe.redirect("/login")

	roles = frappe.get_roles(user)
	is_admin = "System Manager" in roles or "Administrator" in roles or "Faculty" in roles
	preview_mode = frappe.form_dict.get("preview") or frappe.form_dict.get("view") == "portal" or frappe.form_dict.get("student")

	if is_admin and not preview_mode:
		frappe.redirect("/app")

	context.notifications = frappe.get_all(
		"Notification",
		fields=["title", "category", "target_role", "date", "message"],
		order_by="date desc"
	)

	return context
