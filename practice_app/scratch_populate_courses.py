import frappe

def populate_courses_and_departments():
	frappe.connect()
	frappe.set_user("Administrator")

	# Fetch existing departments in DB
	depts = frappe.get_all("Department", fields=["name", "department_name", "department_code"])
	dept_map = {}
	for d in depts:
		dept_map[d["department_name"]] = d["name"]
		dept_map[d["department_code"]] = d["name"]

	print("DEPT MAP:", dept_map)

	# Ensure Departments exist if missing
	departments = [
		{"department_name": "Computer Science & Engineering", "department_code": "CSE"},
		{"department_name": "Information Technology", "department_code": "IT"},
		{"department_name": "AI & Data Science", "department_code": "AIDS"},
		{"department_name": "Electronics & Communication", "department_code": "ECE"},
		{"department_name": "Electrical & Electronics", "department_code": "EEE"},
		{"department_name": "Mechanical Engineering", "department_code": "MECH"},
		{"department_name": "Civil Engineering", "department_code": "CIVIL"}
	]

	for d in departments:
		code = d["department_code"]
		if not frappe.db.exists("Department", code):
			doc = frappe.get_doc({"doctype": "Department", **d})
			doc.insert(ignore_permissions=True)
			dept_map[d["department_name"]] = doc.name
			dept_map[code] = doc.name
			print(f"CREATED DEPARTMENT: {d['department_name']} -> {doc.name}")

	# Detailed Course Catalog per Department & Semester
	courses_data = [
		# IT Department Courses
		{"course_code": "IT501", "course_name": "Full-Stack Web Development", "department": dept_map.get("Information Technology") or dept_map.get("IT") or "IT", "semester": "Semester 5", "credits": 4, "description": "RESTful API design, Node.js, Express, React framework, and MongoDB integration."},
		{"course_code": "IT502", "course_name": "Cloud Computing & DevOps", "department": dept_map.get("Information Technology") or dept_map.get("IT") or "IT", "semester": "Semester 5", "credits": 4, "description": "AWS cloud infrastructure, Docker containerization, and CI/CD pipelines."},
		{"course_code": "IT503", "course_name": "Cyber Security & Cryptography", "department": dept_map.get("Information Technology") or dept_map.get("IT") or "IT", "semester": "Semester 5", "credits": 3, "description": "Network security protocols, RSA encryption, ethical hacking, and vulnerability testing."},
		{"course_code": "IT504", "course_name": "Mobile Application Development", "department": dept_map.get("Information Technology") or dept_map.get("IT") or "IT", "semester": "Semester 5", "credits": 4, "description": "Android Native and React Native cross-platform mobile application development."},

		{"course_code": "IT401", "course_name": "Object Oriented System Design", "department": dept_map.get("Information Technology") or dept_map.get("IT") or "IT", "semester": "Semester 4", "credits": 4, "description": "UML modeling, design patterns, solid principles, and Java Enterprise Edition."},
		{"course_code": "IT402", "course_name": "Computer Networks & Sockets", "department": dept_map.get("Information Technology") or dept_map.get("IT") or "IT", "semester": "Semester 4", "credits": 4, "description": "TCP/IP layer protocols, routing algorithms, and network socket programming."},

		# CSE Department Courses
		{"course_code": "CS301", "course_name": "Data Structures & Algorithms", "department": dept_map.get("Computer Science & Engineering") or dept_map.get("CSE") or "CSE", "semester": "Semester 5", "credits": 4, "description": "Height-balanced BSTs, graph algorithms, and asymptotic time complexity analysis."},
		{"course_code": "CS302", "course_name": "Database Management Systems", "department": dept_map.get("Computer Science & Engineering") or dept_map.get("CSE") or "CSE", "semester": "Semester 5", "credits": 4, "description": "Relational algebra, SQL querying, E-R modeling, 3NF normalization, and ACID properties."},
		{"course_code": "CS303", "course_name": "Operating Systems", "department": dept_map.get("Computer Science & Engineering") or dept_map.get("CSE") or "CSE", "semester": "Semester 5", "credits": 4, "description": "Process synchronization, CPU scheduling, virtual memory paging, and deadlock handling."},
		{"course_code": "CS304", "course_name": "Computer Networks", "department": dept_map.get("Computer Science & Engineering") or dept_map.get("CSE") or "CSE", "semester": "Semester 5", "credits": 4, "description": "OSI model, Ethernet, IP addressing, TCP congestion control, and DNS protocols."},

		{"course_code": "CS201", "course_name": "Theory of Computation", "department": dept_map.get("Computer Science & Engineering") or dept_map.get("CSE") or "CSE", "semester": "Semester 4", "credits": 4, "description": "Finite automata, regular expressions, context-free grammars, and Turing machines."},
		{"course_code": "CS202", "course_name": "Software Engineering", "department": dept_map.get("Computer Science & Engineering") or dept_map.get("CSE") or "CSE", "semester": "Semester 4", "credits": 4, "description": "Agile methodologies, software testing, requirement engineering, and Git workflows."},

		# AI & DS Department Courses
		{"course_code": "AD501", "course_name": "Deep Learning & Neural Networks", "department": dept_map.get("AI & Data Science") or dept_map.get("AIDS") or "AIDS", "semester": "Semester 5", "credits": 4, "description": "PyTorch, Convolutional Neural Networks (CNNs), and Transformer models."},
		{"course_code": "AD502", "course_name": "Big Data Analytics & PySpark", "department": dept_map.get("AI & Data Science") or dept_map.get("AIDS") or "AIDS", "semester": "Semester 5", "credits": 4, "description": "Hadoop Distributed File System (HDFS), MapReduce, and PySpark RDD analytics."},

		# ECE Department Courses
		{"course_code": "EC501", "course_name": "Embedded Systems & ARM", "department": dept_map.get("Electronics & Communication") or dept_map.get("ECE") or "ECE", "semester": "Semester 5", "credits": 4, "description": "ARM Cortex-M architecture, GPIO interfacing, and FreeRTOS microcontrollers."},
		{"course_code": "EC502", "course_name": "Wireless Communication", "department": dept_map.get("Electronics & Communication") or dept_map.get("ECE") or "ECE", "semester": "Semester 5", "credits": 4, "description": "Cellular communication systems, 5G NR architecture, and OFDM signal processing."},

		# EEE Department Courses
		{"course_code": "EE501", "course_name": "Power Electronics & Drives", "department": dept_map.get("Electrical & Electronics") or dept_map.get("EEE") or "EEE", "semester": "Semester 5", "credits": 4, "description": "Thyristors, inverters, choppers, and AC/DC drive control systems."},
		{"course_code": "EE502", "course_name": "Control Systems Engineering", "department": dept_map.get("Electrical & Electronics") or dept_map.get("EEE") or "EEE", "semester": "Semester 5", "credits": 4, "description": "Bode plots, Root Locus stability, state-space representations, and PID controllers."},

		# Mechanical Department Courses
		{"course_code": "ME501", "course_name": "Heat Transfer & Thermodynamics", "department": dept_map.get("Mechanical Engineering") or dept_map.get("MECH") or "MECH", "semester": "Semester 5", "credits": 4, "description": "Conduction, convection, radiation heat exchangers, and steam turbines."},
		{"course_code": "ME502", "course_name": "CAD/CAM & FEA Modeling", "department": dept_map.get("Mechanical Engineering") or dept_map.get("MECH") or "MECH", "semester": "Semester 5", "credits": 4, "description": "3D SolidWorks modeling, CNC G-code programming, and ANSYS finite element analysis."},

		# Civil Department Courses
		{"course_code": "CE501", "course_name": "Surveying & Structural Engineering", "department": dept_map.get("Civil Engineering") or dept_map.get("CIVIL") or "CIVIL", "semester": "Semester 5", "credits": 4, "description": "Total station surveying, GPS levelling, and reinforced concrete beam design."},
		{"course_code": "CE502", "course_name": "Concrete Technology & Lab", "department": dept_map.get("Civil Engineering") or dept_map.get("CIVIL") or "CIVIL", "semester": "Semester 5", "credits": 4, "description": "Slump test, mix ratio design, and compressive strength testing of concrete cubes."}
	]

	for c in courses_data:
		code = c["course_code"]
		if frappe.db.exists("Course", code):
			doc = frappe.get_doc("Course", code)
			doc.update(c)
			doc.save(ignore_permissions=True)
			print(f"UPDATED COURSE: {code}")
		else:
			doc = frappe.get_doc({"doctype": "Course", **c})
			doc.insert(ignore_permissions=True)
			print(f"CREATED COURSE: {code}")

	frappe.db.commit()
	print("COURSES POPULATION COMPLETED SUCCESSFULLY.")

if __name__ == "__main__":
	populate_courses_and_departments()
