import frappe

base_template_path = "templates/portal_base.html"

def get_context(context):
	context.base_template_path = "templates/portal_base.html"
	context.title = "Academic Certificates - EduPortal"
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

	# Fetch student record
	student_doc = (
		frappe.db.get_value("Student-form", {"email": user}, ["name", "student_name", "department"], as_dict=True)
		or frappe.db.get_value("Student-form", {"owner": user}, ["name", "student_name", "department"], as_dict=True)
	)

	cert_list = []
	if student_doc:
		student_id = student_doc.get("name")
		student_name = student_doc.get("student_name")
		
		# Fetch certificates where student is ID or student_name
		cert_list = frappe.db.sql("""
			SELECT name, certificate_type, issue_date, status, certificate_file
			FROM `tabCertificate`
			WHERE student = %(student_id)s OR student_name = %(student_name)s OR student = %(student_name)s
			ORDER BY issue_date DESC, creation DESC
		""", {"student_id": student_id, "student_name": student_name}, as_dict=True)

	context.student = student_doc or {}
	context.certificates = cert_list
	context.total_count = len(cert_list)
	context.issued_count = sum(1 for c in cert_list if c.get("status") == "Issued")
	context.pending_count = sum(1 for c in cert_list if c.get("status") == "Pending")
	return context
