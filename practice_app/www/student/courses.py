import frappe

base_template_path = "templates/portal_base.html"

def parse_sem_num(sem_val):
	"""Extracts integer semester number from string (e.g., '1', 'Semester 5' -> 1, 5)."""
	if not sem_val:
		return 1
	sem_str = str(sem_val).lower().replace("semester", "").strip()
	try:
		return int(sem_str)
	except ValueError:
		return 1

def get_context(context):
	context.base_template_path = "templates/portal_base.html"
	context.title = "Enrolled Courses & Study Notes - EduPortal"
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

	# Fetch logged in student details
	req_student = frappe.form_dict.get("student")
	if req_student and ("System Manager" in roles or "Administrator" in roles):
		student_doc = frappe.db.get_value("Student-form", {"name": req_student}, ["name", "student_name", "department", "semester"], as_dict=True)
	else:
		student_doc = frappe.db.get_value("Student-form", {"email": user}, ["name", "student_name", "department", "semester"], as_dict=True) or frappe.db.get_value("Student-form", {"owner": user}, ["name", "student_name", "department", "semester"], as_dict=True)

	student_dept = student_doc.get("department") if student_doc and student_doc.get("department") else "CSE"
	raw_sem = student_doc.get("semester") if student_doc else "1"
	max_allowed_sem = parse_sem_num(raw_sem)

	# Get semester filter from query parameter if provided
	req_sem_raw = frappe.form_dict.get("semester")
	if req_sem_raw:
		requested_sem_num = parse_sem_num(req_sem_raw)
		if requested_sem_num > max_allowed_sem:
			selected_semester_num = max_allowed_sem
		else:
			selected_semester_num = requested_sem_num
	else:
		selected_semester_num = max_allowed_sem

	selected_semester_title = f"Semester {selected_semester_num}"

	# Lookup department code/name link
	dept_doc_name = frappe.db.get_value("Department", {"department_name": student_dept}, "name") or frappe.db.get_value("Department", {"department_code": student_dept}, "name") or student_dept

	# Query Courses filtered STRICTLY for this student's department & validated semester
	courses = frappe.get_all(
		"Course",
		filters={"department": dept_doc_name, "semester": selected_semester_title},
		fields=["name", "course_name", "course_code", "department", "semester", "duration_years", "description", "credits"],
		order_by="course_name asc"
	)

	# Fallback if specific course codes aren't assigned to exact semester
	if not courses:
		courses = frappe.get_all(
			"Course",
			filters={"department": dept_doc_name},
			fields=["name", "course_name", "course_code", "department", "semester", "duration_years", "description", "credits"],
			order_by="semester desc, course_name asc"
		)

	course_list = []
	for c in courses:
		c["notes"] = frappe.get_all(
			"Course Material",
			filters={"course": c.get("name")},
			fields=["name", "title", "material_type", "file_attachment", "description"],
			order_by="creation desc"
		)
		course_list.append(c)

	available_semesters = [f"Semester {i}" for i in range(max_allowed_sem, 0, -1)]

	context.student = student_doc or {}
	context.student_dept = student_dept
	context.student_sem = selected_semester_title
	context.max_allowed_sem = max_allowed_sem
	context.courses = course_list
	context.available_semesters = available_semesters

	return context
