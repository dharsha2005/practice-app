import frappe
import re

base_template_path = "templates/portal_base.html"

def get_context(context):
	context.base_template_path = "templates/portal_base.html"
	context.title = "Notifications & Announcements - EduPortal"
	user = frappe.session.user
	
	if user == "Guest":
		frappe.redirect("/login")

	roles = frappe.get_roles(user)
	is_admin = "System Manager" in roles or "Administrator" in roles or "Faculty" in roles
	preview_mode = frappe.form_dict.get("preview") or frappe.form_dict.get("view") == "portal" or frappe.form_dict.get("student")

	if is_admin and not preview_mode:
		frappe.redirect("/app")

	# Fetch valid student announcements, filtering out raw system integration error logs
	all_notifs = frappe.get_all(
		"Notification",
		fields=["title", "category", "target_role", "date", "message"],
		order_by="date desc"
	)

	clean_notifs = []
	for notif in all_notifs:
		msg = notif.get("message") or ""
		# Skip system integration request / raw error Jinja templates
		if "{{" in msg or "{%" in msg or "doc.reference_doctype" in msg or "Error Details" in msg or "Response Output" in msg:
			continue
		
		# Clean HTML tags if text editor contains raw markup
		notif["clean_message"] = re.sub(r'<[^>]+>', '', msg)
		clean_notifs.append(notif)

	context.notifications = clean_notifs
	return context
