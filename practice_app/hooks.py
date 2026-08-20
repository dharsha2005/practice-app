# Student Management Portal - Frappe v17 Hooks
# Copyright (c) 2026, Dharshan and contributors
# License: MIT. See LICENSE

app_name = "practice_app"
app_title = "Student Management Portal"
app_publisher = "Dharshan"
app_description = "Production-ready Student Management Portal built on Frappe Framework v17"
app_email = "admin@studentportal.local"
app_license = "mit"
app_icon = "/assets/practice_app/images/practice_app.svg"
app_logo_url = "/assets/practice_app/images/practice_app.svg"
app_include_icons = [
	"/assets/practice_app/images/practice_app_icons.svg"
]
add_to_apps_screen = [
	{
		"name": "practice_app",
		"title": "Student Management Portal",
		"logo": "/assets/practice_app/images/practice_app.svg",
		"route": "/app/student-portal"
	},
	{
		"name": "college_admin",
		"title": "College Admin",
		"logo": "/assets/practice_app/images/practice_app.svg",
		"route": "/app/college-admin"
	}
]
# Session Boot Hooks
boot_session = [
	"practice_app.utils.boot_session"
]

# JSON Request Body handling per Frappe v17 standard
use_json_request_body = True
export_python_type_annotations = True
require_type_annotated_api_methods = True

# Web & Desk Assets
app_include_css = "/assets/practice_app/css/student_portal.css"
app_include_js = "/assets/practice_app/js/student_portal.js"

web_include_css = [
	"https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css",
	"https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css",
	"/assets/practice_app/css/student_portal.css"
]

web_include_js = [
	"https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js",
	"/assets/practice_app/js/student_portal.js"
]

# Role-Based Home Pages & Authentication Redirection
role_home_page = {
	"Student": "/student",
	"Faculty": "/app",
	"System Manager": "/app",
	"Administrator": "/app"
}

get_website_user_home_page = "practice_app.utils.get_website_user_home_page"
website_user_home = "practice_app.utils.get_website_user_home_page"
update_website_context = "practice_app.utils.update_website_context"

# Explicit URL Routing Rules
website_route_rules = [
	{"from_route": "/login", "to_route": "student/login"},
	{"from_route": "/portal/login", "to_route": "student/login"},
	{"from_route": "/student", "to_route": "student/index"},
	{"from_route": "/student/profile", "to_route": "student/profile"},
	{"from_route": "/student/attendance", "to_route": "student/attendance"},
	{"from_route": "/student/marks", "to_route": "student/marks"},
	{"from_route": "/student/fees", "to_route": "student/fees"},
	{"from_route": "/student/notifications", "to_route": "student/notifications"},
	{"from_route": "/student/courses", "to_route": "student/courses"},
	{"from_route": "/student/timetable", "to_route": "student/timetable"},
	{"from_route": "/student/assignments", "to_route": "student/assignments"},
	{"from_route": "/student/materials", "to_route": "student/materials"},
	{"from_route": "/student/announcements", "to_route": "student/announcements"},
	{"from_route": "/student/leave", "to_route": "student/leave"},
	{"from_route": "/student/certificates", "to_route": "student/certificates"},
	{"from_route": "/student/settings", "to_route": "student/settings"},
	{"from_route": "/student/admission", "to_route": "student/admission"}
]


# Document Event Hooks for Validations & Workflow Logic
doc_events = {
	"Student-form": {
		"validate": "practice_app.utils.validate_student_form",
		"on_update": "practice_app.utils.on_student_update"
	},
	"Attendance": {
		"validate": "practice_app.utils.validate_attendance",
		"on_update": "practice_app.utils.on_attendance_submit",
		"after_insert": "practice_app.utils.on_attendance_submit"
	},
	"Fee": {
		"validate": "practice_app.utils.validate_fee",
		"on_update": "practice_app.utils.on_fee_submit",
		"after_insert": "practice_app.utils.on_fee_submit"
	},
	"Marks": {
		"validate": "practice_app.utils.validate_marks",
		"on_update": "practice_app.utils.on_marks_submit",
		"after_insert": "practice_app.utils.on_marks_submit"
	},
	"AssignmentSubmission": {
		"validate": "practice_app.utils.validate_assignment_submission",
		"on_update": "practice_app.utils.on_assignment_submission_update"
	}
}

# Scheduled Tasks for Background Notifications & Cleanup
scheduler_events = {
	"daily": [
		"practice_app.utils.send_daily_attendance_alerts",
		"practice_app.utils.send_fee_due_reminders"
	]
}

# Role Based Permission Queries
permission_query_conditions = {
	"Student-form": "practice_app.utils.get_student_permission_query_conditions",
	"Attendance": "practice_app.utils.get_attendance_permission_query_conditions",
	"Marks": "practice_app.utils.get_marks_permission_query_conditions",
	"Fee": "practice_app.utils.get_fee_permission_query_conditions"
}

has_permission = {
	"Student-form": "practice_app.utils.has_student_permission",
	"Attendance": "practice_app.utils.has_attendance_permission"
}
app_include_js = "custom_desk.bundle.js"