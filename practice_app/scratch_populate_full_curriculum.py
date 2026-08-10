import os
import frappe

def seed_full_curriculum():
	frappe.connect()
	frappe.set_user("Administrator")

	departments = [
		{"department_name": "Computer Science & Engineering", "department_code": "CSE"},
		{"department_name": "Information Technology", "department_code": "IT"},
		{"department_name": "AI & Data Science", "department_code": "AIDS"},
		{"department_name": "Electronics & Communication", "department_code": "ECE"},
		{"department_name": "Electrical & Electronics", "department_code": "EEE"},
		{"department_name": "Mechanical Engineering", "department_code": "MECH"},
		{"department_name": "Civil Engineering", "department_code": "CIVIL"}
	]

	dept_map = {}
	for d in departments:
		code = d["department_code"]
		if not frappe.db.exists("Department", code):
			doc = frappe.get_doc({"doctype": "Department", **d})
			doc.insert(ignore_permissions=True)
			dept_map[code] = doc.name
		else:
			dept_map[code] = code

	print("DEPARTMENTS INITIALIZED:", dept_map)

	# Template subjects for Semesters 1 to 8 across all engineering disciplines
	curriculum_templates = {
		"Semester 1": [
			{"code_prefix": "MA101", "name": "Linear Algebra & Differential Calculus", "credits": 4, "desc": "Matrices, eigenvalues, single variable calculus, and ordinary differential equations."},
			{"code_prefix": "PH101", "name": "Engineering Physics", "credits": 4, "desc": "Oscillations, optics, lasers, fiber optics, and quantum mechanics fundamentals."},
			{"code_prefix": "GE101", "name": "Problem Solving & Python Programming", "credits": 4, "desc": "Algorithmic thinking, control flow, functions, structures, and Python modules."},
			{"code_prefix": "GE102", "name": "Engineering Graphics & Design", "credits": 3, "desc": "Projection of points, lines, planes, solids, isometric views, and CAD drafting."}
		],
		"Semester 2": [
			{"code_prefix": "MA102", "name": "Vector Calculus & Complex Variables", "credits": 4, "desc": "Vector differential calculus, line integrals, analytic functions, and residues."},
			{"code_prefix": "CH101", "name": "Engineering Chemistry", "credits": 4, "desc": "Water technology, electrochemistry, corrosion control, polymers, and fuels."},
			{"code_prefix": "GE201", "name": "Basic Electrical & Electronics Engg", "credits": 3, "desc": "DC/AC circuit theorems, transformers, diodes, transistors, and operational amplifiers."},
			{"code_prefix": "GE202", "name": "C Programming & Data Structures", "credits": 4, "desc": "Pointers, dynamic memory allocation, stacks, queues, and linked lists in C."}
		],
		"Semester 3": [
			{"code_prefix": "MA301", "name": "Discrete Mathematics & Probability", "credits": 4, "desc": "Propositional logic, combinatorics, graph theory, random variables, and distributions."},
			{"code_prefix": "CORE301", "name": "Data Structures & Algorithmic Analysis", "credits": 4, "desc": "Trees, AVL structures, heaps, sorting algorithms, and divide-and-conquer strategies."},
			{"code_prefix": "CORE302", "name": "Digital Logic & System Design", "credits": 4, "desc": "Karnaugh maps, combinational logic, sequential flip-flops, counters, and Verilog HDL."},
			{"code_prefix": "CORE303", "name": "Object Oriented Programming (C++/Java)", "credits": 3, "desc": "Classes, inheritance, polymorphism, templates, exception handling, and STL."}
		],
		"Semester 4": [
			{"code_prefix": "MA401", "name": "Numerical Methods & Statistics", "credits": 4, "desc": "Root finding, interpolation, numerical integration, and hypothesis testing."},
			{"code_prefix": "CORE401", "name": "Database Management Systems", "credits": 4, "desc": "Relational model, SQL queries, normalization 3NF/BCNF, indexing, and transactions."},
			{"code_prefix": "CORE402", "name": "Operating Systems & Architecture", "credits": 4, "desc": "Process scheduling, thread synchronization, virtual memory, and POSIX system calls."},
			{"code_prefix": "CORE403", "name": "Computer Organization & Assembly", "credits": 3, "desc": "Instruction set architecture, MIPS pipeline, cache memory, and I/O organization."}
		],
		"Semester 5": [
			{"code_prefix": "CORE501", "name": "Computer Networks & Protocols", "credits": 4, "desc": "OSI & TCP/IP layers, routing protocols, flow control, socket API, and DNS."},
			{"code_prefix": "CORE502", "name": "Theory of Computation & Automata", "credits": 4, "desc": "DFA/NFA, regular languages, context-free grammars, and Turing machine computability."},
			{"code_prefix": "CORE503", "name": "Software Engineering & Agile", "credits": 4, "desc": "Requirements modeling, UML design, software architecture, testing, and DevOps."},
			{"code_prefix": "CORE504", "name": "Web Technology & Cloud Applications", "credits": 3, "desc": "Full-stack web development, REST APIs, microservices, and cloud deployment."}
		],
		"Semester 6": [
			{"code_prefix": "CORE601", "name": "Artificial Intelligence & Machine Learning", "credits": 4, "desc": "Search algorithms, supervised regression/classification, decision trees, and SVMs."},
			{"code_prefix": "CORE602", "name": "Compiler Design & Code Generation", "credits": 4, "desc": "Lexical analysis, LALR parsing, intermediate code representation, and optimization."},
			{"code_prefix": "CORE603", "name": "Cryptography & Cyber Security", "credits": 4, "desc": "AES, RSA, public key infrastructure, network firewalls, and ethical hacking."},
			{"code_prefix": "CORE604", "name": "Mobile & Pervasive Computing", "credits": 3, "desc": "Mobile OS architectures, wireless protocols, and cross-platform native apps."}
		],
		"Semester 7": [
			{"code_prefix": "CORE701", "name": "Cloud Infrastructure & Distributed Systems", "credits": 4, "desc": "Virtualization, Docker containers, Kubernetes, consensus protocols, and AWS/Azure."},
			{"code_prefix": "CORE702", "name": "Big Data Analytics & PySpark", "credits": 4, "desc": "Hadoop, MapReduce, HDFS, Spark RDDs, streaming analytics, and NoSQL databases."},
			{"code_prefix": "CORE703", "name": "Elective 1: Deep Learning & Vision", "credits": 3, "desc": "Convolutional networks, recurrent networks, PyTorch, and computer vision."},
			{"code_prefix": "PROJECT7", "name": "Major Project Phase I & Seminar", "credits": 4, "desc": "Problem formulation, literature review, architectural design, and prototype build."}
		],
		"Semester 8": [
			{"code_prefix": "CORE801", "name": "Blockchain & Smart Contracts", "credits": 3, "desc": "Distributed ledgers, Ethereum EVM, Solidity programming, and consensus algorithms."},
			{"code_prefix": "CORE802", "name": "Internet of Things (IoT) & Edge Computing", "credits": 3, "desc": "Sensory nodes, MQTT, Raspberry Pi/ESP32, edge processing, and industrial IoT."},
			{"code_prefix": "PROJECT8", "name": "Capestone Industrial Project & Thesis", "credits": 8, "desc": "Full industrial implementation, performance benchmarking, and final thesis defense."}
		]
	}

	site_files_path = frappe.get_site_path("public", "files")
	os.makedirs(site_files_path, exist_ok=True)

	dummy_pdf_data = (
		"%PDF-1.4\n"
		"1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj\n"
		"2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj\n"
		"3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R>> endobj\n"
		"4 0 obj <</Length 55>> stream\n"
		"BT /F1 18 Tf 50 700 Td (TIT Engineering - Verified Academic Syllabus & Notes) Tj ET\n"
		"endstream endobj\n"
		"xref\n"
		"0 5\n"
		"0000000000 65535 f \n"
		"0000000009 00000 n \n"
		"0000000056 00000 n \n"
		"0000000111 00000 n \n"
		"0000000212 00000 n \n"
		"trailer <</Size 5 /Root 1 0 R>>\n"
		"startxref\n"
		"318\n"
		"%%EOF"
	)

	course_count = 0
	material_count = 0

	for dept_code in ["CSE", "IT", "AIDS", "ECE", "EEE", "MECH", "CIVIL"]:
		dept_name = dept_map[dept_code]
		
		for sem_title, subj_list in curriculum_templates.items():
			sem_num = sem_title.replace("Semester ", "")

			for subj in subj_list:
				course_code = f"{dept_code}-{subj['code_prefix']}"
				full_course_name = f"{subj['name']} ({dept_code})"
				
				# Upsert Course doc
				if frappe.db.exists("Course", course_code):
					c_doc = frappe.get_doc("Course", course_code)
					c_doc.course_name = full_course_name
					c_doc.department = dept_code
					c_doc.semester = sem_title
					c_doc.credits = subj["credits"]
					c_doc.description = f"{subj['desc']} Specific to {dept_code} Department, {sem_title}."
					c_doc.save(ignore_permissions=True)
				else:
					c_doc = frappe.get_doc({
						"doctype": "Course",
						"course_code": course_code,
						"course_name": full_course_name,
						"department": dept_code,
						"semester": sem_title,
						"duration_years": 4,
						"credits": subj["credits"],
						"description": f"{subj['desc']} Specific to {dept_code} Department, {sem_title}."
					})
					c_doc.insert(ignore_permissions=True)
					course_count += 1

				# Create physical PDF & Course Material entry for each course
				pdf_filename = f"{course_code}_Notes.pdf"
				pdf_filepath = os.path.join(site_files_path, pdf_filename)
				with open(pdf_filepath, "wb") as f:
					f.write(dummy_pdf_data.encode("latin-1"))

				file_url = f"/files/{pdf_filename}"
				if not frappe.db.exists("File", {"file_url": file_url}):
					frappe.get_doc({
						"doctype": "File",
						"file_name": pdf_filename,
						"file_url": file_url,
						"is_private": 0
					}).insert(ignore_permissions=True)

				# Seed 2 Course Material records per course
				mat_title1 = f"{subj['name']} - Complete Unit 1 to 5 Lecture Notes"
				mat_title2 = f"{subj['name']} - Lab Manual & Practical Experiments"

				if not frappe.db.exists("Course Material", {"title": mat_title1, "course": course_code}):
					frappe.get_doc({
						"doctype": "Course Material",
						"title": mat_title1,
						"course": course_code,
						"semester": sem_title,
						"material_type": "Lecture Notes",
						"file_attachment": file_url,
						"description": f"Verified lecture notes and reading material for {course_code}."
					}).insert(ignore_permissions=True)
					material_count += 1

				if not frappe.db.exists("Course Material", {"title": mat_title2, "course": course_code}):
					frappe.get_doc({
						"doctype": "Course Material",
						"title": mat_title2,
						"course": course_code,
						"semester": sem_title,
						"material_type": "Lab Manual",
						"file_attachment": file_url,
						"description": f"Verified practical lab code and experiment manual for {course_code}."
					}).insert(ignore_permissions=True)
					material_count += 1

	frappe.db.commit()
	print(f"FULL CURRICULUM SEEDED: Created/updated courses and {material_count} materials across 7 departments for Semesters 1 to 8!")

if __name__ == "__main__":
	seed_full_curriculum()
