import frappe

def get_context(context):
	context.title = "Student Profile - EduPortal"
	user = frappe.session.user
	
	if user == "Guest":
		frappe.redirect("/login")
	
	roles = frappe.get_roles(user)
	is_admin = "System Manager" in roles or "Administrator" in roles or "Faculty" in roles
	preview_mode = frappe.form_dict.get("preview") or frappe.form_dict.get("view") == "portal" or frappe.form_dict.get("student")

	if is_admin and not preview_mode:
		frappe.redirect("/app")
	
	req_student = frappe.form_dict.get("student")
	
	fields = [
		"name", "student_name", "register_number", "department", "semester", "year",
		"phone_number", "email", "gender", "blood_group", "date_of_birth", "age",
		"cgpa", "address", "city", "state", "country", "pincode",
		"father_name", "mother_name", "parent_phone", "parent_email", "student_photo"
	]

	if req_student and ("System Manager" in frappe.get_roles(user) or "Administrator" in frappe.get_roles(user)):
		student = frappe.db.get_value("Student-form", {"name": req_student}, fields, as_dict=True)
	else:
		student = frappe.db.get_value("Student-form", {"email": user}, fields, as_dict=True) or frappe.db.get_value("Student-form", {"owner": user}, fields, as_dict=True)
	
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
			"address": "Institute Administrative Block",
			"city": "-",
			"state": "-",
			"country": "-",
			"pincode": "-",
			"father_name": "-",
			"mother_name": "-",
			"parent_phone": "-",
			"parent_email": "-",
			"student_photo": user_doc.user_image or "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80",
			"is_admin_preview": True
		}
		
	context.student = student
	return context
