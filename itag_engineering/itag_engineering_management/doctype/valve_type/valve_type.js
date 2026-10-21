// Copyright (c) 2026, Globcom Qatar and contributors
// For license information, please see license.txt

frappe.ui.form.on("Valve Type", {
	refresh(frm) {
		frm.set_query("item_code_rule", () => {
			return {
				filters: [
					["Item Code Rule", "is_active", "=", 1],
					["Item Code Rule", "code_prefix", "is", "set"],
				],
			};
		});
	},
});
