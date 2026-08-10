import frappe

def get_context(context):
	context.title = "EduPortal - Student Management Portal"
	
	context.stats = {
		"students": frappe.db.count("Student-form") or 0,
		"courses": frappe.db.count("Course") or 0,
		"departments": frappe.db.count("Department") or 0,
		"placement_rate": 96
	}

	context.featured_courses = frappe.get_all(
		"Course",
		fields=["name", "course_name", "department", "duration_years", "description", "credits"],
		order_by="creation desc",
		limit=4
	)

	context.upcoming_events = frappe.get_all(
		"Notification",
		fields=["title", "category", "date", "message"],
		order_by="date desc",
		limit=3
	)

	return context
