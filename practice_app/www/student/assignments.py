import frappe
from datetime import datetime

base_template_path = "templates/portal_base.html"

def get_context(context):
	context.base_template_path = "templates/portal_base.html"
	context.title = "Assignment Management - EduPortal"
	user = frappe.session.user
	
	if user == "Guest":
		frappe.redirect("/login")

	roles = frappe.get_roles(user)
	is_admin = "System Manager" in roles or "Administrator" in roles or "Faculty" in roles
	preview_mode = frappe.form_dict.get("preview") or frappe.form_dict.get("view") == "portal" or frappe.form_dict.get("student")

	if is_admin and not preview_mode:
		frappe.redirect("/app")

	# Fetch the logged-in student's record
	student_doc = (
		frappe.db.get_value("Student-form", {"email": user}, ["name", "student_name", "department", "semester"], as_dict=True)
		or frappe.db.get_value("Student-form", {"owner": user}, ["name", "student_name", "department", "semester"], as_dict=True)
	)

	student_id = student_doc.get("name") if student_doc else None
	student_dept = student_doc.get("department") if student_doc else None

	# Build submission map: {assignment_name -> submission_doc}
	submission_map = {}
	if student_id:
		submissions = frappe.get_all(
			"Assignment Submission",
			filters={"student": student_id},
			# NOTE: Assignment Submission has marks_obtained and total_marks (correctly named)
			fields=["name", "assignment", "status", "submission_date", "marks_obtained", "total_marks", "faculty_feedback"],
		)
		for sub in submissions:
			submission_map[sub.get("assignment")] = sub

	# Fetch assignments filtered by student's department
	# NOTE: Assignment DocType uses 'total_points' NOT 'total_marks'
	dept_filter = {}
	if student_dept:
		# Department field on Assignment stores department code directly (IT, CSE, etc.)
		dept_filter["department"] = student_dept

	raw_assignments = frappe.get_all(
		"Assignment",
		filters=dept_filter if dept_filter else {},
		# FIXED: Use 'total_points' - the actual field name in Assignment DocType
		fields=["name", "title", "subject", "department", "due_date", "total_points", "attachment", "description"],
		order_by="due_date asc"
	)

	# Fallback: if no dept-filtered results, show all
	if not raw_assignments and dept_filter:
		raw_assignments = frappe.get_all(
			"Assignment",
			fields=["name", "title", "subject", "department", "due_date", "total_points", "attachment", "description"],
			order_by="due_date asc"
		)

	today_date = datetime.now().date()
	assignment_list = []

	for item in raw_assignments:
		assignment_name = item.get("name")
		due_d = item.get("due_date")

		# Normalize due_date to a date object
		if due_d and hasattr(due_d, 'date'):
			due_date_val = due_d.date()
		elif isinstance(due_d, str):
			try:
				due_date_val = datetime.strptime(due_d, "%Y-%m-%d").date()
			except Exception:
				due_date_val = None
		else:
			due_date_val = due_d

		# Check real submission status from Assignment Submission DocType
		if assignment_name in submission_map:
			sub = submission_map[assignment_name]
			real_status = sub.get("status") or "Submitted"
			if real_status == "Graded" and sub.get("marks_obtained") is not None:
				grade = f"{sub.get('marks_obtained')}/{sub.get('total_marks') or item.get('total_points') or 100}"
			elif real_status == "Graded":
				grade = "Graded"
			else:
				grade = "Pending Review"
			badge_class = {
				"Submitted": "badge-submitted",
				"Graded": "badge-graded",
				"Late": "badge-late",
				"Rejected": "badge-late"
			}.get(real_status, "badge-submitted")
			item["submission_id"] = sub.get("name")
		else:
			# Not submitted — check if overdue
			if due_date_val and due_date_val < today_date:
				real_status = "Late"
				badge_class = "badge-late"
				grade = "Overdue"
			else:
				real_status = "Pending"
				badge_class = "badge-pending"
				grade = "-"
			item["submission_id"] = None

		item["status"] = real_status
		item["badge_class"] = badge_class
		item["grade"] = grade
		# Normalize field name for template (use total_points as total_marks for display)
		item["display_points"] = item.get("total_points") or 100
		assignment_list.append(item)

	context.student = student_doc or {}
	context.assignments = assignment_list
	context.total_count = len(assignment_list)
	context.pending_count = sum(1 for a in assignment_list if a.get("status") == "Pending")
	context.submitted_count = sum(1 for a in assignment_list if a.get("status") in ["Submitted", "Late"])
	context.graded_count = sum(1 for a in assignment_list if a.get("status") == "Graded")

	return context
