import frappe

def student_saved(doc, method):
    frappe.msgprint("Student was saved!")

def redirect_after_login(login_manager):

    roles = frappe.get_roles(frappe.session.user)

    if "System Manager" in roles or "Employee" in roles:
        frappe.local.response["home_page"] = "/app"

    else:
        frappe.local.response["home_page"] = "/student-dashboard"
