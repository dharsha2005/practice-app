import frappe

base_template_path = "templates/portal_base.html"

def get_context(context):
	context.base_template_path = "templates/portal_base.html"
	context.title = "Fee Details - EduPortal"
	user = frappe.session.user
	
	if user == "Guest":
		frappe.redirect("/login")

	roles = frappe.get_roles(user)
	is_admin = "System Manager" in roles or "Administrator" in roles or "Faculty" in roles
	preview_mode = frappe.form_dict.get("preview") or frappe.form_dict.get("view") == "portal" or frappe.form_dict.get("student")

	if is_admin and not preview_mode:
		frappe.redirect("/app")

	req_student = frappe.form_dict.get("student")
	
	if req_student and ("System Manager" in frappe.get_roles(user) or "Administrator" in frappe.get_roles(user)):
		student_name = req_student
	else:
		student_name = frappe.db.get_value("Student-form", {"email": user}, "name") or frappe.db.get_value("Student-form", {"owner": user}, "name")
	
	if student_name:
		context.fee_list = frappe.get_all(
			"Fee",
			filters={"student": student_name},
			fields=["name", "posting_date", "due_date", "tuition_fee", "hostel_fee", "other_fee", "total_amount", "paid_amount", "outstanding_amount", "status"],
			order_by="posting_date desc"
		)
	else:
		context.fee_list = []
		
	return context
