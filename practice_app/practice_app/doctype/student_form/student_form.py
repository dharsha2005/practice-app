import frappe
from frappe.model.document import Document


class Studentform(Document):

    def after_insert(self):
        
        if not self.email:
            frappe.throw("Email is required")

        if frappe.db.exists("User", self.email):
            self.db_set("user", self.email)
            return

        user = frappe.get_doc({
            "doctype": "User",
            "email": self.email,
            "first_name": self.student_name,
            "enabled": 1,
            "user_type": "Website User"
        })

        user.insert(ignore_permissions=True)

        self.db_set("user", user.name)

StudentForm = Studentform