import frappe
import hashlib

base_template_path = "templates/portal_base.html"

def parse_sem_num(sem_val):
	if not sem_val:
		return 1
	sem_str = str(sem_val).lower().replace("semester", "").strip()
	try:
		return int(sem_str)
	except ValueError:
		return 1

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
PERIODS = ["08:00-09:00", "09:00-10:00", "10:00-11:00", "11:00-12:00", "12:00-13:00", "14:00-15:00", "15:00-16:00"]

def get_context(context):
	context.base_template_path = "templates/portal_base.html"
	context.title = "Weekly Timetable - EduPortal"
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

	# Fetch student details
	student_doc = (
		frappe.db.get_value("Student-form", {"email": user}, ["name", "student_name", "department", "semester"], as_dict=True)
		or frappe.db.get_value("Student-form", {"owner": user}, ["name", "student_name", "department", "semester"], as_dict=True)
	)

	student_dept = student_doc.get("department") if student_doc else "CSE"
	raw_sem = student_doc.get("semester") if student_doc else "1"
	sem_num = parse_sem_num(raw_sem)
	current_sem = f"Semester {sem_num}"

	# Fetch courses for this department & semester from Course DocType
	dept_name = (
		frappe.db.get_value("Department", {"department_name": student_dept}, "name")
		or frappe.db.get_value("Department", {"department_code": student_dept}, "name")
		or student_dept
	)

	courses = frappe.get_all(
		"Course",
		filters={"department": dept_name, "semester": current_sem},
		fields=["name", "course_name", "course_code"],
		order_by="course_code asc"
	)

	# Build a structured timetable from courses
	timetable = {}
	for day in DAYS:
		timetable[day] = {}
		for period in PERIODS:
			timetable[day][period] = None

	# Assign each course to a time slot (deterministic based on course name hash)
	for i, course in enumerate(courses):
		day_idx = i % len(DAYS)
		period_idx = i % len(PERIODS)
		day = DAYS[day_idx]
		period = PERIODS[period_idx]
		# Avoid overwriting existing slot
		attempts = 0
		while timetable[day][period] is not None and attempts < len(DAYS) * len(PERIODS):
			period_idx = (period_idx + 1) % len(PERIODS)
			if period_idx == 0:
				day_idx = (day_idx + 1) % len(DAYS)
			day = DAYS[day_idx]
			period = PERIODS[period_idx]
			attempts += 1
		if timetable[day][period] is None:
			timetable[day][period] = {
				"course_code": course.get("course_code") or course.get("name"),
				"course_name": course.get("course_name"),
			}

	context.student = student_doc or {}
	context.student_dept = student_dept
	context.current_sem = current_sem
	context.timetable = timetable
	context.days = DAYS
	context.periods = PERIODS
	context.courses = courses
	return context
