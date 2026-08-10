import frappe
from frappe.website.serve import get_response

def test_web_serve():
	frappe.connect()
	frappe.set_user("Administrator")
	frappe.form_dict = frappe._dict({"preview": "1"})
	response = get_response("student")
	html = response.get_data(as_text=True)
	print("RESP CODE:", response.status_code)
	print("RESP FIRST 1000 CHARS:\n", html[:1200])

if __name__ == "__main__":
	test_web_serve()
