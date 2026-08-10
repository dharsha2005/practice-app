import frappe

def test_full_curriculum_fetch():
	frappe.connect()
	frappe.form_dict = frappe._dict({"preview": "1"})

	from practice_app.www.student.courses import get_context

	# Test 1: Hari (Semester 1, CSE)
	frappe.set_user("harikumaranks.23it@kongu.edu")
	ctx_hari = get_context(frappe._dict())
	print("--- HARI (Semester 1 CSE Student) ---")
	print("Department:", ctx_hari.get("student_dept"))
	print("Active Semester:", ctx_hari.get("student_sem"))
	print("Available Semesters:", ctx_hari.get("available_semesters"))
	print("Courses Count:", len(ctx_hari.get("courses")))
	for c in ctx_hari.get("courses"):
		print(f"  - {c.course_code}: {c.course_name} (Notes: {len(c.notes)})")

	# Test 2: Dharshan (Semester 5 IT)
	frappe.set_user("baladharshan1972@gmail.com")
	ctx_dharshan = get_context(frappe._dict())
	print("\n--- DHARSHAN (Semester 5 IT Student) ---")
	print("Department:", ctx_dharshan.get("student_dept"))
	print("Active Semester:", ctx_dharshan.get("student_sem"))
	print("Available Semesters:", ctx_dharshan.get("available_semesters"))
	print("Courses Count:", len(ctx_dharshan.get("courses")))
	for c in ctx_dharshan.get("courses"):
		print(f"  - {c.course_code}: {c.course_name} (Notes: {len(c.notes)})")

if __name__ == "__main__":
	test_full_curriculum_fetch()
