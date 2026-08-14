// Copyright (c) 2026, Dharshan and contributors
// For license information, please see license.txt

frappe.ui.form.on("Marks", {
	setup(frm) {
		frm.set_query("student", function() {
			if (frm.doc.semester) {
				return {
					filters: {
						"semester": frm.doc.semester
					}
				};
			}
			return {};
		});
	}
});