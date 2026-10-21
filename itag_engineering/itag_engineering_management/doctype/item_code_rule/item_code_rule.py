# Copyright (c) 2026, Globcom Qatar and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint


class ItemCodeRule(Document):
	def before_validate(self):
		# A series prefix means this rule is one numbered block (530-#####),
		# not a free-form segment formula. Build that pattern here, before
		# the mandatory check, so the segments table does not have to be
		# filled in by hand.
		if not self.code_prefix:
			return

		self.code_prefix = str(self.code_prefix).strip()
		digits = cint(self.sequence_digits) or 5
		self.sequence_digits = digits
		self.separator = "-"
		self.preview_template = f"{self.code_prefix}-{'#' * digits}"
		if not self.series_name:
			self.series_name = self.rule_name
		self.set(
			"segments",
			[
				{"segment_type": "Fixed Prefix", "fixed_value": self.code_prefix},
				{"segment_type": "Sequence", "sequence_digits": digits},
			],
		)

	def validate(self):
		self.validate_code_prefix()
		self.validate_has_sequence_segment()

	def validate_code_prefix(self):
		if not self.code_prefix:
			return
		if not str(self.code_prefix).isalnum():
			frappe.throw(_("Series Prefix can only contain letters and numbers."))
		digits = cint(self.sequence_digits) or 5
		if digits < 1 or digits > 10:
			frappe.throw(_("Sequence Digits must be between 1 and 10."))
		duplicate = frappe.db.get_value(
			"Item Code Rule",
			{"code_prefix": self.code_prefix, "name": ["!=", self.name]},
			"name",
		)
		if duplicate:
			frappe.throw(
				_("Series Prefix {0} is already used by Item Code Rule {1}.").format(
					self.code_prefix, duplicate
				)
			)

	def validate_has_sequence_segment(self):
		if not any(s.segment_type == "Sequence" for s in self.segments):
			frappe.throw(_("At least one segment must be of type Sequence."))
