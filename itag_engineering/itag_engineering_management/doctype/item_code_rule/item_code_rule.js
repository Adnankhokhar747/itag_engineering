// Copyright (c) 2026, Globcom Qatar and contributors
// For license information, please see license.txt

frappe.ui.form.on("Item Code Rule", {
	code_prefix(frm) {
		apply_series_pattern(frm);
	},
	sequence_digits(frm) {
		apply_series_pattern(frm);
	},
});

function apply_series_pattern(frm) {
	const prefix = (frm.doc.code_prefix || "").trim();
	if (!prefix) {
		return;
	}
	const digits = frm.doc.sequence_digits || 5;
	frm.set_value("separator", "-");
	frm.set_value("preview_template", `${prefix}-${"#".repeat(digits)}`);
	frm.clear_table("segments");
	frm.add_child("segments", { segment_type: "Fixed Prefix", fixed_value: prefix });
	frm.add_child("segments", { segment_type: "Sequence", sequence_digits: digits });
	frm.refresh_field("segments");
}
