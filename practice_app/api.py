# Student Management Portal - Core API Endpoints
# Copyright (c) 2026, Dharshan and contributors
# License: MIT. See LICENSE

import json
import frappe
from frappe import _
from typing import Dict, Any, List, Optional

@frappe.whitelist(allow_guest=True, methods=["GET", "POST"])
def custom_logout():
	"""Logs out the current user session and redirects to login page."""
	if hasattr(frappe.local, "login_manager"):
		frappe.local.login_manager.logout()
	frappe.db.commit()
	frappe.respond_as_web_page(
		_("Logged Out"),
		_("You have been successfully logged out of the EDU Portal."),
		indicator_color="green",
		primary_action="/login",
		primary_action_label=_("Go to Login")
	)


@frappe.whitelist(allow_guest=True)
def get_public_stats() -> Dict[str, int]:
	"""Returns aggregate stats for home page display."""
	return {
		"students_count": frappe.db.count("Student-form") or 0,
		"courses_count": frappe.db.count("Course") if frappe.db.exists("DocType", "Course") else 0,
		"departments_count": frappe.db.count("Department") if frappe.db.exists("DocType", "Department") else 0,
		"faculty_count": frappe.db.count("Faculty") if frappe.db.exists("DocType", "Faculty") else 0,
	}

@frappe.whitelist(allow_guest=True)
def submit_contact_form(name: str, email: str, phone: str, subject: str, message: str) -> Dict[str, Any]:
	"""Stores contact form submissions and triggers real-time email notification via Resend API."""
	if not name or not email or not message:
		frappe.throw(_("Name, Email, and Message are required fields."))
	
	doc = frappe.get_doc({
		"doctype": "Communication",
		"communication_type": "Communication",
		"sender": email,
		"sender_full_name": name,
		"subject": subject or "Portal Contact Form Submission",
		"content": f"Phone: {phone}\n\nMessage:\n{message}"
	})
	doc.insert(ignore_permissions=True)

	from practice_app.utils import send_resend_email
	email_subject = f"⚡ Realtime Portal Contact Inquiry: {subject or 'Inquiry'}"
	html = f"""
	<div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #e2e8f0; border-radius: 12px; max-width: 600px;">
		<h2 style="color: #6366f1;">New Portal Contact Submission</h2>
		<p><strong>Name:</strong> {name}</p>
		<p><strong>Sender Email:</strong> {email}</p>
		<p><strong>Phone:</strong> {phone or '-'}</p>
		<p><strong>Subject:</strong> {subject}</p>
		<div style="background: #f8fafc; padding: 15px; border-radius: 8px; border-left: 4px solid #6366f1; margin: 15px 0;">
			<p style="margin: 0;">{message}</p>
		</div>
		<hr>
		<p style="font-size: 12px; color: #64748b;">EduPortal Realtime Email System & Resend API.</p>
	</div>
	"""
	send_resend_email(email_subject, html, [email, "baladharshan1972@gmail.com"])
	
	return {
		"status": "success",
		"message": _("Thank you for contacting us! We will get back to you shortly.")
	}

@frappe.whitelist(allow_guest=True)
def send_test_realtime_email(to_email: Optional[str] = None, subject: Optional[str] = None, message: Optional[str] = None) -> Dict[str, Any]:
	"""Whitelisted API endpoint to send real-time email notifications via Resend API."""
	from practice_app.utils import send_resend_email
	recipient = to_email or "baladharshan1972@gmail.com"
	mail_subject = subject or "⚡ EduPortal Realtime Email Notification"
	body_text = message or "This is a real-time email notification sent via Resend API from EduPortal."
	
	html = f"""
	<div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #e2e8f0; border-radius: 12px; max-width: 600px;">
		<h2 style="color: #6366f1;">⚡ EduPortal Real-Time Email Notification</h2>
		<p>{body_text}</p>
		<p><strong>Recipient Email:</strong> {recipient}</p>
		<p><strong>Timestamp:</strong> {frappe.utils.now()}</p>
		<hr>
		<p style="font-size: 12px; color: #64748b;">Powered by Resend API integration (baladharshan1972@gmail.com).</p>
	</div>
	"""
	res = send_resend_email(mail_subject, html, recipient)
	return res

