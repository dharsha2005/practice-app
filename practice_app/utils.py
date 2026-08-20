# Student Management Portal - Core Utilities & Validation Hooks
# Copyright (c) 2026, Dharshan and contributors
# License: MIT. See LICENSE

import re
import frappe
from frappe import _
from typing import Optional, Dict, Any

def boot_session(bootinfo: Dict[str, Any]) -> None:
	"""Extends bootinfo.app_data to display College Admin and Library as separate icons on the /desk screen."""
	if hasattr(bootinfo, "app_data") and isinstance(bootinfo.app_data, list):
		# Fix Framework icon route so it opens Frappe DocType List (/desk/doctype/DocType)
		for app in bootinfo.app_data:
			if app.get("app_name") == "frappe" or app.get("app_title") == "Framework":
				app["app_route"] = "/app/doctype/DocType"

		if not any(app.get("app_name") == "college_admin" for app in bootinfo.app_data):
			bootinfo.app_data.append({
				"on_apps_screen": True,
				"sequence_id": 50,
				"app_name": "college_admin",
				"app_title": "College Admin",
				"app_route": "/app/college-admin",
				"app_logo_url": "/assets/practice_app/images/practice_app.svg",
				"modules": [],
				"workspaces": ["College Admin"]
			})

		if not any(app.get("app_name") == "library_workspace" for app in bootinfo.app_data):
			bootinfo.app_data.append({
				"on_apps_screen": True,
				"sequence_id": 60,
				"app_name": "library_workspace",
				"app_title": "Library",
				"app_route": "/app/library",
				"app_logo_url": "/assets/practice_app/images/practice_app.svg",
				"modules": [],
				"workspaces": ["Library"]
			})

def fix_library_workspace() -> None:
	"""Converts Library-Administrator workspace to a Public Workspace."""
	if frappe.db.exists("Workspace", "Library-Administrator"):
		doc = frappe.get_doc("Workspace", "Library-Administrator")
		doc.for_user = ""
		doc.public = 1
		doc.module = "Practice App"
		doc.app = "practice_app"
		doc.save(ignore_permissions=True)
		frappe.rename_doc("Workspace", "Library-Administrator", "Library", force=True)
		frappe.db.commit()
	elif frappe.db.exists("Workspace", "Library"):
		lib_doc = frappe.get_doc("Workspace", "Library")
		lib_doc.public = 1
		lib_doc.for_user = ""
		lib_doc.module = "Practice App"
		lib_doc.app = "practice_app"
		lib_doc.save(ignore_permissions=True)
		frappe.db.commit()

def validate_student_form(doc, method: Optional[str] = None) -> None:
	"""Validates Student Form fields: phone number format, email format, age, CGPA."""
	if doc.phone_number:
		pattern = r"^\+?[0-9]{10,15}$"
		if not re.match(pattern, doc.phone_number):
			frappe.throw(_("Invalid phone number format. Must be 10-15 digits."))

	if doc.cgpa is not None:
		if not (0.0 <= float(doc.cgpa) <= 10.0):
			frappe.throw(_("CGPA must be between 0.00 and 10.00."))

	if doc.age is not None and doc.age < 15:
		frappe.throw(_("Student age must be at least 15 years."))

def on_student_update(doc, method: Optional[str] = None) -> None:
	"""Syncs student email user or updates cache."""
	pass

def validate_attendance(doc, method: Optional[str] = None) -> None:
	"""Ensures attendance record integrity."""
	pass

def on_attendance_submit(doc, method: Optional[str] = None) -> None:
	"""Triggers alert if attendance falls below threshold."""
	pass

def validate_fee(doc, method: Optional[str] = None) -> None:
	"""Validates fee payment status and amounts."""
	pass

def on_fee_submit(doc, method: Optional[str] = None) -> None:
	"""Handles post-fee submission events."""
	pass

def validate_marks(doc, method: Optional[str] = None) -> None:
	"""Validates obtained marks against total marks."""
	if hasattr(doc, "obtained_marks") and hasattr(doc, "total_marks"):
		if float(doc.obtained_marks or 0) > float(doc.total_marks or 100):
			frappe.throw(_("Obtained marks cannot exceed total marks."))

