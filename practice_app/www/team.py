import frappe

def get_context(context):
    context.title= "our family"
    context.no_cache = True
    
    context.users = frappe.get_all(
        "User",
        filters = {"enabled": 1},
        fields = ["email", "full_name"],    
        order_by = "modified desc"
    )