@frappe.whitelist()
def get_logged_user_student_info() -> Dict[str, Any]:
	"""Retrieves profile details for the currently logged in student."""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Please log in to view portal information."), frappe.PermissionError)
	
	student = frappe.db.get_value(
		"Student-form",
		{"email": user},
		["name", "student_name", "register_number", "department", "semester", "year", "cgpa", "phone_number", "student_photo"],
		as_dict=True
	)
	return student or {}

import base64

@frappe.whitelist(allow_guest=False)
def upload_student_profile_photo(filedata: Optional[str] = None, filename: Optional[str] = None, file_url: Optional[str] = None, student_id: Optional[str] = None) -> Dict[str, Any]:
	"""Saves base64 uploaded file or image URL directly as student_photo on Student-form."""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Please log in to perform this action."), frappe.PermissionError)

	roles = frappe.get_roles(user)
	is_admin = "Administrator" in roles or "System Manager" in roles

	if student_id and is_admin:
		target_student = student_id
	else:
		target_student = frappe.db.get_value("Student-form", {"email": user}, "name") or frappe.db.get_value("Student-form", {"owner": user}, "name")

	if not target_student:
		frappe.throw(_("Student record not found."))

	final_url = file_url
	if filedata:
		if "," in filedata:
			header, content = filedata.split(",", 1)
		else:
			content = filedata

		decoded_content = base64.b64decode(content)
		_file = frappe.get_doc({
			"doctype": "File",
			"file_name": filename or f"student_photo_{target_student}.jpg",
			"attached_to_doctype": "Student-form",
			"attached_to_name": target_student,
			"attached_to_field": "student_photo",
			"content": decoded_content,
			"is_private": 0
		})
		_file.insert(ignore_permissions=True)
		final_url = _file.file_url

	if not final_url:
		frappe.throw(_("No image file or URL provided."))

	frappe.db.set_value("Student-form", target_student, "student_photo", final_url)
	frappe.db.commit()

	return {
		"status": "success",
		"message": _("Profile photo updated successfully!"),
		"file_url": final_url
	}

# ==================================================
# REST APIs FOR STUDENT CRUD OPERATIONS
# ==================================================

@frappe.whitelist()
def get_student(student_id: Optional[str] = None, register_number: Optional[str] = None) -> Dict[str, Any]:
	"""Gets student record by name/ID or register number."""
	filters = {}
	if student_id:
		filters["name"] = student_id
	elif register_number:
		filters["register_number"] = register_number
	else:
		frappe.throw(_("Please specify student_id or register_number."))

	student = frappe.get_doc("Student-form", filters)
	if not student.has_permission("read"):
		frappe.throw(_("Permission denied to read this student record."), frappe.PermissionError)
		
	return student.as_dict()

@frappe.whitelist()
def create_student(data: Any) -> Dict[str, Any]:
	"""Creates a new Student record."""
	if not frappe.has_permission("Student-form", "create"):
		frappe.throw(_("Permission denied to create student records."), frappe.PermissionError)

	if isinstance(data, str):
		data = json.loads(data)

	student = frappe.get_doc({"doctype": "Student-form", **data})
	student.insert()
	frappe.db.commit()
	
	return {
		"status": "success",
		"message": _("Student {0} created successfully.").format(student.student_name),
		"student_id": student.name
	}