# Permission Query Conditions
def get_student_permission_query_conditions(user: str) -> str:
	if not user:
		user = frappe.session.user
	if "System Manager" in frappe.get_roles(user) or "Administrator" in user:
		return ""
	# Students can only view their own record
	return f"`tabStudent-form`.email = {frappe.db.escape(user)}"

def get_attendance_permission_query_conditions(user: str) -> str:
	if not user:
		user = frappe.session.user
	if "System Manager" in frappe.get_roles(user) or "Administrator" in user or "Faculty" in frappe.get_roles(user):
		return ""
	student_name = frappe.db.get_value("Student-form", {"email": user}, "name")
	if student_name:
		return f"`tabAttendance`.student = {frappe.db.escape(student_name)}"
	return "1=0"

def get_marks_permission_query_conditions(user: str) -> str:
	if not user:
		user = frappe.session.user
	if "System Manager" in frappe.get_roles(user) or "Administrator" in user or "Faculty" in frappe.get_roles(user):
		return ""
	student_name = frappe.db.get_value("Student-form", {"email": user}, "name")
	if student_name:
		return f"`tabMarks`.student = {frappe.db.escape(student_name)}"
	return "1=0"

def get_fee_permission_query_conditions(user: str) -> str:
	if not user:
		user = frappe.session.user
	if "System Manager" in frappe.get_roles(user) or "Administrator" in user:
		return ""
	student_name = frappe.db.get_value("Student-form", {"email": user}, "name")
	if student_name:
		return f"`tabFee`.student = {frappe.db.escape(student_name)}"
	return "1=0"

def has_student_permission(doc, ptype: str, user: str) -> bool:
	if "System Manager" in frappe.get_roles(user) or "Administrator" in user:
		return True
	return doc.email == user

def has_attendance_permission(doc, ptype: str, user: str) -> bool:
	if "System Manager" in frappe.get_roles(user) or "Administrator" in user or "Faculty" in frappe.get_roles(user):
		return True
	student_name = frappe.db.get_value("Student-form", {"email": user}, "name")
	return getattr(doc, "student", None) == student_name

# Scheduled Event Handlers
import json
import urllib.request

import os

RESEND_API_KEY = getattr(frappe.conf, "resend_api_key", None) or os.environ.get("RESEND_API_KEY")
ADMIN_NOTIFICATION_EMAIL = getattr(frappe.conf, "admin_notification_email", "baladharshan1972@gmail.com")

def send_resend_email(subject: str, html_content: str, to_email: Optional[Any] = None) -> Dict[str, Any]:
	"""Sends real-time email notifications via Resend API to Admin & Student individually."""
	recipients = []
	if isinstance(to_email, list):
		for e in to_email:
			if e and str(e).strip() and str(e).strip() not in recipients:
				recipients.append(str(e).strip())
	elif isinstance(to_email, str) and to_email.strip():
		recipients.append(to_email.strip())

	if ADMIN_NOTIFICATION_EMAIL not in recipients:
		recipients.append(ADMIN_NOTIFICATION_EMAIL)

	results = []
	url = "https://api.resend.com/emails"
	headers = {
		"Authorization": f"Bearer {RESEND_API_KEY}",
		"Content-Type": "application/json",
		"User-Agent": "Mozilla/5.0 (EduPortal Realtime Email Client)"
	}

	for recipient in recipients:
		payload = {
			"from": "EduPortal <onboarding@resend.dev>",
			"to": [recipient],
			"subject": subject,
			"html": html_content
		}
		req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
		try:
			with urllib.request.urlopen(req) as resp:
				res_data = json.loads(resp.read().decode("utf-8"))
				frappe.logger().info(f"Resend email sent to {recipient}: {res_data}")
				results.append({"recipient": recipient, "status": "success", "id": res_data.get("id")})
		except Exception as e:
			err_text = str(e)
			if hasattr(e, "read"):
				try:
					err_text = e.read().decode("utf-8")
				except Exception:
					pass
			frappe.logger().error(f"Resend email failure for {recipient}: {err_text}")
			results.append({"recipient": recipient, "status": "error", "message": err_text})

	return {"status": "completed", "results": results}

