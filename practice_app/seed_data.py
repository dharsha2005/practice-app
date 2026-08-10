import frappe

def seed():
	print("Seeding initial data into MariaDB...")
	frappe.init(site="practice.localhost", sites_path="sites")
	frappe.connect()

	# 0. Ensure Student Role Exists
	if not frappe.db.exists("Role", "Student"):
		role_doc = frappe.get_doc({"doctype": "Role", "role_name": "Student", "desk_access": 0})
		role_doc.insert(ignore_permissions=True)
		print("Created Role: Student")

	# 0. Create User Accounts for Students
	student_users = [
		{"email": "dharshan@example.com", "first_name": "Dharshan", "last_name": "R"},
		{"email": "ananya@example.com", "first_name": "Ananya", "last_name": "Sharma"}
	]

	for u in student_users:
		if not frappe.db.exists("User", u["email"]):
			user_doc = frappe.get_doc({
				"doctype": "User",
				"email": u["email"],
				"first_name": u["first_name"],
				"last_name": u["last_name"],
				"enabled": 1,
				"send_welcome_email": 0,
				"user_type": "Website User",
				"new_password": "EduPortal@2026!"
			})
			user_doc.insert(ignore_permissions=True)
			user_doc.add_roles("Student")
			print(f"Created User: {u['email']}")
		else:
			u_doc = frappe.get_doc("User", u["email"])
			u_doc.new_password = "EduPortal@2026!"
			u_doc.save(ignore_permissions=True)
			u_doc.add_roles("Student")

	# 1. Departments
	departments = [
		{"department_name": "Computer Science & Engineering", "department_code": "CSE", "established_year": 2005, "head_of_department": "Dr. Alan Turing", "description": "School of Computer Science and Intelligent Systems."},
		{"department_name": "Information Technology", "department_code": "IT", "established_year": 2008, "head_of_department": "Dr. Ada Lovelace", "description": "Department of Cloud, Web, and Software Engineering."},
		{"department_name": "Electronics & Communication", "department_code": "ECE", "established_year": 2006, "head_of_department": "Dr. Nikola Tesla", "description": "School of VLSI, Embedded Systems, and IoT."},
		{"department_name": "Electrical & Electronics", "department_code": "EEE", "established_year": 2007, "head_of_department": "Prof. Michael Faraday", "description": "Department of Power Electronics and Smart Grids."},
		{"department_name": "Mechanical Engineering", "department_code": "MECH", "established_year": 2005, "head_of_department": "Prof. James Watt", "description": "Department of CAD/CAM, Thermal Science, and Robotics."},
		{"department_name": "Civil Engineering", "department_code": "CIVIL", "established_year": 2009, "head_of_department": "Prof. Isambard Brunel", "description": "Department of Structural and Environmental Engineering."},
		{"department_name": "Artificial Intelligence & Data Science", "department_code": "AIDS", "established_year": 2021, "head_of_department": "Dr. Geoffrey Hinton", "description": "Department of Neural Networks and Big Data Analytics."}
	]

	for d in departments:
		if not frappe.db.exists("Department", d["department_code"]):
			doc = frappe.get_doc({"doctype": "Department", **d})
			doc.insert(ignore_permissions=True)

	# 2. Courses
	courses = [
		{"course_name": "B.Tech Computer Science & Engineering", "course_code": "BTECH-CSE", "department": "CSE", "duration_years": 4, "credits": 160, "description": "Algorithms, Systems, AI, and Software Architecture."},
		{"course_name": "B.Tech Information Technology", "course_code": "BTECH-IT", "department": "IT", "duration_years": 4, "credits": 160, "description": "Full-Stack Web APIs, Cloud Systems, and Cybersecurity."},
		{"course_name": "B.E. Electronics & Communication", "course_code": "BE-ECE", "department": "ECE", "duration_years": 4, "credits": 160, "description": "Embedded Hardware, Signal Processing, and Wireless Comms."},
		{"course_name": "B.E. Electrical & Electronics", "course_code": "BE-EEE", "department": "EEE", "duration_years": 4, "credits": 160, "description": "Power Engineering, Machines, and Drives."},
		{"course_name": "B.E. Mechanical Engineering", "course_code": "BE-MECH", "department": "MECH", "duration_years": 4, "credits": 160, "description": "Automotive Engineering, Thermodynamics, and Mechatronics."},
		{"course_name": "B.E. Civil Engineering", "course_code": "BE-CIVIL", "department": "CIVIL", "duration_years": 4, "credits": 160, "description": "Surveying, Structural Design, and Construction Mgmt."},
		{"course_name": "B.Tech AI & Data Science", "course_code": "BTECH-AIDS", "department": "AIDS", "duration_years": 4, "credits": 160, "description": "Deep Learning, Analytics, and Computer Vision."}
	]

	for c in courses:
		if not frappe.db.exists("Course", c["course_code"]):
			doc = frappe.get_doc({"doctype": "Course", **c})
			doc.insert(ignore_permissions=True)

	# 3. Faculty
	faculties = [
		{"employee_id": "EMP-001", "faculty_name": "Dr. Alan Turing", "designation": "Professor & HOD", "department": "CSE", "email": "alan.turing@eduportal.edu", "phone_number": "+919876543201", "qualification": "Ph.D. in Computer Science", "photo": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80"},
		{"employee_id": "EMP-002", "faculty_name": "Dr. Ada Lovelace", "designation": "Professor", "department": "IT", "email": "ada.lovelace@eduportal.edu", "phone_number": "+919876543202", "qualification": "Ph.D. in Software Systems", "photo": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=300&q=80"},
		{"employee_id": "EMP-003", "faculty_name": "Dr. Nikola Tesla", "designation": "Associate Professor", "department": "ECE", "email": "nikola.tesla@eduportal.edu", "phone_number": "+919876543203", "qualification": "Ph.D. in Electrical Engineering", "photo": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=300&q=80"},
		{"employee_id": "EMP-004", "faculty_name": "Prof. Margaret Hamilton", "designation": "Assistant Professor", "department": "CSE", "email": "m.hamilton@eduportal.edu", "phone_number": "+919876543204", "qualification": "M.Tech in Software Engineering", "photo": "https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&w=300&q=80"}
	]

	for f in faculties:
		if not frappe.db.exists("Faculty", f["employee_id"]):
			doc = frappe.get_doc({"doctype": "Faculty", **f})
			doc.insert(ignore_permissions=True)

	# 4. Students
	students = [
		{
			"student_name": "Dharshan R",
			"register_number": "211422104001",
			"department": "IT",
			"year": "III",
			"semester": "6",
			"phone_number": "+919876543210",
			"email": "dharshan@example.com",
			"gender": "Male",
			"blood_group": "O+",
			"date_of_birth": "2004-05-14",
			"age": 22,
			"cgpa": 8.85,
			"address": "123 Academic Street, Tech Park",
			"city": "Chennai",
			"state": "Tamil Nadu",
			"country": "India",
			"pincode": "600001",
			"father_name": "Rajeswaran K",
			"mother_name": "Lakshmi R",
			"parent_phone": "+919876543211",
			"parent_email": "parent@example.com",
			"student_photo": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&w=300&q=80"
		},
		{
			"student_name": "Ananya Sharma",
			"register_number": "211422104002",
			"department": "CSE",
			"year": "III",
			"semester": "6",
			"phone_number": "+919876543220",
			"email": "ananya@example.com",
			"gender": "Female",
			"blood_group": "A+",
			"date_of_birth": "2004-08-20",
			"age": 22,
			"cgpa": 9.20,
			"address": "45 Green Park Colony",
			"city": "Bengaluru",
			"state": "Karnataka",
			"country": "India",
			"pincode": "560001",
			"father_name": "Suresh Sharma",
			"mother_name": "Anita Sharma",
			"parent_phone": "+919876543221",
			"parent_email": "ananya_parent@example.com",
			"student_photo": "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=300&q=80"
		}
	]

	created_students = []
	for s in students:
		if not frappe.db.exists("Student-form", s["student_name"]):
			doc = frappe.get_doc({"doctype": "Student-form", **s})
			doc.insert(ignore_permissions=True)
			created_students.append(doc.name)
		else:
			doc = frappe.get_doc("Student-form", s["student_name"])
			doc.email = s["email"]
			doc.save(ignore_permissions=True)
			created_students.append(doc.name)

	# 5. Attendance
	if len(created_students) >= 2:
		# Student 1: Dharshan R
		s1 = created_students[0]
		att_dates1 = ["2026-08-07", "2026-08-06", "2026-08-05", "2026-08-04", "2026-08-03"]
		att_subjects1 = ["Web Development & APIs", "Database Management Systems", "Data Structures & Algorithms", "Computer Networks", "Operating Systems"]
		att_statuses1 = ["Present", "Present", "Present", "On Leave", "Present"]
		for i in range(len(att_dates1)):
			if not frappe.db.exists("Attendance", {"student": s1, "date": att_dates1[i]}):
				doc = frappe.get_doc({"doctype": "Attendance", "student": s1, "date": att_dates1[i], "subject": att_subjects1[i], "status": att_statuses1[i], "remarks": "Lecture & Practical"})
				doc.insert(ignore_permissions=True)

		# Student 2: Ananya Sharma
		s2 = created_students[1]
		att_dates2 = ["2026-08-07", "2026-08-06", "2026-08-05", "2026-08-04"]
		att_subjects2 = ["Artificial Intelligence", "Machine Learning", "Cloud Computing", "Software Engineering"]
		att_statuses2 = ["Present", "Present", "Present", "Present"]
		for i in range(len(att_dates2)):
			if not frappe.db.exists("Attendance", {"student": s2, "date": att_dates2[i]}):
				doc = frappe.get_doc({"doctype": "Attendance", "student": s2, "date": att_dates2[i], "subject": att_subjects2[i], "status": att_statuses2[i], "remarks": "Lecture"})
				doc.insert(ignore_permissions=True)

		# Marks for Dharshan R
		marks1 = [
			{"subject": "Web Development & APIs", "exam_type": "Internal Assessment", "obtained_marks": 92, "total_marks": 100},
			{"subject": "Database Management Systems", "exam_type": "Internal Assessment", "obtained_marks": 85, "total_marks": 100}
		]
		for m in marks1:
			if not frappe.db.exists("Marks", {"student": s1, "subject": m["subject"]}):
				doc = frappe.get_doc({"doctype": "Marks", "student": s1, **m})
				doc.insert(ignore_permissions=True)

		# Marks for Ananya Sharma
		marks2 = [
			{"subject": "Artificial Intelligence", "exam_type": "Internal Assessment", "obtained_marks": 96, "total_marks": 100},
			{"subject": "Machine Learning", "exam_type": "Internal Assessment", "obtained_marks": 94, "total_marks": 100}
		]
		for m in marks2:
			if not frappe.db.exists("Marks", {"student": s2, "subject": m["subject"]}):
				doc = frappe.get_doc({"doctype": "Marks", "student": s2, **m})
				doc.insert(ignore_permissions=True)

		# Fees
		if not frappe.db.exists("Fee", {"student": s1}):
			doc = frappe.get_doc({"doctype": "Fee", "student": s1, "posting_date": "2026-06-01", "due_date": "2026-07-15", "tuition_fee": 45000, "hostel_fee": 25000, "other_fee": 5000, "paid_amount": 75000})
			doc.insert(ignore_permissions=True)

		if not frappe.db.exists("Fee", {"student": s2}):
			doc = frappe.get_doc({"doctype": "Fee", "student": s2, "posting_date": "2026-06-01", "due_date": "2026-07-15", "tuition_fee": 48000, "hostel_fee": 0, "other_fee": 4000, "paid_amount": 52000})
			doc.insert(ignore_permissions=True)

	frappe.db.commit()
	print("Database seeding completed successfully! Credentials: email and password 'EduPortal@2026!'")

if __name__ == "__main__":
	seed()
