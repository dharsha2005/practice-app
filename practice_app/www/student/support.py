import frappe

base_template_path = "templates/portal_base.html"

def get_context(context):
	context.base_template_path = "templates/portal_base.html"
	context.title = "Student Support - EduPortal"
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

	# Fetch student for sidebar
	student_doc = (
		frappe.db.get_value("Student-form", {"email": user}, ["name", "student_name", "register_number", "department", "student_photo"], as_dict=True)
		or frappe.db.get_value("Student-form", {"owner": user}, ["name", "student_name", "register_number", "department", "student_photo"], as_dict=True)
	)
	context.student = student_doc or {}

	# Support FAQs
	context.faqs = [
		{"question": "How do I apply for a bonafide certificate?", "answer": "Go to Services → Certificates and click 'Request Bonafide Certificate'. Your request will be processed within 3–5 working days."},
		{"question": "How do I apply for a leave of absence?", "answer": "Go to Services → Leave Application, fill the form with your reason and dates, and submit. Faculty will review and approve."},
		{"question": "Where can I see my exam results?", "answer": "Go to Academics → Results to see all your semester-wise marks, grades, and CGPA."},
		{"question": "How is my attendance percentage calculated?", "answer": "Attendance % = (Classes Present / Total Classes) × 100. You must maintain ≥75% to avoid detainment."},
		{"question": "How do I update my profile information?", "answer": "Go to Account → Settings to update your phone number, address, and other personal details."},
		{"question": "Where can I download study materials?", "answer": "Go to Academics → Materials to download lecture notes, lab manuals, syllabi, and reference books for your courses."},
		{"question": "How do I submit an assignment?", "answer": "Go to Academics → Assignments, find your assignment, and click 'Submit'. You can upload your work as a file attachment."},
		{"question": "Who do I contact for fee-related issues?", "answer": "Visit the college accounts office or email accounts@college.edu for any fee payment queries."},
	]

	# Contact details
	context.contacts = [
		{"dept": "Academic Office", "email": "academics@college.edu", "phone": "+91-44-0000-0001", "icon": "bi-mortarboard-fill", "color": "primary"},
		{"dept": "Examination Cell", "email": "exams@college.edu", "phone": "+91-44-0000-0002", "icon": "bi-file-earmark-text-fill", "color": "danger"},
		{"dept": "Accounts & Fees", "email": "accounts@college.edu", "phone": "+91-44-0000-0003", "icon": "bi-credit-card-fill", "color": "success"},
		{"dept": "IT Help Desk", "email": "ithelpdesk@college.edu", "phone": "+91-44-0000-0004", "icon": "bi-headset", "color": "warning"},
		{"dept": "Library", "email": "library@college.edu", "phone": "+91-44-0000-0005", "icon": "bi-book-fill", "color": "info"},
	]

	return context
