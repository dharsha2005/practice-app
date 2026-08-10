import frappe

def get_context(context):
	context.title = "Campus News & Events - EduPortal"
	
	context.events = frappe.get_all(
		"Notification",
		fields=["title", "category", "date", "message"],
		order_by="date desc"
	)

	return context
