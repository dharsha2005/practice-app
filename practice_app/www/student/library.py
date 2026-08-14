import frappe

base_template_path = "templates/portal_base.html"

def get_context(context):
	context.base_template_path = "templates/portal_base.html"
	context.title = "Library Books & Issued Status - EduPortal"
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

	student_doc = (
		frappe.db.get_value("Student-form", {"email": user}, ["name", "student_name", "register_number", "department", "student_photo"], as_dict=True)
		or frappe.db.get_value("Student-form", {"owner": user}, ["name", "student_name", "register_number", "department", "student_photo"], as_dict=True)
	)
	context.student = student_doc or {}
	student_id = student_doc.get("name") if student_doc else None

	books = []
	if student_id:
		books = frappe.get_all(
			"Library Record",
			filters={"student": student_id},
			fields=["name", "book_title", "author", "isbn", "issue_date", "due_date", "return_date", "status", "fine_amount"],
			order_by="issue_date desc"
		)

	context.books = books
	context.total_issued = sum(1 for b in books if b.get("status") == "Issued")
	context.total_overdue = sum(1 for b in books if b.get("status") == "Overdue")
	context.total_returned = sum(1 for b in books if b.get("status") == "Returned")
	context.total_fine = sum(float(b.get("fine_amount") or 0) for b in books)
	return context