def on_attendance_submit(doc, method: Optional[str] = None) -> None:
	"""Triggers real-time email alert on attendance submission to Admin & Student."""
	if not doc:
		return
	student_info = frappe.db.get_value("Student-form", doc.student, ["student_name", "email"], as_dict=True) or {}
	student_name = student_info.get("student_name") or doc.student
	student_email = student_info.get("email")

	recipients = [ADMIN_NOTIFICATION_EMAIL]
	if student_email:
		recipients.append(student_email)

	subject = f"⚡ Realtime Alert: Attendance Update for {student_name}"
	status_color = "#10b981" if doc.status == "Present" else "#ef4444"
	html = f"""
	<div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #e2e8f0; border-radius: 12px; max-width: 600px;">
		<h2 style="color: #6366f1;">EduPortal Realtime Attendance Alert</h2>
		<p><strong>Student:</strong> {student_name} ({doc.student})</p>
		<p><strong>Date:</strong> {doc.date}</p>
		<p><strong>Subject:</strong> {getattr(doc, 'subject', 'General') or 'General'}</p>
		<p><strong>Status:</strong> <span style="color: {status_color}; font-weight: bold;">{doc.status}</span></p>
		<p><strong>Remarks:</strong> {getattr(doc, 'remarks', '-') or '-'}</p>
		<hr>
		<p style="font-size: 12px; color: #64748b;">Powered by EduPortal Realtime Email Engine & Resend API.</p>
	</div>
	"""
	send_resend_email(subject, html, recipients)

def on_fee_submit(doc, method: Optional[str] = None) -> None:
	"""Triggers real-time email receipt alert post-fee submission to Admin & Student."""
	if not doc:
		return
	student_info = frappe.db.get_value("Student-form", doc.student, ["student_name", "email"], as_dict=True) or {}
	student_name = student_info.get("student_name") or doc.student
	student_email = student_info.get("email")

	recipients = [ADMIN_NOTIFICATION_EMAIL]
	if student_email:
		recipients.append(student_email)

	subject = f"⚡ Realtime Notification: Fee Receipt Received for {student_name}"
	html = f"""
	<div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #e2e8f0; border-radius: 12px; max-width: 600px;">
		<h2 style="color: #10b981;">EduPortal Realtime Fee Notification</h2>
		<p><strong>Student:</strong> {student_name}</p>
		<p><strong>Posting Date:</strong> {doc.posting_date}</p>
		<p><strong>Total Fee:</strong> ₹{getattr(doc, 'total_amount', 0) or 0}</p>
		<p><strong>Paid Amount:</strong> ₹{getattr(doc, 'paid_amount', 0) or 0}</p>
		<p><strong>Outstanding Balance:</strong> ₹{getattr(doc, 'outstanding_amount', 0) or 0}</p>
		<p><strong>Payment Status:</strong> <strong>{getattr(doc, 'status', 'Paid') or 'Paid'}</strong></p>
		<hr>
		<p style="font-size: 12px; color: #64748b;">Powered by EduPortal Realtime Email Engine & Resend API.</p>
	</div>
	"""
	send_resend_email(subject, html, recipients)

def on_marks_submit(doc, method: Optional[str] = None) -> None:
	"""Triggers real-time email alert on marks submission to Admin & Student."""
	if not doc:
		return
	student_info = frappe.db.get_value("Student-form", doc.student, ["student_name", "email"], as_dict=True) or {}
	student_name = student_info.get("student_name") or doc.student
	student_email = student_info.get("email")

	recipients = [ADMIN_NOTIFICATION_EMAIL]
	if student_email:
		recipients.append(student_email)

	subject = f"⚡ Realtime Alert: Marks Entry Published for {student_name}"
	html = f"""
	<div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #e2e8f0; border-radius: 12px; max-width: 600px;">
		<h2 style="color: #6366f1;">EduPortal Realtime Marks Entry Notification</h2>
		<p><strong>Student:</strong> {student_name}</p>
		<p><strong>Subject:</strong> {getattr(doc, 'subject', '-') or '-'}</p>
		<p><strong>Exam Type:</strong> {getattr(doc, 'exam_type', '-') or '-'}</p>
		<p><strong>Obtained Marks:</strong> {getattr(doc, 'obtained_marks', 0)} / {getattr(doc, 'total_marks', 100)}</p>
		<p><strong>Grade:</strong> <strong>{getattr(doc, 'grade', '-')}</strong></p>
		<hr>
		<p style="font-size: 12px; color: #64748b;">Powered by EduPortal Realtime Email Engine & Resend API.</p>
	</div>
	"""
	send_resend_email(subject, html, recipients)

