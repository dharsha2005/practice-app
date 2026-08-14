import frappe

base_template_path = "templates/portal_base.html"

def parse_sem_num(sem_val):
	if not sem_val:
		return 1
	sem_str = str(sem_val).lower().replace("semester", "").strip()
	try:
		return int(sem_str)
	except ValueError:
		return 1

def get_context(context):
	context.base_template_path = "templates/portal_base.html"
	context.title = "Course Feedback - EduPortal"
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

	student_doc = (
		frappe.db.get_value("Student-form", {"email": user}, ["name", "student_name", "register_number", "department", "semester", "student_photo"], as_dict=True)
		or frappe.db.get_value("Student-form", {"owner": user}, ["name", "student_name", "register_number", "department", "semester", "student_photo"], as_dict=True)
	)
	context.student = student_doc or {}
	student_id = student_doc.get("name") if student_doc else None
	student_dept = student_doc.get("department") or "CSE"
	sem_num = parse_sem_num(student_doc.get("semester"))
	current_sem_title = f"Semester {sem_num}"

	dept_name = (
		frappe.db.get_value("Department", {"department_name": student_dept}, "name")
		or frappe.db.get_value("Department", {"department_code": student_dept}, "name")
		or student_dept
	)

	courses = frappe.get_all(
		"Course",
		filters={"department": dept_name, "semester": current_sem_title},
		fields=["name", "course_name", "course_code"],
		order_by="course_name asc"
	)
	if not courses:
		courses = frappe.get_all(
			"Course",
			filters={"department": dept_name},
			fields=["name", "course_name", "course_code"],
			order_by="course_name asc"
		)

	# Fetch existing feedback submissions
	my_feedbacks = []
	if student_id:
		my_feedbacks = frappe.get_all(
			"Course Feedback",
			filters={"student": student_id},
			fields=["name", "course", "course_name", "rating", "teaching_quality", "content_quality", "comments", "submitted_on"],
			order_by="submitted_on desc"
		)

	submitted_course_names = {fb.get("course") for fb in my_feedbacks}

	context.courses = courses
	context.feedbacks = my_feedbacks
	context.submitted_courses = submitted_course_names
	return context
