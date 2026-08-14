import frappe

base_template_path = "templates/portal_base.html"

def get_context(context):
	context.base_template_path = "templates/portal_base.html"
	context.title = "Student Attendance - EduPortal"
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

	req_student = frappe.form_dict.get("student")
	
	if req_student and ("System Manager" in roles or "Administrator" in roles):
		student_doc = frappe.db.get_value("Student-form", {"name": req_student}, ["name", "student_name", "department", "semester"], as_dict=True)
		student_name_id = req_student
	else:
		student_doc = (
			frappe.db.get_value("Student-form", {"email": user}, ["name", "student_name", "department", "semester"], as_dict=True)
			or frappe.db.get_value("Student-form", {"owner": user}, ["name", "student_name", "department", "semester"], as_dict=True)
		)
		student_name_id = student_doc.get("name") if student_doc else None

	# Fetch ALL attendance records for this student from Attendance DocType
	attendance_list = []
	overall_pct = 0.0
	subject_summary = {}

	if student_name_id:
		attendance_list = frappe.get_all(
			"Attendance",
			filters={"student": student_name_id},
			fields=["date", "subject", "status", "remarks"],
			order_by="date desc"
		)

		total = len(attendance_list)
		present = sum(1 for a in attendance_list if a.get("status") == "Present")
		absent = sum(1 for a in attendance_list if a.get("status") == "Absent")
		on_leave = sum(1 for a in attendance_list if a.get("status") == "On Leave")
		overall_pct = round((present / total) * 100, 1) if total > 0 else 0.0

		# Build per-subject summary
		for record in attendance_list:
			subj = record.get("subject") or "General"
			if subj not in subject_summary:
				subject_summary[subj] = {"total": 0, "present": 0, "absent": 0, "on_leave": 0}
			subject_summary[subj]["total"] += 1
			if record.get("status") == "Present":
				subject_summary[subj]["present"] += 1
			elif record.get("status") == "Absent":
				subject_summary[subj]["absent"] += 1
			elif record.get("status") == "On Leave":
				subject_summary[subj]["on_leave"] += 1

		# Calculate percentage and attendance class for each subject
		for subj, data in subject_summary.items():
			pct = round((data["present"] / data["total"]) * 100, 1) if data["total"] > 0 else 0.0
			data["percentage"] = pct
			# Attendance status badge
			if pct >= 75:
				data["status_class"] = "bg-success"
				data["status_label"] = "Good Standing"
			elif pct >= 60:
				data["status_class"] = "bg-warning text-dark"
				data["status_label"] = "Warning"
			else:
				data["status_class"] = "bg-danger"
				data["status_label"] = "Critical"

		context.total_classes = total
		context.present_count = present
		context.absent_count = absent
		context.on_leave_count = on_leave
	else:
		context.total_classes = 0
		context.present_count = 0
		context.absent_count = 0
		context.on_leave_count = 0

	# Attendance badge class for overall percentage
	if overall_pct >= 75:
		context.overall_badge = "bg-success"
	elif overall_pct >= 60:
		context.overall_badge = "bg-warning text-dark"
	else:
		context.overall_badge = "bg-danger"

	context.student = student_doc or {}
	context.attendance_list = attendance_list
	context.overall_attendance = overall_pct
	context.subject_summary = subject_summary
	return context
