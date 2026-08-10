import frappe

def get_context(context):
	context.title = "Marks & Grades - EduPortal"
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
		student_doc = frappe.db.get_value("Student-form", {"name": req_student}, ["name", "cgpa"], as_dict=True)
	else:
		student_doc = frappe.db.get_value("Student-form", {"email": user}, ["name", "cgpa"], as_dict=True) or frappe.db.get_value("Student-form", {"owner": user}, ["name", "cgpa"], as_dict=True)
	
	if student_doc:
		context.marks_list = frappe.get_all(
			"Marks",
			filters={"student": student_doc.get("name")},
			fields=["subject", "exam_type", "total_marks", "obtained_marks", "grade"],
			order_by="modified desc"
		)

		has_fail = any("Fail" in (m.get("grade") or "") or float(m.get("obtained_marks") or 0) < 40 for m in context.marks_list)
		
		if context.marks_list:
			calc_cgpa = round(sum((float(m.get("obtained_marks") or 0) / float(m.get("total_marks") or 100)) * 10 for m in context.marks_list) / len(context.marks_list), 2)
			context.cgpa = calc_cgpa
			if student_doc.get("name"):
				frappe.db.set_value("Student-form", student_doc.get("name"), "cgpa", calc_cgpa)
		else:
			context.cgpa = float(student_doc.get("cgpa") or 0.0)

		if has_fail:
			context.classification = "Arrear / Reappear Required"
			context.classification_badge_class = "bg-danger-subtle text-danger"
		elif context.cgpa >= 8.5:
			context.classification = "First Class with Distinction"
			context.classification_badge_class = "bg-primary-subtle text-primary"
		elif context.cgpa >= 7.0:
			context.classification = "First Class"
			context.classification_badge_class = "bg-success-subtle text-success"
		elif context.cgpa >= 5.5:
			context.classification = "Second Class"
			context.classification_badge_class = "bg-info-subtle text-info"
		elif context.cgpa >= 4.0:
			context.classification = "Pass Class"
			context.classification_badge_class = "bg-warning-subtle text-warning"
		else:
			context.classification = "Needs Improvement"
			context.classification_badge_class = "bg-danger-subtle text-danger"
	else:
		context.marks_list = []
		context.cgpa = 0.0
		context.classification = "No Records"
		context.classification_badge_class = "bg-secondary-subtle text-secondary"

	return context
