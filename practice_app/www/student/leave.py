import frappe

base_template_path = "templates/portal_base.html"

def get_context(context):
	context.base_template_path = "templates/portal_base.html"
	context.title = "Leave Application - EduPortal"
	user = frappe.session.user
	
	if user == "Guest":
		frappe.redirect("/login")

	roles = frappe.get_roles(user)
	is_admin = "System Manager" in roles or "Administrator" in roles or "Faculty" in roles
	preview_mode = frappe.form_dict.get("preview") or frappe.form_dict.get("view") == "portal" or frappe.form_dict.get("student")

	if is_admin and not preview_mode:
		frappe.redirect("/app")

	# Fetch student details
	student_doc = (
		frappe.db.get_value("Student-form", {"email": user}, ["name", "student_name", "department", "semester"], as_dict=True)
		or frappe.db.get_value("Student-form", {"owner": user}, ["name", "student_name", "department", "semester"], as_dict=True)
	)

	student_id = student_doc.get("name") if student_doc else None

	# Fetch existing Leave Application records for this student from DocType
	leave_list = []
	if student_id:
		leave_list = frappe.get_all(
			"Leave Application",
			filters={"student": student_id},
			fields=["name", "leave_type", "from_date", "to_date", "no_of_days", "reason", "status", "faculty_remarks"],
			order_by="from_date desc"
		)

	# Status badge mapping
	for leave in leave_list:
		leave["badge_class"] = {
			"Pending": "badge-pending",
			"Approved": "badge-graded",
			"Rejected": "badge-late",
			"Cancelled": "bg-secondary"
		}.get(leave.get("status") or "Pending", "badge-pending")

	leave_types = ["Medical Leave", "Personal Leave", "Family Emergency", "OD (On Duty)", "Hospitalization", "Other"]

	context.student = student_doc or {}
	context.leave_list = leave_list
	context.leave_types = leave_types
	context.pending_count = sum(1 for l in leave_list if l.get("status") == "Pending")
	context.approved_count = sum(1 for l in leave_list if l.get("status") == "Approved")
	context.total_count = len(leave_list)
	return context
