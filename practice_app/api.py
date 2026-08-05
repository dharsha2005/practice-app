import frappe
from frappe.query_builder import DocType
from frappe.utils import now

def custom_logic(doc, method):
    frappe.msgprint("Hook executed!")

@frappe.whitelist(allow_guest=True)
def assignment_api():
    practice_manager = DocType("practice-manager")
    child = DocType("practice-child")
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
            "practice-manager",
            pr,
            "age",
            20
        )
        frappe.db.commit()
    return query.run(as_dict=True)

@frappe.whitelist()
def get_recent_todos():
    todos = frappe.get_list(
        "ToDo",
        fields = ["name","description","owner"],
        order_by= "modified desc",
        limit= 5    
    )
    for todo in todos:
        email = frappe.db.get_value(
            "User",
            todo['owner'],
            "email"
        )
        todo['email'] = email
    return{
        'timestamp':now(),
        'records': todos
    }