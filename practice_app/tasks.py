import frappe
def daily_maintenance():
    frappe.log_error("Background job started")
