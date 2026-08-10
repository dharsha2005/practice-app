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
	
	if req_student and ("System Manager" in roles or "Administrator" in roles):
		student_doc = frappe.db.get_value("Student-form", {"name": req_student}, ["name", "student_name", "department", "semester", "cgpa"], as_dict=True)
	else:
		student_doc = (
			frappe.db.get_value("Student-form", {"email": user}, ["name", "student_name", "department", "semester", "cgpa"], as_dict=True)
			or frappe.db.get_value("Student-form", {"owner": user}, ["name", "student_name", "department", "semester", "cgpa"], as_dict=True)
		)
	
	student_id = student_doc.get("name") if student_doc else None
	raw_sem = student_doc.get("semester") if student_doc else "1"
	max_allowed_sem = parse_sem_num(raw_sem)

	# === FETCH MARKS STRICTLY FROM Marks DocType ===
	# Only show marks for semesters <= student's current semester (REAL-TIME boundary)
	raw_marks = []
	if student_id:
		raw_marks = frappe.get_all(
			"Marks",
			filters={"student": student_id},
			fields=["name", "semester", "subject", "exam_type", "total_marks", "obtained_marks", "grade"],
			order_by="semester asc, subject asc"
		)

	# Group marks by semester, strictly filtering out future semesters
	semesters_data = {}
	for m in raw_marks:
		sem_str = m.get("semester") or "Semester 1"
		s_num = parse_sem_num(sem_str)
		# STRICT: only include semesters the student has completed or is currently in
		if s_num > max_allowed_sem:
			continue
		key = f"Semester {s_num}"
		if key not in semesters_data:
			semesters_data[key] = {"sem_num": s_num, "subjects": []}
		semesters_data[key]["subjects"].append({
			"subject": m.get("subject"),
			"exam_type": m.get("exam_type") or "Regular",
			"total_marks": m.get("total_marks") or 100,
			"obtained_marks": m.get("obtained_marks") or 0,
			"grade": m.get("grade") or "-"
		})

	# Compute SGPA per semester from actual marks
	for sem_key, sem_val in semesters_data.items():
		subjs = sem_val["subjects"]
		if subjs:
			total_obtained = sum(float(s["obtained_marks"]) for s in subjs)
			total_possible = sum(float(s["total_marks"]) for s in subjs)
			sgpa = round((total_obtained / total_possible) * 10, 2) if total_possible > 0 else 0.0
			# Credits: count of subjects * 3 (standard credit assumption)
			credits = len(subjs) * 3
		else:
			sgpa = 0.0
			credits = 0
		sem_val["sgpa"] = sgpa
		sem_val["credits"] = credits

	# Sort semesters in ascending order
	allowed_semesters = dict(
		sorted(semesters_data.items(), key=lambda x: x[1]["sem_num"])
	)

	# Compute overall CGPA from all marks
	all_obtained = []
	all_total = []
	for sem_val in allowed_semesters.values():
		for s in sem_val["subjects"]:
			all_obtained.append(float(s["obtained_marks"]))
			all_total.append(float(s["total_marks"]))

	if all_obtained and all_total:
		cgpa = round((sum(all_obtained) / sum(all_total)) * 10, 2)
	else:
		cgpa = student_doc.get("cgpa") or 0.0

	# Update CGPA in Student-form if we computed it from real data
	if student_id and all_obtained:
		try:
			frappe.db.set_value("Student-form", student_id, "cgpa", cgpa)
			frappe.db.commit()
		except Exception:
			pass

	context.student = student_doc or {}
	context.max_allowed_sem = max_allowed_sem
	context.current_sem_title = f"Semester {max_allowed_sem}"
	context.semesters = allowed_semesters
	context.cgpa = cgpa
	context.has_marks = bool(allowed_semesters)
	return context