@frappe.whitelist()
def update_student(student_id: str, data: Any) -> Dict[str, Any]:
	"""Updates an existing Student record."""
	student = frappe.get_doc("Student-form", student_id)
	if not student.has_permission("write"):
		frappe.throw(_("Permission denied to update this student record."), frappe.PermissionError)

	if isinstance(data, str):
		data = json.loads(data)

	student.update(data)
	student.save()
	frappe.db.commit()

	return {
		"status": "success",
		"message": _("Student {0} updated successfully.").format(student.student_name)
	}

@frappe.whitelist()
def delete_student(student_id: str) -> Dict[str, Any]:
	"""Deletes a Student record."""
	student = frappe.get_doc("Student-form", student_id)
	if not student.has_permission("delete"):
		frappe.throw(_("Permission denied to delete student record."), frappe.PermissionError)

	frappe.delete_doc("Student-form", student_id)
	frappe.db.commit()

	return {
		"status": "success",
		"message": _("Student record deleted successfully.")
	}

# ==================================================
# ATTENDANCE APIs
# ==================================================

@frappe.whitelist()
def get_attendance(student_id: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict[str, Any]]:
	"""Fetches attendance entries for a student."""
	filters = {"student": student_id}
	if from_date and to_date:
		filters["date"] = ["between", [from_date, to_date]]
		
	return frappe.get_all(
		"Attendance",
		filters=filters,
		fields=["name", "date", "subject", "status", "remarks"],
		order_by="date desc"
	)

@frappe.whitelist()
def mark_attendance(student_id: str, date: str, status: str, subject: Optional[str] = None, remarks: Optional[str] = None) -> Dict[str, Any]:
	"""Marks attendance for a student."""
	if not frappe.has_permission("Attendance", "create"):
		frappe.throw(_("Permission denied to mark attendance."), frappe.PermissionError)

	att = frappe.get_doc({
		"doctype": "Attendance",
		"student": student_id,
		"date": date,
		"status": status,
		"subject": subject,
		"remarks": remarks
	})
	att.insert()
	frappe.db.commit()

	return {
		"status": "success",
		"attendance_id": att.name
	}

# ==================================================
# MARKS APIs
# ==================================================

@frappe.whitelist()
def get_marks(student_id: str, exam_type: Optional[str] = None) -> List[Dict[str, Any]]:
	"""Gets mark sheets for a student."""
	filters = {"student": student_id}
	if exam_type:
		filters["exam_type"] = exam_type
		
	return frappe.get_all(
		"Marks",
		filters=filters,
		fields=["subject", "exam_type", "total_marks", "obtained_marks", "grade"],
		order_by="modified desc"
	)

@frappe.whitelist()
def add_marks(student_id: str, subject: str, exam_type: str, obtained_marks: float, total_marks: float = 100.0) -> Dict[str, Any]:
	"""Submits marks entry for a student."""
	if not frappe.has_permission("Marks", "create"):
		frappe.throw(_("Permission denied to add marks."), frappe.PermissionError)

	marks_doc = frappe.get_doc({
		"doctype": "Marks",
		"student": student_id,
		"subject": subject,
		"exam_type": exam_type,
		"obtained_marks": float(obtained_marks),
		"total_marks": float(total_marks)
	})
	marks_doc.insert()
	frappe.db.commit()

	return {
		"status": "success",
		"grade": marks_doc.grade,
		"marks_id": marks_doc.name
	}

# ==================================================
# CERTIFICATES & FEES APIs
# ==================================================

@frappe.whitelist()
def get_certificates(student_id: Optional[str] = None) -> List[Dict[str, Any]]:
	"""Gets issued certificates for a student."""
	user = frappe.session.user
	if user == "Guest":
		return []

	if not student_id:
		student_doc = (
			frappe.db.get_value("Student-form", {"email": user}, ["name", "student_name"], as_dict=True)
			or frappe.db.get_value("Student-form", {"owner": user}, ["name", "student_name"], as_dict=True)
		)
		student_id = student_doc.get("name") if student_doc else None

	if not student_id:
		return []

	return frappe.get_all(
		"Certificate",
		filters={"student": student_id},
		fields=["name", "certificate_type", "issue_date", "status", "certificate_file"],
		order_by="issue_date desc"
	)

