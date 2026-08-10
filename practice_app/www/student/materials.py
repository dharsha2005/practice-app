import frappe

base_template_path = "templates/portal_base.html"

def parse_sem_num(sem_val):
	if not sem_val:
		return 1
	sem_str = str(sem_val).lower().replace("semester", "").strip()
	try:
		return int(sem_str)
	except ValueError:
		return 1

def get_context(context):
	context.base_template_path = "templates/portal_base.html"
	context.title = "Course Materials & Resources - EduPortal"
	user = frappe.session.user
	
	if user == "Guest":
		frappe.redirect("/login")

	roles = frappe.get_roles(user)
	is_admin = "System Manager" in roles or "Administrator" in roles or "Faculty" in roles
	preview_mode = frappe.form_dict.get("preview") or frappe.form_dict.get("view") == "portal" or frappe.form_dict.get("student")

	if is_admin and not preview_mode:
		frappe.redirect("/app")

	# Fetch student details
	student_doc = (
		frappe.db.get_value("Student-form", {"email": user}, ["name", "student_name", "department", "semester"], as_dict=True)
		or frappe.db.get_value("Student-form", {"owner": user}, ["name", "student_name", "department", "semester"], as_dict=True)
	)

	student_dept = student_doc.get("department") if student_doc else None
	raw_sem = student_doc.get("semester") if student_doc else "1"
	max_sem_num = parse_sem_num(raw_sem)
	current_sem = f"Semester {max_sem_num}"

	# Get requested material type filter
	mat_type_filter = frappe.form_dict.get("type") or ""

	# Build Course Material filters for this student's department and current semester
	filters = {}
	if student_dept:
		# Get matching department name used in Course Material
		dept_name = frappe.db.get_value("Department", {"department_name": student_dept}, "name") or \
					frappe.db.get_value("Department", {"department_code": student_dept}, "name") or \
					student_dept
	
	# Fetch all course materials for this student's active courses
	# Filter by: courses linked to their dept + current semester
	course_names = frappe.get_all(
		"Course",
		filters={"department": dept_name if student_dept else [], "semester": current_sem},
		pluck="name"
	)

	mat_filters = {}
	if course_names:
		mat_filters["course"] = ["in", course_names]
	if mat_type_filter:
		mat_filters["material_type"] = mat_type_filter

	materials = frappe.get_all(
		"Course Material",
		filters=mat_filters,
		fields=["name", "title", "course", "semester", "material_type", "file_attachment", "description"],
		order_by="course asc, material_type asc"
	) if mat_filters else []

	# Group by course
	course_material_map = {}
	for m in materials:
		course_key = m.get("course") or "Uncategorized"
		if course_key not in course_material_map:
			course_material_map[course_key] = []
		course_material_map[course_key].append(m)

	# Available material types for filter tabs
	material_types = ["Lecture Notes", "Syllabus PDF", "Lab Manual", "Reference Textbook", "Question Bank"]

	context.student = student_doc or {}
	context.student_dept = student_dept
	context.current_sem = current_sem
	context.materials = materials
	context.course_material_map = course_material_map
	context.material_types = material_types
	context.selected_type = mat_type_filter
	context.total_count = len(materials)
	return context
