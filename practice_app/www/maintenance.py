import frappe

def get_context(context):
	context.message = frappe.db.get_single_value(
		"Student Portal Settings", 
		"maintenance_message"
	) or "The Student Portal is temporarily offline for maintenance. Please try again later."
	return context
