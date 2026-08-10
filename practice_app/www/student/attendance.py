import frappe

def get_context(context):
	context.title = "Student Attendance - EduPortal"
	user = frappe.session.user
	
	if user == "Guest":
		frappe.redirect("/login")

	roles = frappe.get_roles(user)
	is_admin = "System Manager" in roles or "Administrator" in roles or "Faculty" in roles
	preview_mode = frappe.form_dict.get("preview") or frappe.form_dict.get("view") == "portal" or frappe.form_dict.get("student")

	if is_admin and not preview_mode:
		frappe.redirect("/app")

	req_student = frappe.form_dict.get("student")
	
	if req_student and ("System Manager" in frappe.get_roles(user) or "Administrator" in frappe.get_roles(user)):
		student_name = req_student
	else:
		student_name = frappe.db.get_value("Student-form", {"email": user}, "name") or frappe.db.get_value("Student-form", {"owner": user}, "name")
	
	if student_name:
		context.attendance_list = frappe.get_all(
			"Attendance",
			filters={"student": student_name},
			fields=["date", "subject", "status", "remarks"],
			order_by="date desc"
		)
		total_att = len(context.attendance_list)
		present_att = sum(1 for a in context.attendance_list if a.get("status") == "Present")
		context.overall_attendance = round((present_att / total_att) * 100, 1) if total_att > 0 else 0.0
	else:
		context.attendance_list = []
		context.overall_attendance = 0.0

	return context