@frappe.whitelist()
def submit_certificate_request(certificate_type: str, reason: Optional[str] = None) -> Dict[str, Any]:
	"""Submits a new certificate request for the logged-in student."""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Please log in to submit certificate requests."), frappe.PermissionError)

	if not certificate_type:
		frappe.throw(_("Certificate Type is required."))

	student_doc = (
		frappe.db.get_value("Student-form", {"email": user}, ["name", "student_name"], as_dict=True)
		or frappe.db.get_value("Student-form", {"owner": user}, ["name", "student_name"], as_dict=True)
	)
	if not student_doc:
		frappe.throw(_("Student profile not found. Please complete your profile first."))

	cert = frappe.get_doc({
		"doctype": "Certificate",
		"student": student_doc.get("name"),
		"student_name": student_doc.get("student_name"),
		"certificate_type": certificate_type,
		"issue_date": frappe.utils.today(),
		"status": "Pending"
	})
	cert.insert(ignore_permissions=True)
	frappe.db.commit()

	try:
		from practice_app.utils import send_resend_email
		subject = f"⚡ Realtime Alert: Certificate Request ({certificate_type}) Received"
		html = f"""
		<div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #e2e8f0; border-radius: 12px; max-width: 600px;">
			<h2 style="color: #6366f1;">EduPortal Academic Certificate Request</h2>
			<p><strong>Student:</strong> {student_doc.get('student_name')}</p>
			<p><strong>Certificate Requested:</strong> {certificate_type}</p>
			<p><strong>Reason:</strong> {reason or '-'}</p>
			<p><strong>Status:</strong> <span style="color: #f59e0b; font-weight: bold;">Pending Verification</span></p>
			<hr>
			<p style="font-size: 12px; color: #64748b;">Powered by Resend API Realtime Engine.</p>
		</div>
		"""
		send_resend_email(subject, html, user)
	except Exception:
		pass

	return {
		"status": "success",
		"message": _("Certificate request submitted successfully! Academic office will verify your request."),
		"certificate_id": cert.name
	}

# ==================================================
# ASSIGNMENT SUBMISSION API (REAL DOCTYPE LINKED)
# ==================================================

