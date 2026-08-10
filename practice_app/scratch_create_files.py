import os
import frappe

def create_sample_files():
	frappe.connect()
	frappe.set_user("Administrator")

	site_path = frappe.get_site_path("public", "files")
	os.makedirs(site_path, exist_ok=True)

	# List of course materials to create real files for
	materials = frappe.get_all("Course Material", fields=["name", "title", "course", "file_attachment"])

	dummy_pdf_content = (
		"%PDF-1.4\n"
		"1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj\n"
		"2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj\n"
		"3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R>> endobj\n"
		"4 0 obj <</Length 55>> stream\n"
		"BT /F1 18 Tf 50 700 Td (TIT Engineering - Verified Study Material) Tj ET\n"
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

	file_names = [
		"CE501_Surveying_Notes.pdf",
		"CE502_Concrete_Lab.pdf",
		"EE501_Power_Electronics.pdf",
		"EE502_Control_Systems.pdf",
		"EC501_Embedded_Notes.pdf",
		"EC502_Wireless_Lab.pdf",
		"ME501_Heat_Transfer.pdf",
		"ME502_CAD_CAM_Lab.pdf",
		"AD501_Deep_Learning.pdf",
		"AD502_PySpark_Lab.pdf",
		"CS301_Data_Structures.pdf",
		"CS302_DBMS_Lab.pdf",
		"IT501_Web_Dev.pdf",
		"IT502_Docker_Cloud.pdf"
	]

	for fname in file_names:
		fpath = os.path.join(site_path, fname)
		with open(fpath, "wb") as f:
			f.write(dummy_pdf_content.encode("latin-1"))
		
		# Check if File doc exists in DB, else insert
		file_url = f"/files/{fname}"
		if not frappe.db.exists("File", {"file_url": file_url}):
			file_doc = frappe.get_doc({
				"doctype": "File",
				"file_name": fname,
				"file_url": file_url,
				"is_private": 0
			})
			file_doc.insert(ignore_permissions=True)
		print(f"CREATED REAL FILE: {file_url} AT {fpath}")

	frappe.db.commit()
	print("ALL SAMPLE FILES CREATED SUCCESSFULLY.")

if __name__ == "__main__":
	create_sample_files()
