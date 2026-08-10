import frappe
from frappe.website.serve import get_response

def test_all_routes():
	frappe.connect()
	frappe.set_user("Administrator")
	frappe.form_dict = frappe._dict({"preview": "1"})

	routes = [
		"student",
		"student/profile",
		"student/attendance",
		"student/marks",
		"student/fees",
		"student/notifications",
		"student/assignments",
		"student/timetable",
		"student/materials",
		"student/announcements",
		"student/courses",
		"student/leave",
		"student/certificates",
		"student/settings",
		"student/admission",
		"courses",
		"faculty",
		"events",
		"contact"
	]
	
	failed = 0
	for r in routes:
		res = get_response(r)
		status = res.status_code
		print(f"ROUTE /{r:25} -> STATUS {status}")
		if status != 200:
			failed += 1
			
	print(f"\nTOTAL ROUTES TESTED: {len(routes)}, FAILED: {failed}")

if __name__ == "__main__":
	test_all_routes()