@frappe.whitelist()
def submit_assignment(assignment_name: str, comments: Optional[str] = None, submitted_file: Optional[str] = None) -> Dict[str, Any]:
	"""Creates an AssignmentSubmission record in the database for the logged-in student.
	   Marks the row as Submitted so the UI can reflect the real status on reload.
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Please log in to submit assignments."), frappe.PermissionError)

	# Validate that the assignment exists
	if not frappe.db.exists("Assignment", assignment_name):
		frappe.throw(_("Assignment not found: {0}").format(assignment_name))

	# Fetch student record linked to this user
	student_doc = (
		frappe.db.get_value("Student-form", {"email": user}, ["name", "student_name"], as_dict=True)
		or frappe.db.get_value("Student-form", {"owner": user}, ["name", "student_name"], as_dict=True)
	)
	if not student_doc:
		frappe.throw(_("Student profile not found for this user. Please complete your profile first."))

	# Check if already submitted
	existing = frappe.db.exists("AssignmentSubmission", {
		"assignment": assignment_name,
		"student": student_doc.get("name")
	})
	if existing:
		return {
			"status": "already_submitted",
			"message": _("You have already submitted this assignment."),
			"submission_id": existing
		}

	# Check file validation
	if submitted_file:
		import os
		allowed_extensions = {".pdf", ".zip", ".txt", ".py", ".java", ".cpp", ".png", ".jpg", ".jpeg", ".docx", ".xlsx"}
		# Strip query params like ?v=...
		clean_url = submitted_file.split("?")[0]
		ext = os.path.splitext(clean_url)[1].lower()
		if ext not in allowed_extensions:
			frappe.throw(_("Invalid file format. Allowed formats: PDF, ZIP, TXT, DOCX, XLSX, Images, or Code files."))

	# Validate late submission
	due_date = frappe.db.get_value("Assignment", assignment_name, "due_date")
	status = "Submitted"
	if due_date:
		from frappe.utils import getdate
		if getdate(frappe.utils.today()) > getdate(due_date):
			status = "Late"

	# Create real submission record
	submission = frappe.get_doc({
		"doctype": "AssignmentSubmission",
		"assignment": assignment_name,
		"student": student_doc.get("name"),
		"student_name": student_doc.get("student_name"),
		"submission_date": frappe.utils.today(),
		"status": status,
		"comments": comments or "",
		"submitted_file": submitted_file or ""
	})
	submission.insert(ignore_permissions=True)
	
	# Link the uploaded file record in MariaDB File manager to this submission name
	if submitted_file:
		frappe.db.set_value("File", {"file_url": submitted_file}, {
			"attached_to_doctype": "AssignmentSubmission",
			"attached_to_name": submission.name
		})

	frappe.db.commit()

	# Trigger Realtime Email Notification via Resend API
	try:
		from practice_app.utils import send_resend_email
		assg_title = frappe.db.get_value("Assignment", assignment_name, "title") or assignment_name
		email_subject = f"⚡ Realtime Alert: Assignment Submitted for {student_doc.get('student_name')}"
		html = f"""
		<div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #e2e8f0; border-radius: 12px; max-width: 600px;">
			<h2 style="color: #6366f1;">EduPortal Realtime Assignment Submission</h2>
			<p><strong>Student:</strong> {student_doc.get('student_name')}</p>
			<p><strong>Assignment:</strong> {assg_title}</p>
			<p><strong>Status:</strong> <span style="color: {'#ef4444' if status == 'Late' else '#10b981'}; font-weight: bold;">{status}</span></p>
			<p><strong>Submitted File:</strong> {submitted_file or 'No file attached'}</p>
			<p><strong>Comments:</strong> {comments or '-'}</p>
			<hr>
			<p style="font-size: 12px; color: #64748b;">Powered by Resend API Realtime Engine.</p>
		</div>
		"""
		send_resend_email(email_subject, html, user)
	except Exception:
		pass

	msg = _("Assignment submitted successfully!")
	if status == "Late":
		msg = _("Assignment submitted successfully! (Submitted past the due date)")

	return {
		"status": "success",
		"message": msg,
		"submission_id": submission.name
	}

@frappe.whitelist()
def get_student_submissions(student_id: Optional[str] = None) -> List[Dict[str, Any]]:
	"""Returns all submission records for a student, used to determine assignment status on the UI."""
	user = frappe.session.user
	if user == "Guest":
		return []

	if not student_id:
		student_rec = (
			frappe.db.get_value("Student-form", {"email": user}, "name")
			or frappe.db.get_value("Student-form", {"owner": user}, "name")
		)
	else:
		student_rec = student_id

	if not student_rec:
		return []

	return frappe.get_all(
		"AssignmentSubmission",
		filters={"student": student_rec},
		fields=["name", "assignment", "status", "submission_date", "marks_obtained", "total_marks", "faculty_feedback"],
		order_by="submission_date desc"
	)

# ==================================================
# LEAVE APPLICATION API (REAL DOCTYPE LINKED)
# ==================================================

@frappe.whitelist()
def submit_leave_application(leave_type: str, from_date: str, to_date: str, reason: str, supporting_document: Optional[str] = None) -> Dict[str, Any]:
	"""Creates a Leave Application record in the Leave Application DocType for the logged-in student."""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Please log in to submit leave applications."), frappe.PermissionError)

	if not leave_type or not from_date or not to_date or not reason:
		frappe.throw(_("Leave Type, From Date, To Date and Reason are all required fields."))

	student_doc = (
		frappe.db.get_value("Student-form", {"email": user}, ["name", "student_name", "department"], as_dict=True)
		or frappe.db.get_value("Student-form", {"owner": user}, ["name", "student_name", "department"], as_dict=True)
	)
	if not student_doc:
		frappe.throw(_("Student profile not found. Please complete your profile first."))

	from frappe.utils import date_diff
	try:
		days = date_diff(to_date, from_date) + 1
	except Exception:
		days = 1

	if days <= 0:
		frappe.throw(_("To Date must be on or after From Date."))

	leave = frappe.get_doc({
		"doctype": "Leave Application",
		"student": student_doc.get("name"),
		"student_name": student_doc.get("student_name"),
		"department": student_doc.get("department"),
		"leave_type": leave_type,
		"from_date": from_date,
		"to_date": to_date,
		"no_of_days": days,
		"reason": reason,
		"supporting_document": supporting_document or "",
		"status": "Pending"
	})
	leave.insert(ignore_permissions=True)
	frappe.db.commit()

	try:
		from practice_app.utils import send_resend_email
		subject = f"⚡ Realtime Alert: Leave Application Submitted by {student_doc.get('student_name')}"
		html = f"""
		<div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #e2e8f0; border-radius: 12px; max-width: 600px;">
			<h2 style="color: #f59e0b;">EduPortal Leave Application Request</h2>
			<p><strong>Student:</strong> {student_doc.get('student_name')}</p>
			<p><strong>Leave Category:</strong> {leave_type}</p>
			<p><strong>Dates:</strong> {from_date} to {to_date} ({days} days)</p>
			<p><strong>Reason:</strong> {reason}</p>
			<p><strong>Status:</strong> <span style="color: #f59e0b; font-weight: bold;">Pending Approval</span></p>
			<hr>
			<p style="font-size: 12px; color: #64748b;">Powered by Resend API Realtime Engine.</p>
		</div>
		"""
		send_resend_email(subject, html, user)
	except Exception:
		pass

	return {
		"status": "success",
		"message": _("Leave application submitted successfully! It is now pending faculty approval."),
		"leave_id": leave.name,
		"no_of_days": days
	}

@frappe.whitelist()
def cancel_leave_application(leave_id: str) -> Dict[str, Any]:
	"""Cancels a pending leave application."""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Please log in."), frappe.PermissionError)

	student_rec = (
		frappe.db.get_value("Student-form", {"email": user}, "name")
		or frappe.db.get_value("Student-form", {"owner": user}, "name")
	)

	leave = frappe.get_doc("Leave Application", leave_id)

	# Only allow cancellation if the leave belongs to this student and is still pending
	if leave.student != student_rec:
		frappe.throw(_("Permission denied: This leave application does not belong to you."), frappe.PermissionError)
	if leave.status != "Pending":
		frappe.throw(_("Only pending leave applications can be cancelled."))

	leave.status = "Cancelled"
	leave.save(ignore_permissions=True)
	frappe.db.commit()

	return {
		"status": "success",
		"message": _("Leave application cancelled successfully.")
	}

# ==================================================
# COURSE FEEDBACK & ONLINE FEE PAYMENT APIs
# ==================================================

@frappe.whitelist()
def submit_course_feedback(course: str, rating: int, comments: Optional[str] = None, teaching_quality: Optional[int] = 5, content_quality: Optional[int] = 5) -> Dict[str, Any]:
	"""Submits student feedback for a course."""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Please log in to submit feedback."), frappe.PermissionError)

	student_doc = (
		frappe.db.get_value("Student-form", {"email": user}, ["name", "student_name", "semester"], as_dict=True)
		or frappe.db.get_value("Student-form", {"owner": user}, ["name", "student_name", "semester"], as_dict=True)
	)
	if not student_doc:
		frappe.throw(_("Student record not found."))

	course_name = frappe.db.get_value("Course", course, "course_name") or course

	fb = frappe.get_doc({
		"doctype": "Course Feedback",
		"student": student_doc.get("name"),
		"student_name": student_doc.get("student_name"),
		"course": course,
		"course_name": course_name,
		"semester": student_doc.get("semester"),
		"rating": int(rating or 5),
		"teaching_quality": int(teaching_quality or 5),
		"content_quality": int(content_quality or 5),
		"comments": comments or "",
		"submitted_on": frappe.utils.today()
	})
	fb.insert(ignore_permissions=True)
	frappe.db.commit()

	return {
		"status": "success",
		"message": _("Thank you! Your course feedback has been submitted successfully."),
		"feedback_id": fb.name
	}

@frappe.whitelist()
def pay_fee_online(fee_id: str, amount: float) -> Dict[str, Any]:
	"""Simulates online fee payment processing and updates Fee record."""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Please log in."), frappe.PermissionError)

	fee = frappe.get_doc("Fee", fee_id)
	paid = float(fee.paid_amount or 0) + float(amount)
	total = float(fee.total_amount or 0)
	outstanding = max(0.0, total - paid)
	status = "Paid" if outstanding <= 0 else "Partially Paid"

	fee.paid_amount = paid
	fee.outstanding_amount = outstanding
	fee.status = status
	fee.save(ignore_permissions=True)
	frappe.db.commit()

	try:
		from practice_app.utils import send_resend_email
		student_name = frappe.db.get_value("Student-form", fee.student, "student_name") or fee.student
		subject = f"⚡ Instant Receipt: Online Fee Payment of ₹{amount} Received"
		html = f"""
		<div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #e2e8f0; border-radius: 12px; max-width: 600px;">
			<h2 style="color: #10b981;">EduPortal Official Fee Payment Receipt</h2>
			<p><strong>Invoice Ref:</strong> {fee.name}</p>
			<p><strong>Student:</strong> {student_name}</p>
			<p><strong>Amount Paid:</strong> ₹{amount:,.2f}</p>
			<p><strong>Total Paid to Date:</strong> ₹{paid:,.2f}</p>
			<p><strong>Remaining Outstanding:</strong> ₹{outstanding:,.2f}</p>
			<p><strong>Status:</strong> <span style="color: {'#10b981' if status == 'Paid' else '#f59e0b'}; font-weight: bold;">{status}</span></p>
			<hr>
			<p style="font-size: 12px; color: #64748b;">Powered by Resend API Realtime Engine.</p>
		</div>
		"""
		send_resend_email(subject, html, user)
	except Exception:
		pass

	return {
		"status": "success",
		"message": _("Payment of ₹{0} successful! Remaining outstanding: ₹{1}").format(amount, outstanding),
		"fee_status": status,
		"outstanding": outstanding
	}

@frappe.whitelist()
def update_student_profile(phone_number: Optional[str] = None, address: Optional[str] = None, city: Optional[str] = None, state: Optional[str] = None, pincode: Optional[str] = None) -> Dict[str, Any]:
	"""Updates contact/address details for logged-in student."""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Please log in."), frappe.PermissionError)

	student_name = (
		frappe.db.get_value("Student-form", {"email": user}, "name")
		or frappe.db.get_value("Student-form", {"owner": user}, "name")
	)
	if not student_name:
		frappe.throw(_("Student record not found."))

	doc = frappe.get_doc("Student-form", student_name)
	if phone_number is not None: doc.phone_number = phone_number
	if address is not None: doc.address = address
	if city is not None: doc.city = city
	if state is not None: doc.state = state
	if pincode is not None: doc.pincode = pincode

	doc.save(ignore_permissions=True)
	frappe.db.commit()

	return {
		"status": "success",
		"message": _("Profile details updated successfully!")
	}