import frappe
def get_context(context):
    user = frappe.session.user
    student = frappe.db.get_value("Student-form", {"email": user}, ["student_name","email","gender", "register_number","department"], as_dict=True)
    if not student:
        student = {}
    context.student = student