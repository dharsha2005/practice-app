import frappe
import re

base_template_path = "templates/portal_base.html"

def get_context(context):
	context.base_template_path = "templates/portal_base.html"
	context.title = "Campus Announcements - EduPortal"
	user = frappe.session.user
	
	if user == "Guest":
		frappe.redirect("/login")
		return context

	roles = frappe.get_roles(user)
	is_admin = "System Manager" in roles or "Administrator" in roles or "Faculty" in roles
	preview_mode = frappe.form_dict.get("preview") or frappe.form_dict.get("view") == "portal" or frappe.form_dict.get("student")

	if is_admin and not preview_mode:
		frappe.redirect("/app")
		return context

	# Fetch student for sidebar
	student_doc = (
		frappe.db.get_value("Student-form", {"email": user}, ["name", "student_name", "register_number", "student_photo"], as_dict=True)
		or frappe.db.get_value("Student-form", {"owner": user}, ["name", "student_name", "register_number", "student_photo"], as_dict=True)
	)
	context.student = student_doc or {}

	# Fetch all Notification records from DocType (announcements for students)
	all_notifs = frappe.get_all(
		"Notification",
		fields=["name", "title", "category", "date", "message", "target_role"],
		order_by="date desc",
		limit=50
	)

	# Filter out system/error records and clean HTML
	clean_notifs = []
	for notif in all_notifs:
		# Skip records without title (system records like 'Error Log', 'Integration Request')
		if not notif.get("title"):
			continue
		msg = notif.get("message") or ""
		# Skip records with raw Jinja/template content
		if "{{" in msg or "{%" in msg or "doc.reference_doctype" in msg:
			continue
		notif["clean_message"] = re.sub(r'<[^>]+>', '', msg)[:300]
		notif["category_badge"] = {
			"Exam Schedule": "bg-danger",
			"Fee Notice": "bg-warning text-dark",
			"Campus Event": "bg-success",
			"Holiday": "bg-info text-dark",
			"General": "bg-secondary"
		}.get(notif.get("category") or "", "bg-primary")
		clean_notifs.append(notif)

	context.announcements = clean_notifs
	context.total_count = len(clean_notifs)
	return context
