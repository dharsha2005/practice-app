import frappe

base_template_path = "templates/portal_base.html"

def compute_cgpa_from_marks(student_id):
	"""Calculate real CGPA from Marks DocType records for this student."""
	if not student_id:
		return None
	marks_records = frappe.get_all(
		"Marks",
		filters={"student": student_id},
		fields=["obtained_marks", "total_marks", "grade", "semester"]
	)
	if not marks_records:
		return None
	# Calculate CGPA: average of (obtained/total * 10) across all subjects
	valid = [(float(m.get("obtained_marks") or 0), float(m.get("total_marks") or 100))
			 for m in marks_records if m.get("total_marks") and float(m.get("total_marks")) > 0]
	if not valid:
		return None
	cgpa = round(sum((ob / tot) * 10 for ob, tot in valid) / len(valid), 2)
	return cgpa

def get_attendance_summary(student_id):
	"""Get attendance stats from Attendance DocType."""
	if not student_id:
		return {"total": 0, "present": 0, "absent": 0, "on_leave": 0, "percentage": 0.0}
	
	all_records = frappe.get_all(
		"Attendance",
		filters={"student": student_id},
		fields=["status", "date", "subject"]
	)
	total = len(all_records)
	present = sum(1 for r in all_records if r.get("status") == "Present")
	absent = sum(1 for r in all_records if r.get("status") == "Absent")
	on_leave = sum(1 for r in all_records if r.get("status") == "On Leave")
	pct = round((present / total) * 100, 1) if total > 0 else 0.0
	return {"total": total, "present": present, "absent": absent, "on_leave": on_leave, "percentage": pct}

def get_assignment_summary(student_id, student_dept):
	"""Get assignment submission stats from Assignment + AssignmentSubmission DocTypes."""
	if not student_id:
		return {"total": 0, "submitted": 0, "pending": 0, "graded": 0}
	
	dept_filter = {"department": student_dept} if student_dept else {}
	all_assignments = frappe.get_all("Assignment", filters=dept_filter, pluck="name")
	total = len(all_assignments)
	
	if not total:
		return {"total": 0, "submitted": 0, "pending": 0, "graded": 0}
	
	submissions = frappe.get_all(
		"AssignmentSubmission",
		filters={"student": student_id},
		fields=["assignment", "status"]
	)
	submitted_names = {s.get("assignment") for s in submissions}
	graded = sum(1 for s in submissions if s.get("status") == "Graded")
	submitted = len(submissions)
	pending = total - submitted
	
	return {"total": total, "submitted": submitted, "pending": pending, "graded": graded}

def get_context(context):
	context.base_template_path = "templates/portal_base.html"
	context.title = "Student Profile - EduPortal"
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
	
	fields = [
		"name", "student_name", "register_number", "department", "semester", "year",
		"phone_number", "email", "gender", "blood_group", "date_of_birth", "age",
		"cgpa", "address", "city", "state", "country", "pincode",
		"father_name", "mother_name", "parent_phone", "parent_email", "student_photo"
	]

	if req_student and ("System Manager" in roles or "Administrator" in roles):
		student = frappe.db.get_value("Student-form", {"name": req_student}, fields, as_dict=True)
	else:
		student = (
			frappe.db.get_value("Student-form", {"email": user}, fields, as_dict=True)
			or frappe.db.get_value("Student-form", {"owner": user}, fields, as_dict=True)
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
			"phone_number": user_doc.phone or "-",
			"email": user_doc.email,
			"gender": "N/A",
			"blood_group": "N/A",
			"date_of_birth": "-",
			"age": "-",
			"cgpa": 0.0,
			"address": "-",
			"city": "-",
			"state": "-",
			"country": "-",
			"pincode": "-",
			"father_name": "-",
			"mother_name": "-",
			"parent_phone": "-",
			"parent_email": "-",
			"student_photo": user_doc.user_image or "",
			"is_admin_preview": True
		}

	student_id = student.get("name") if student else None
	student_dept = student.get("department") if student else None

	# --- REAL CGPA FROM MARKS DOCTYPE ---
	real_cgpa = compute_cgpa_from_marks(student_id)
	if real_cgpa is not None:
		# Update the student record's CGPA to reflect real calculated value
		student["cgpa"] = real_cgpa
		if student_id:
			try:
				frappe.db.set_value("Student-form", student_id, "cgpa", real_cgpa)
				frappe.db.commit()
			except Exception:
				pass

	# --- REAL MARKS FROM MARKS DOCTYPE ---
	marks_list = []
	if student_id:
		marks_list = frappe.get_all(
			"Marks",
			filters={"student": student_id},
			fields=["name", "subject", "semester", "exam_type", "obtained_marks", "total_marks", "grade"],
			order_by="semester desc, subject asc"
		)

	# --- REAL ATTENDANCE FROM ATTENDANCE DOCTYPE ---
	attendance_summary = get_attendance_summary(student_id)
	attendance_list = []
	if student_id:
		attendance_list = frappe.get_all(
			"Attendance",
			filters={"student": student_id},
			fields=["date", "subject", "status", "remarks"],
			order_by="date desc",
			limit=20
		)

	# --- REAL ASSIGNMENTS FROM ASSIGNMENT + SUBMISSION DOCTYPES ---
	assignment_summary = get_assignment_summary(student_id, student_dept)

	# --- REAL CERTIFICATES FROM CERTIFICATE DOCTYPE ---
	certificates = []
	if student_id:
		certificates = frappe.get_all(
			"Certificate",
			filters={"student": student_id},
			fields=["name", "certificate_type", "issue_date", "status", "certificate_file"]
		)

	# --- REAL FEES FROM FEE DOCTYPE ---
	fees = []
	if student_id:
		fees = frappe.get_all(
			"Fee",
			filters={"student": student_id},
			fields=["name", "posting_date", "total_amount", "paid_amount", "outstanding_amount", "status"],
			order_by="posting_date desc"
		)
	total_fees = sum(f.get("total_amount") or 0 for f in fees)
	paid_fees = sum(f.get("paid_amount") or 0 for f in fees)
	outstanding_fees = sum(f.get("outstanding_amount") or 0 for f in fees)

	context.student = student
	context.marks_list = marks_list
	context.attendance_summary = attendance_summary
	context.attendance_list = attendance_list
	context.assignment_summary = assignment_summary
	context.certificates = certificates
	context.fees = fees
	context.total_fees = total_fees
	context.paid_fees = paid_fees
	context.outstanding_fees = outstanding_fees
	return context
