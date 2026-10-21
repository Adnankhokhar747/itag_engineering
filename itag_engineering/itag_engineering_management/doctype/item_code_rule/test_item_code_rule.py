# Copyright (c) 2026, Globcom Qatar and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from itag_engineering.itag_engineering_management.item_code_service import reserve_item_code

SERIES_RULES = ("TST990", "TST991", "TST990B")


def _delete_series_rules():
	for name in SERIES_RULES:
		frappe.db.delete("Item Code Reservation", {"rule": name})
		frappe.db.delete("Item Code Rule Segment", {"parent": name})
		frappe.db.delete("Item Code Rule", {"name": name})


class TestItemCodeRule(FrappeTestCase):
	def setUp(self):
		frappe.db.delete("Item Code Rule Segment", {"parent": "Test Valve Rule"})
		frappe.db.delete("Item Code Rule", {"rule_name": "Test Valve Rule"})
		_delete_series_rules()

	def tearDown(self):
		frappe.db.delete("Item Code Rule Segment", {"parent": "Test Valve Rule"})
		frappe.db.delete("Item Code Rule", {"rule_name": "Test Valve Rule"})
		_delete_series_rules()

	def test_create_rule_with_segments(self):
		rule = frappe.get_doc(
			{
				"doctype": "Item Code Rule",
				"rule_name": "Test Valve Rule",
				"is_active": 1,
				"priority": 1,
				"separator": "-",
				"case_conversion": "Upper",
				"segments": [
					{"segment_type": "Product Family", "source_fieldname": "itag_product_family"},
					{"segment_type": "Valve Type", "source_fieldname": "itag_valve_type"},
					{"segment_type": "Sequence", "sequence_digits": 3},
				],
			}
		)
		rule.insert()
		self.assertEqual(len(rule.segments), 3)
		self.assertEqual(rule.segments[2].segment_type, "Sequence")

	def test_at_least_one_sequence_segment_required(self):
		rule = frappe.get_doc(
			{
				"doctype": "Item Code Rule",
				"rule_name": "Test Valve Rule",
				"is_active": 1,
				"priority": 1,
				"segments": [
					{"segment_type": "Product Family", "source_fieldname": "itag_product_family"},
				],
			}
		)
		with self.assertRaises(frappe.ValidationError):
			rule.insert()

	def test_non_admin_cannot_create_rule(self):
		frappe.set_user("Guest")
		try:
			with self.assertRaises(frappe.PermissionError):
				frappe.get_doc(
					{
						"doctype": "Item Code Rule",
						"rule_name": "Test Valve Rule",
						"segments": [{"segment_type": "Sequence", "sequence_digits": 3}],
					}
				).insert()
		finally:
			frappe.set_user("Administrator")

	def test_series_prefix_builds_pattern_and_own_sequence(self):
		tag_plate = frappe.get_doc(
			{
				"doctype": "Item Code Rule",
				"rule_name": "TST990",
				"series_name": "Tag Plate",
				"code_prefix": "990",
				"company": "",
			}
		).insert()
		self.assertEqual(tag_plate.preview_template, "990-#####")
		self.assertEqual(tag_plate.separator, "-")
		self.assertEqual(tag_plate.segments[0].fixed_value, "990")
		self.assertEqual(tag_plate.segments[1].sequence_digits, 5)

		bracket = frappe.get_doc(
			{
				"doctype": "Item Code Rule",
				"rule_name": "TST991",
				"series_name": "Actuator Bracket",
				"code_prefix": "991",
				"company": "",
			}
		).insert()

		self.assertEqual(reserve_item_code(tag_plate.name, {}), "990-00001")
		self.assertEqual(reserve_item_code(tag_plate.name, {}), "990-00002")
		self.assertEqual(reserve_item_code(bracket.name, {}), "991-00001")

	def test_duplicate_series_prefix_is_rejected(self):
		frappe.get_doc(
			{
				"doctype": "Item Code Rule",
				"rule_name": "TST990",
				"series_name": "Tag Plate",
				"code_prefix": "990",
				"company": "",
			}
		).insert()
		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				{
					"doctype": "Item Code Rule",
					"rule_name": "TST990B",
					"series_name": "Other Plate",
					"code_prefix": "990",
					"company": "",
				}
			).insert()

	def test_series_prefix_rejects_separator_characters(self):
		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				{
					"doctype": "Item Code Rule",
					"rule_name": "TST990",
					"code_prefix": "990-1",
					"company": "",
				}
			).insert()