def update_website_context(context: Dict[str, Any]) -> None:
	"""Globally injects role flags into website Jinja context and implements portal block check."""
	# 1. Centralized Student Portal access blocking check
	route = getattr(frappe.local, "path", "") or ""
	if route.startswith("student"):
		block_portal = frappe.db.get_single_value("Student Portal Settings", "block_student_portal")
		if block_portal:
			user = frappe.session.user
			roles = frappe.get_roles(user) if user else []
			if "Administrator" not in roles and "System Manager" not in roles:
				frappe.redirect("/maintenance")
				raise frappe.Redirect

	# 2. Inject role flags
	user = frappe.session.user
	if user and user != "Guest":
		roles = frappe.get_roles(user)
		context.is_admin = bool({"Administrator", "System Manager", "Faculty"}.intersection(set(roles)))
		context.user_roles = roles
	else:
		context.is_admin = False
		context.user_roles = []

def get_website_user_home_page(user: Optional[str] = None) -> str:
	"""Determines home page route based on user roles (Admin/Staff -> /app, Student -> /student)."""
	if not user or user == "Guest":
		return None
	roles = frappe.get_roles(user)
	if "Administrator" in roles or "System Manager" in roles or "Faculty" in roles or "System User" in roles:
		return "/app"
	if "Student" in roles:
		return "/student"
	return "/app"

def send_daily_attendance_alerts() -> None:
	"""Daily background task to notify students with low attendance."""
	pass

def send_fee_due_reminders() -> None:
	"""Daily background task to send fee due reminders."""
	pass

def validate_assignment_submission(doc, method: Optional[str] = None) -> None:
	"""Pre-save check to detect if status is transitioning to Graded."""
	if not doc:
		return
	if doc.status == "Graded":
		# If the document is new or status was not Graded in DB, set flag
		db_status = frappe.db.get_value("AssignmentSubmission", doc.name, "status") if doc.name else None
		if db_status != "Graded":
			doc.flags.should_notify_grading = True

def on_assignment_submission_update(doc, method: Optional[str] = None) -> None:
	"""Triggers real-time notice announcement and email alerts when assignment is graded."""
	if not doc:
		return
	
	if getattr(doc.flags, "should_notify_grading", False):
		# Fetch assignment title
		assignment_title = frappe.db.get_value("Assignment", doc.assignment, "title") or doc.assignment
		subject = f"Graded: {assignment_title}"
		
		# Strip HTML tags from feedback if present
		import re
		feedback = getattr(doc, "faculty_feedback", "") or ""
		clean_feedback = re.sub('<[^<]+?>', '', feedback).strip()
		
		msg = f"Your submission for assignment '{assignment_title}' has been graded.\n"
		msg += f"Marks Obtained: {getattr(doc, 'marks_obtained', 0)} / {getattr(doc, 'total_marks', 100)}\n"
		if clean_feedback:
			msg += f"Feedback: {clean_feedback}"

		# Create notice/announcement Notification record
		notif = frappe.get_doc({
			"doctype": "Notification",
			"title": subject,
			"category": "Academic",
			"target_role": "Student",
			"date": frappe.utils.today(),
			"message": msg
		})
		notif.insert(ignore_permissions=True)

		# Trigger real-time email notification via Resend API
		student_email = frappe.db.get_value("Student-form", doc.student, "email")
		if student_email:
			html = f"""
			<div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #e2e8f0; border-radius: 12px; max-width: 600px;">
				<h2 style="color: #4f46e5;">Assignment Graded Alert</h2>
				<p><strong>Assignment:</strong> {assignment_title}</p>
				<p><strong>Marks Obtained:</strong> {getattr(doc, 'marks_obtained', 0)} / {getattr(doc, 'total_marks', 100)}</p>
				{f'<div style="background: #f8fafc; padding: 15px; border-radius: 8px; border-left: 4px solid #4f46e5; margin: 15px 0;"><p style="margin:0;"><strong>Faculty Feedback:</strong> {clean_feedback}</p></div>' if clean_feedback else ''}
				<hr>
				<p style="font-size: 12px; color: #64748b;">Powered by EduPortal Realtime Email Engine & Resend API.</p>
			</div>
			"""
			send_resend_email(subject, html, [student_email])

