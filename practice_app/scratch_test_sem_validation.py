import frappe

def test_semester_validation():
	frappe.connect()
	
	# Test Hari (Semester 1, CSE)
	frappe.set_user("harikumaranks.23it@kongu.edu")
	frappe.form_dict = frappe._dict({"preview": "1"})

	from practice_app.www.student.marks import get_context as get_marks_context
	from practice_app.www.student.courses import get_context as get_courses_context

	ctx_marks_hari = get_marks_context(frappe._dict())
	ctx_courses_hari = get_courses_context(frappe._dict())

	print("--- HARI (Semester 1 Student) ---")
	print("Max Allowed Sem:", ctx_marks_hari.get("max_allowed_sem"))
	print("Pills Rendered in Marks:", list(ctx_marks_hari.get("semesters").keys()))
	print("Semesters Available in Courses:", ctx_courses_hari.get("available_semesters"))

	# Test Dharshan (Semester 5, IT)
	frappe.set_user("baladharshan1972@gmail.com")
	ctx_marks_dharshan = get_marks_context(frappe._dict())
	ctx_courses_dharshan = get_courses_context(frappe._dict())

	print("\n--- DHARSHAN (Semester 5 Student) ---")
	print("Max Allowed Sem:", ctx_marks_dharshan.get("max_allowed_sem"))
	print("Pills Rendered in Marks:", list(ctx_marks_dharshan.get("semesters").keys()))
	print("Semesters Available in Courses:", ctx_courses_dharshan.get("available_semesters"))

if __name__ == "__main__":
	test_semester_validation()
