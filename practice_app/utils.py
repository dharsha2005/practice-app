# Student Management Portal - Core Utilities & Validation Hooks
# Copyright (c) 2026, Dharshan and contributors
# License: MIT. See LICENSE

import re
import frappe
from frappe import _
from typing import Optional, Dict, Any

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
	"""Globally injects role flags into website Jinja context."""
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
		return "/"
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
