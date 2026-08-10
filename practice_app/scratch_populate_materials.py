import frappe

def populate_course_materials():
	frappe.connect()
	frappe.set_user("Administrator")

	# Fetch all courses
	courses = frappe.get_all("Course", fields=["name", "course_name", "course_code", "department"])
	print(f"FOUND {len(courses)} COURSES.")

	# Pre-defined course specific materials map
	materials_map = {
		"B.E. Civil Engineering": [
			{"title": "CE501 Surveying & Structural Analysis Notes", "material_type": "Lecture Notes", "file_attachment": "/files/CE501_Surveying_Notes.pdf", "description": "Complete lecture notes on surveying, leveling, and structural design."},
			{"title": "CE502 Concrete Technology Lab Manual", "material_type": "Lab Manual", "file_attachment": "/files/CE502_Concrete_Lab.pdf", "description": "Laboratory procedures for slump test and compressive strength testing."}
		],
		"B.E. Electrical & Electronics": [
			{"title": "EE501 Power Electronics & Drives Notes", "material_type": "Lecture Notes", "file_attachment": "/files/EE501_Power_Electronics.pdf", "description": "Thyristors, inverters, choppers, and AC/DC drive control notes."},
			{"title": "EE502 Control Systems Simulation Manual", "material_type": "Lab Manual", "file_attachment": "/files/EE502_Control_Systems.pdf", "description": "MATLAB/Simulink laboratory experiments for Bode plots and Root Locus."}
		],
		"B.E. Electronics & Communication": [
			{"title": "EC501 Embedded Systems & ARM Microcontrollers", "material_type": "Lecture Notes", "file_attachment": "/files/EC501_Embedded_Notes.pdf", "description": "ARM Cortex-M architecture, GPIO interfacing, and RTOS principles."},
			{"title": "EC502 Wireless Communication Lab Guide", "material_type": "Lab Manual", "file_attachment": "/files/EC502_Wireless_Lab.pdf", "description": "S-parameter measurement and antenna radiation pattern lab manual."}
		],
		"B.E. Mechanical Engineering": [
			{"title": "ME501 Thermodynamics & Heat Transfer Notes", "material_type": "Lecture Notes", "file_attachment": "/files/ME501_Heat_Transfer.pdf", "description": "Conduction, convection, radiation heat transfer, and steam turbines."},
			{"title": "ME502 CAD/CAM Solid Modeling Manual", "material_type": "Lab Manual", "file_attachment": "/files/ME502_CAD_CAM_Lab.pdf", "description": "3D SolidWorks and ANSYS finite element analysis lab exercises."}
		],
		"B.Tech AI & Data Science": [
			{"title": "AD501 Deep Learning & Neural Networks Guide", "material_type": "Lecture Notes", "file_attachment": "/files/AD501_Deep_Learning.pdf", "description": "PyTorch, Convolutional Neural Networks (CNNs), and Transformer models."},
			{"title": "AD502 Big Data Analytics & PySpark Manual", "material_type": "Lab Manual", "file_attachment": "/files/AD502_PySpark_Lab.pdf", "description": "Hadoop Distributed File System (HDFS) and PySpark RDD lab notebook."}
		],
		"B.Tech Computer Science & Engineering": [
			{"title": "CS301 Data Structures & AVL Trees Complete Notes", "material_type": "Lecture Notes", "file_attachment": "/files/CS301_Data_Structures.pdf", "description": "Height-balanced BSTs, graph algorithms, and asymptotic time complexity."},
			{"title": "CS302 DBMS Relational Algebra & SQL Lab", "material_type": "Lab Manual", "file_attachment": "/files/CS302_DBMS_Lab.pdf", "description": "SQL joins, indexing, 3NF normalization, and transaction processing."}
		],
		"B.Tech Information Technology": [
			{"title": "IT501 Full-Stack Web Development Notes", "material_type": "Lecture Notes", "file_attachment": "/files/IT501_Web_Dev.pdf", "description": "RESTful API design, Node.js, React framework, and MongoDB integration."},
			{"title": "IT502 Cloud Computing & Docker Lab Manual", "material_type": "Lab Manual", "file_attachment": "/files/IT502_Docker_Cloud.pdf", "description": "Docker containerization, Kubernetes orchestration, and AWS EC2 deployment."}
		]
	}

	# Clear existing test materials
	frappe.db.sql("DELETE FROM `tabCourse Material`")

	for c in courses:
		name = c.get("name")
		course_name = c.get("course_name")
		
		# Match specific items or fallback based on name
		mat_list = materials_map.get(course_name) or materials_map.get(name) or [
			{"title": f"{name} Unit 1-3 Lecture Notes", "material_type": "Lecture Notes", "file_attachment": f"/files/{name}_Notes.pdf", "description": f"Curriculum notes for {course_name}."},
			{"title": f"{name} Academic Laboratory Manual", "material_type": "Lab Manual", "file_attachment": f"/files/{name}_Lab.pdf", "description": f"Lab experiments and reference code for {course_name}."}
		]

		for item in mat_list:
			doc = frappe.get_doc({
				"doctype": "Course Material",
				"title": item["title"],
				"course": name,
				"semester": "Semester 5",
				"material_type": item["material_type"],
				"file_attachment": item["file_attachment"],
				"description": item["description"]
			})
			doc.insert(ignore_permissions=True)
			print(f"CREATED: {item['title']} FOR COURSE {name}")

	frappe.db.commit()
	print("POPUATION COMPLETED SUCCESSFULLY.")

if __name__ == "__main__":
	populate_course_materials()
