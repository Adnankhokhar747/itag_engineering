# Copyright (c) 2026, Globcom Qatar and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class ValveType(Document):
	def validate(self):
		self.validate_one_series_per_valve_type()

	def validate_one_series_per_valve_type(self):
		if not self.item_code_rule:
			return
		other = frappe.db.get_value(
			"Valve Type",
			{"item_code_rule": self.item_code_rule, "name": ["!=", self.name]},
			"name",
		)
		if other:
			frappe.throw(
				_("Item Code Series {0} is already used by Valve Type {1}.").format(
					self.item_code_rule, other
				)
			)
