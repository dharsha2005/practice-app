import frappe

def run():
    try:
        val = frappe.db.get_single_value("System Settings", "setup_complete")
        print(f"SETUP_COMPLETE: {val}")
    except Exception as e:
        print(f"ERROR: {e}")
