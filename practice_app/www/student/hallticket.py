import frappe
from datetime import datetime, timedelta

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
	context.title = "Exam Hall Ticket - EduPortal"
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
	fields = ["name", "student_name", "register_number", "department", "semester", "year",
			  "phone_number", "email", "date_of_birth", "student_photo", "cgpa"]

	if req_student and ("System Manager" in roles or "Administrator" in roles):
		student = frappe.db.get_value("Student-form", {"name": req_student}, fields, as_dict=True)
	else:
		student = (
			frappe.db.get_value("Student-form", {"email": user}, fields, as_dict=True)
			or frappe.db.get_value("Student-form", {"owner": user}, ["name", "student_name", "register_number", "department", "semester", "year", "phone_number", "email", "date_of_birth", "student_photo", "cgpa"], as_dict=True)
		)

	if not student:
		user_doc = frappe.get_doc("User", user)
		student = {
			"name": "", "student_name": user_doc.full_name or user,
			"register_number": "ADMIN", "department": "Administration",
			"semester": "N/A", "year": "N/A", "phone_number": "-",
			"email": user_doc.email, "date_of_birth": "-",
			"student_photo": user_doc.user_image or "", "cgpa": 0.0
		}

	student_dept = student.get("department") or "CSE"
	raw_sem = student.get("semester") or "1"
	max_allowed_sem = parse_sem_num(raw_sem)

	# Handle semester filter from query parameter
	req_sem_raw = frappe.form_dict.get("semester")
	if req_sem_raw:
		req_sem_num = parse_sem_num(req_sem_raw)
		selected_sem_num = min(req_sem_num, max_allowed_sem) if max_allowed_sem > 0 else req_sem_num
	else:
		selected_sem_num = max_allowed_sem

	selected_sem_title = f"Semester {selected_sem_num}"

	dept_doc_name = (
		frappe.db.get_value("Department", {"department_name": student_dept}, "name")
		or frappe.db.get_value("Department", {"department_code": student_dept}, "name")
		or student_dept
	)

	# === QUERY EXPLICIT Exam Schedule DocType FIRST ===
	exam_schedule_name = frappe.db.get_value(
		"Exam Schedule",
		{"department": dept_doc_name, "semester": selected_sem_title, "is_published": 1},
		"name"
	)

	exam_title = f"{selected_sem_title} End Semester Examinations"
	academic_year = "2026-2027"
	courses = []

	if exam_schedule_name:
		sch_doc = frappe.get_doc("Exam Schedule", exam_schedule_name)
		exam_title = sch_doc.title or exam_title
		academic_year = sch_doc.academic_year or academic_year

		for item in sch_doc.schedule_items:
			d_val = item.exam_date
			if d_val and hasattr(d_val, 'strftime'):
				formatted_date = d_val.strftime("%d-%b-%Y (%a)")
			else:
				formatted_date = str(d_val)

			courses.append({
				"course_code": item.course_code or item.course,
				"course_name": item.course_name,
				"credits": 3,
				"exam_date": formatted_date,
				"exam_slot": item.exam_time,
				"hall": item.hall_no or "Hall 101"
			})

	# Fallback if no specific Exam Schedule record is published
	if not courses:
		raw_courses = frappe.get_all(
			"Course",
			filters={"department": dept_doc_name, "semester": selected_sem_title},
			fields=["name", "course_name", "course_code", "credits"],
			order_by="course_code asc"
		)
		if not raw_courses:
			raw_courses = frappe.get_all(
				"Course",
				filters={"department": dept_doc_name},
				fields=["name", "course_name", "course_code", "credits"],
				order_by="course_name asc"
			)

		start_date = datetime.now().date() + timedelta(days=5)
		exam_slots = ["09:00 AM - 12:00 PM", "02:00 PM - 05:00 PM"]
		exam_halls = ["Hall A - 101", "Hall B - 202", "Hall C - 301", "Hall D - 401", "Hall E - 102"]

		for i, c in enumerate(raw_courses):
			exam_day = start_date + timedelta(days=i * 2)
			if exam_day.weekday() == 6:
				exam_day += timedelta(days=1)
			courses.append({
				"course_code": c.get("course_code") or c.get("name"),
				"course_name": c.get("course_name"),
				"credits": c.get("credits") or 3,
				"exam_date": exam_day.strftime("%d-%b-%Y (%a)"),
				"exam_slot": exam_slots[i % 2],
				"hall": exam_halls[i % len(exam_halls)]
			})

	available_semesters = [f"Semester {i}" for i in range(max_allowed_sem, 0, -1)]

	context.student = student
	context.courses = courses
	context.selected_sem_title = selected_sem_title
	context.exam_title = exam_title
	context.academic_year = academic_year
	context.issued_date = frappe.utils.today()
	context.available_semesters = available_semesters
	return context
