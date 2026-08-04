import frappe
from frappe.query_builder import DocType

def custom_logic(doc, method):
    frappe.msgprint("Hook executed!")

@frappe.whitelist(allow_guest=True)
def assignment_api():
    practice_manager = DocType("practice-manager")
    child = Doctype("practice-child")
    query = (
        frappe.qb.from_(practice_manager)
        .join(child).on(practice_manager.name == child.parent)
        .select(
            practice_manager.name,
            practice_manager.student_name,
            practice_manager.age,
            child.subject,
            child.marks,
        )
        .where(practice_manager.age>=18)
    )
    records = query.run(as_dict=True)
    if records:
        pr = records[0]['name']
        doc = frappe.get_doc("practice-manager",pr)
        frappe.db.set_value(
            doctype="practice-manager",
            name=pr,
            field_name="age",
            value=20
        )
        frappe.db.commit()
    return query.run(as_dict=True)