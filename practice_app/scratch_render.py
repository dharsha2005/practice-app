import frappe

def render_test():
	frappe.connect()
	context = frappe._dict({
		"student": frappe._dict({
			"student_name": "Hari",
			"register_number": "CS2026-042",
			"department": "Computer Science & Engineering",
			"semester": 5,
			"year": 3,
			"cgpa": 8.6
		}),
		"attendance_pct": 87.0
	})
	html = frappe.render_template("www/student/index.html", context)
	print("RENDERED HTML LENGTH:", len(html))
	print(html[:500])

if __name__ == "__main__":
	render_test()
