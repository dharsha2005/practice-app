import frappe

def run():
    try:
        meta = frappe.get_meta("Employment Type")
        print("SUCCESS: Loaded Employment Type metadata!")
        print("Fields:", [f.fieldname for f in meta.fields])
    except Exception as e:
        print("ERROR:", e)
