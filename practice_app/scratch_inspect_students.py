import frappe

def inspect_and_setup_students():
	frappe.connect()
	frappe.set_user("Administrator")

	# Update Hari -> Semester 1 (Value: "1"), CSE
	hari_id = frappe.db.get_value("Student-form", {"email": "harikumaranks.23it@kongu.edu"}, "name") or frappe.db.get_value("Student-form", {"student_name": "Hari"}, "name")
	if hari_id:
		frappe.db.set_value("Student-form", hari_id, {"department": "CSE", "semester": "1"})
		print(f"UPDATED HARI ({hari_id}): Dept=CSE, Sem=1")

	# Update Dharshan (baladharshan1972@gmail.com) -> Semester 5 (Value: "5"), IT
	dharshan_id = frappe.db.get_value("Student-form", {"email": "baladharshan1972@gmail.com"}, "name") or frappe.db.get_value("Student-form", {"student_name": "Dharshan"}, "name")
	if dharshan_id:
		frappe.db.set_value("Student-form", dharshan_id, {"department": "IT", "semester": "5"})
		print(f"UPDATED DHARSHAN ({dharshan_id}): Dept=IT, Sem=5")

	frappe.db.commit()
	print("STUDENTS UPDATED SUCCESSFULLY.")

if __name__ == "__main__":
	inspect_and_setup_students()
