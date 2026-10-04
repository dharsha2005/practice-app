import frappe

@frappe.whitelist()
def get_student(student_id):
    if not frappe.has_permission("Student-form", "read"):
        frappe.throw("Not permitted")

    if not frappe.db.exists("Student-form", student_id):
        frappe.throw(f"Student {student_id} not found")

    student = frappe.get_doc("Student-form", student_id)

    return {
        "name": student.name,
        "student_name": student.student_name,
        "email": student.email,
        "phone_number": getattr(student, "phone_number", ""),
        "department": getattr(student, "department", ""),
        "address": getattr(student, "address", "")
    }

@frappe.whitelist()
def update_student(student_id, student_name, email, phone_number=None, department=None, address=None, phone=None, course=None):
    if not frappe.has_permission("Student-form", "write"):
        frappe.throw("You don't have permission to update student")

    if not frappe.db.exists("Student-form", student_id):
        frappe.throw(f"Student {student_id} not found")

    student = frappe.get_doc("Student-form", student_id)

    student.student_name = student_name
    student.email = email
    student.phone_number = phone_number or phone
    if department or course:
        student.department = department or course
    if address:
        student.address = address

    student.save(ignore_permissions=True)
    frappe.db.commit()

    return {
        "success": True,
        "message": "Student details updated successfully"
    }