import frappe


def get_context(context):
    context.title = "No tasks"
    context.task = frappe.get_all(
        "Task",
        fields = ["subject"],
        order_by = "modified desc",
        limit = 10
    )