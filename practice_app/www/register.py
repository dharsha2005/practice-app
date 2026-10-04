import frappe

def get_context(context):
	context.departments = frappe.get_all("Department", fields=["department_name", "department_code"])

@frappe.whitelist(allow_guest=True)
def submit_student(student_name, register_number, email, department, gender="Other"):
	doc = frappe.new_doc("Student-form")
	doc.student_name = student_name
	doc.register_number = register_number
	doc.email = email
	doc.department = department
	doc.gender = gender
	doc.insert(ignore_permissions=True)
	return {"status": "success", "name": doc.name}
