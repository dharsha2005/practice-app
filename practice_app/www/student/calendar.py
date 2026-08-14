import frappe
import json
from datetime import datetime

base_template_path = "templates/portal_base.html"

def get_context(context):
	context.base_template_path = "templates/portal_base.html"
	context.title = "Academic Calendar - EduPortal"
	user = frappe.session.user

	if user == "Guest":
		frappe.redirect("/login")
		return context

	roles = frappe.get_roles(user)
	is_admin = "System Manager" in roles or "Administrator" in roles or "Faculty" in roles
	preview_mode = frappe.form_dict.get("preview") or frappe.form_dict.get("view") == "portal"

	if is_admin and not preview_mode:
		frappe.redirect("/app")
		return context

	student_doc = (
		frappe.db.get_value("Student-form", {"email": user}, ["name", "student_name", "register_number", "department", "semester", "student_photo"], as_dict=True)
		or frappe.db.get_value("Student-form", {"owner": user}, ["name", "student_name", "register_number", "department", "semester", "student_photo"], as_dict=True)
	)
	context.student = student_doc or {}
	student_id = student_doc.get("name") if student_doc else None
	student_dept = student_doc.get("department") if student_doc else None

	# Collect events from multiple sources
	events = []

	# 1. Assignment due dates
	dept_filter = {"department": student_dept} if student_dept else {}
	assignments = frappe.get_all(
		"Assignment",
		filters=dept_filter if dept_filter else {},
		fields=["name", "title", "subject", "due_date"],
		order_by="due_date asc"
	)
	for a in assignments:
		if a.get("due_date"):
			due = str(a["due_date"])
			events.append({
				"date": due,
				"title": f"📝 Due: {a['title']}",
				"type": "assignment",
				"color": "#ef4444"
			})

	# 2. Leave application dates
	if student_id:
		leaves = frappe.get_all(
			"Leave Application",
			filters={"student": student_id},
			fields=["leave_type", "from_date", "to_date", "status"],
			order_by="from_date asc"
		)
		for l in leaves:
			if l.get("from_date"):
				color = "#10b981" if l["status"] == "Approved" else "#f59e0b"
				events.append({
					"date": str(l["from_date"]),
					"title": f"🏖️ Leave: {l['leave_type']}",
					"type": "leave",
					"color": color
				})

	# 3. Announcements / exam notifications
	notifs = frappe.get_all(
		"Notification",
		fields=["title", "category", "date"],
		filters=[["date", "is", "set"]],
		order_by="date desc",
		limit=20
	)
	for n in notifs:
		if n.get("date") and n.get("title"):
			date_str = str(n["date"])[:10]
			color = "#6366f1"
			if n.get("category") == "Exam Schedule":
				color = "#dc2626"
			events.append({
				"date": date_str,
				"title": f"📢 {n['title']}",
				"type": "announcement",
				"color": color
			})

	context.calendar_events_json = json.dumps(events)
	context.today_str = datetime.now().strftime("%Y-%m-%d")
	return context
