""" Generate the List of Students"""
import frappe

def get_context(context):
    context.students = frappe.get_all(
        "Student-form",
        fields = ["student_name", "register_number"]
    )
    