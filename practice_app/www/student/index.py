import frappe

def get_context(context):
	context.title = "Student Dashboard - EduPortal"
	user = frappe.session.user
	
	if user == "Guest":
		frappe.redirect("/login")

	roles = frappe.get_roles(user)
	is_admin = "System Manager" in roles or "Administrator" in roles or "Faculty" in roles
	preview_mode = frappe.form_dict.get("preview") or frappe.form_dict.get("view") == "portal" or frappe.form_dict.get("student")

	# Admins/Staff land on Desk (/app) unless explicitly requesting portal preview
	if is_admin and not preview_mode:
		frappe.redirect("/app")

	# Check if student parameter is passed in URL (e.g. for Admins/Faculty)
	req_student = frappe.form_dict.get("student")
	
	if req_student and ("System Manager" in frappe.get_roles(user) or "Administrator" in frappe.get_roles(user)):
		student = frappe.db.get_value(
			"Student-form",
			{"name": req_student},
			["name", "student_name", "register_number", "department", "semester", "year", "cgpa", "phone_number", "email", "student_photo"],
			as_dict=True
		)
	else:
		# Query student record linked to the logged in user's email or owner
		student = frappe.db.get_value(
			"Student-form",
			{"email": user},
			["name", "student_name", "register_number", "department", "semester", "year", "cgpa", "phone_number", "email", "student_photo"],
			as_dict=True
		) or frappe.db.get_value(
			"Student-form",
			{"owner": user},
			["name", "student_name", "register_number", "department", "semester", "year", "cgpa", "phone_number", "email", "student_photo"],
			as_dict=True
		)

	if not student:
		# User is an Admin or Staff without a linked Student record
		user_doc = frappe.get_doc("User", user)
		student = {
			"name": "",
			"student_name": user_doc.full_name or user,
			"register_number": "STAFF / ADMIN",
			"department": "Administration",
			"semester": "N/A",
			"year": "N/A",
			"cgpa": 0.0,
			"phone_number": user_doc.phone or "-",
			"email": user_doc.email,
			"student_photo": user_doc.user_image or "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80",
			"is_admin_preview": True
		}
		
	context.student = student
	
	if student.get("name"):
		all_m = frappe.get_all("Marks", filters={"student": student.get("name")}, fields=["obtained_marks", "total_marks"])
		if all_m:
			calc_cgpa = round(sum((float(m.get("obtained_marks") or 0) / float(m.get("total_marks") or 100)) * 10 for m in all_m) / len(all_m), 2)
			context.student["cgpa"] = calc_cgpa

		total_att = frappe.db.count("Attendance", {"student": student.get("name")})
		present_att = frappe.db.count("Attendance", {"student": student.get("name"), "status": "Present"})
		context.attendance_pct = round((present_att / total_att) * 100, 1) if total_att > 0 else 0.0
	else:
		context.attendance_pct = 0.0

	context.all_students = frappe.get_all("Student-form", fields=["name", "student_name", "register_number", "department"])

	context.notifications = frappe.get_all(
		"Notification",
		fields=["title", "category", "date", "message"],
		order_by="date desc",
		limit=5
	)

	return context
