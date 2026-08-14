// Copyright (c) 2026, Dharshan and contributors
// For license information, please see license.txt

frappe.ui.form.on("Fee", {
	refresh: function (frm) {
        frm.add_custom_button('Send Welcome Email', () => {
            frappe.msgprint('Email Sent!');
        }, 'Actions');
    }
}); 