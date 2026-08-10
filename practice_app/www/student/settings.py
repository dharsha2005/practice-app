import frappe

base_template_path = "templates/portal_base.html"

def get_context(context):
	context.base_template_path = "templates/portal_base.html"
	context.title = "Account Settings - EduPortal"
	user = frappe.session.user
	
	if user == "Guest":
		frappe.redirect("/login")

	roles = frappe.get_roles(user)
	is_admin = "System Manager" in roles or "Administrator" in roles or "Faculty" in roles
	preview_mode = frappe.form_dict.get("preview") or frappe.form_dict.get("view") == "portal" or frappe.form_dict.get("student")

	if is_admin and not preview_mode:
		frappe.redirect("/app")

	# Load full student profile from Student-form DocType
	fields = [
		"name", "student_name", "register_number", "department", "semester", "year",
		"phone_number", "email", "gender", "blood_group", "date_of_birth",
		"cgpa", "address", "city", "state", "country", "pincode",
		"father_name", "mother_name", "parent_phone", "parent_email", "student_photo"
	]

	student = (
		frappe.db.get_value("Student-form", {"email": user}, fields, as_dict=True)
		or frappe.db.get_value("Student-form", {"owner": user}, fields, as_dict=True)
	)

	if not student:
		user_doc = frappe.get_doc("User", user)
		student = {
			"name": "",
			"student_name": user_doc.full_name or user,
			"email": user_doc.email,
			"phone_number": user_doc.phone or "",
			"department": "Administration",
			"semester": "N/A",
			"register_number": "ADMIN",
		}

	# Fetch User record for linked email/password settings
	user_record = frappe.db.get_value(
		"User",
		{"name": user},
		["name", "email", "full_name", "mobile_no", "enabled"],
		as_dict=True
	)

	context.student = student
	context.user_record = user_record or {}
	return context
