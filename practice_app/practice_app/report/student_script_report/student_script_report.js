// Copyright (c) 2026, Dharshan and contributors
// For license information, please see license.txt

frappe.query_reports["Student Script Report"] = {
	filters: [
		{
			fieldname: "department",
			label: __("Department"),
			fieldtype: "Select",
			options: "\nCSE\nIT\nECE\nEEE\nMECH\nCIVIL\nAIDS"
		},
		{
			fieldname: "year",
			label: __("Year"),
			fieldtype: "Select",
			options: "\nI\nII\nIII\nIV"
		},
		{
			fieldname: "semester",
			label: __("Semester"),
			fieldtype: "Select",
			options: "\n1\n2\n3\n4\n5\n6\n7\n8"
		}
	]
};
