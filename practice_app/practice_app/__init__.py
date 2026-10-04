import frappe

def get_courses():
	Course = frappe.qb.DocType("Course")
	query = (
		frappe.qb.from_(Course)
		.select(Course.course_name, Course.department)
	)
	return query.run(as_dict=True)
