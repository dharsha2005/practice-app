import frappe
from datetime import datetime, date

base_template_path = "templates/portal_base.html"

def parse_sem_num(sem_val):
	if not sem_val:
		return 1
	sem_str = str(sem_val).lower().replace("semester", "").strip()
	try:
		return int(sem_str)
	except ValueError:
		return 1

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def get_context(context):
	if isinstance(context, dict) and not hasattr(context, "base_template_path"):
		context = frappe._dict(context)
		
	context.base_template_path = "templates/portal_base.html"
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
	student_id = student.get("name")
	student_dept = student.get("department") or "CSE"
	sem_num = parse_sem_num(student.get("semester"))
	current_sem_title = f"Semester {sem_num}"
	context.current_sem_num = sem_num

	# 1. Real CGPA from Marks DocType
	calc_cgpa = None
	if student_id:
		all_m = frappe.get_all("Marks", filters={"student": student_id}, fields=["obtained_marks", "total_marks"])
		if all_m:
			valid_m = [(float(m.get("obtained_marks") or 0), float(m.get("total_marks") or 100)) for m in all_m if m.get("total_marks") and float(m.get("total_marks")) > 0]
			if valid_m:
				calc_cgpa = round(sum(ob / tot for ob, tot in valid_m) / len(valid_m) * 10, 2)
				context.student["cgpa"] = calc_cgpa
				try:
					frappe.db.set_value("Student-form", student_id, "cgpa", calc_cgpa)
					frappe.db.commit()
				except Exception:
					pass
	if calc_cgpa is None:
		context.student["cgpa"] = student.get("cgpa") or 0.0

	# 2. Real Attendance Rate from Attendance DocType
	if student_id:
		total_att = frappe.db.count("Attendance", {"student": student_id})
		present_att = frappe.db.count("Attendance", {"student": student_id, "status": "Present"})
		context.attendance_pct = round((present_att / total_att) * 100, 1) if total_att > 0 else 0.0
	else:
		context.attendance_pct = 0.0

	# 3. Real Enrolled Courses & Credits from Course DocType
	dept_doc_name = (
		frappe.db.get_value("Department", {"department_name": student_dept}, "name")
		or frappe.db.get_value("Department", {"department_code": student_dept}, "name")
		or student_dept
	)
	courses = frappe.get_all(
		"Course",
		filters={"department": dept_doc_name, "semester": current_sem_title},
		fields=["name", "course_name", "course_code", "credits"],
		order_by="course_code asc"
	)
	if not courses:
		courses = frappe.get_all(
			"Course",
			filters={"department": dept_doc_name},
			fields=["name", "course_name", "course_code", "credits"],
			order_by="course_name asc"
		)
	context.enrolled_courses_count = len(courses)
	context.total_credits = sum(int(c.get("credits") or 3) for c in courses)

	# 4. Real Assignments from Assignment and AssignmentSubmission DocTypes
	submission_map = {}
	if student_id:
		submissions = frappe.get_all(
			"AssignmentSubmission",
			filters={"student": student_id},
			fields=["assignment", "status", "marks_obtained", "total_marks"],
		)
		for sub in submissions:
			submission_map[sub.get("assignment")] = sub

	dept_filter = {"department": student_dept} if student_dept else {}
	raw_assignments = frappe.get_all(
		"Assignment",
		filters=dept_filter,
		fields=["name", "title", "subject", "department", "due_date", "total_points"],
		order_by="due_date asc"
	)
	if not raw_assignments and dept_filter:
		raw_assignments = frappe.get_all(
			"Assignment",
			fields=["name", "title", "subject", "department", "due_date", "total_points"],
			order_by="due_date asc"
		)

	today_date = datetime.now().date()
	pending_assignments = []
	all_assigned_list = []

	for item in raw_assignments:
		assg_id = item.get("name")
		due_d = item.get("due_date")
		if due_d and hasattr(due_d, 'date'):
			due_date_val = due_d.date()
		elif isinstance(due_d, str):
			try:
				due_date_val = datetime.strptime(due_d, "%Y-%m-%d").date()
			except Exception:
				due_date_val = None
		else:
			due_date_val = due_d

		if assg_id in submission_map:
			sub = submission_map[assg_id]
			status = sub.get("status") or "Submitted"
			item["status"] = status
			item["badge_class"] = "badge-submitted" if status != "Graded" else "badge-graded"
		else:
			if due_date_val and due_date_val < today_date:
				status = "Late"
				item["badge_class"] = "badge-late"
			else:
				status = "Pending"
				item["badge_class"] = "badge-pending"
				pending_assignments.append(item)
			item["status"] = status
		all_assigned_list.append(item)

	context.pending_assignments_count = len(pending_assignments)
	context.pending_assignments_list = (pending_assignments if pending_assignments else all_assigned_list)[:4]

	# 5. Today's Class Schedule (based on student's actual courses for current department & semester)
	today_name = DAYS[datetime.now().weekday()]
	if today_name == "Sunday":
		today_name = "Monday"
	
	schedule_slots = [
		{"time": "09:00 AM", "type": "Lecture", "badge": "cell-lecture"},
		{"time": "11:00 AM", "type": "Laboratory", "badge": "cell-lab"},
		{"time": "02:00 PM", "type": "Seminar", "badge": "cell-seminar"},
		{"time": "04:00 PM", "type": "Lecture", "badge": "cell-lecture"},
	]
	
	today_schedule = []
	for idx, course in enumerate(courses[:4]):
		slot = schedule_slots[idx % len(schedule_slots)]
		today_schedule.append({
			"time": slot["time"],
			"course_code": course.get("course_code") or course.get("name"),
			"course_name": course.get("course_name"),
			"type": slot["type"],
			"badge": slot["badge"],
			"venue": f"Hall {101 + idx * 3}" if slot["type"] != "Laboratory" else f"Lab {1 + idx}"
		})

	context.today_schedule = today_schedule
	context.today_day_name = today_name
	context.today_formatted = datetime.now().strftime("%A, %d %b")

	# 6. Real Notifications from Notification DocType
	context.notifications = frappe.get_all(
		"Notification",
		fields=["title", "category", "date", "message"],
		order_by="date desc",
		limit=5
	)

	return context
