# Copyright (c) 2026, Globcom Qatar and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class EngineeringItemRequest(Document):
	def validate(self):
		self.apply_series_from_valve_type()
		self._create_item_from_workflow_action()
		self._guard_item_created_requires_item()

	def _create_item_from_workflow_action(self):
		"""The Desk workflow button "Create Item" only changes workflow_state
		and saves. Create the Item in that same save so the button does what
		its label says."""
		if (
			self.workflow_state != "Item Created"
			or self.created_item
			or not self.has_value_changed("workflow_state")
		):
			return
		from itag_engineering.itag_engineering_management.eir_service import create_item_from_eir

		create_item_from_eir(self.name, eir=self, persist_request=False)

	def apply_series_from_valve_type(self):
		"""The series follows the Valve Type. A Valve Type that has a series
		always wins over a hand-picked rule. A Valve Type with no series
		leaves a free-standing rule in place, and drops a series that belongs
		to a different Valve Type."""
		if self.valve_type:
			rule = frappe.db.get_value("Valve Type", self.valve_type, "item_code_rule")
			if rule:
				self.item_code_rule = rule
			elif self.item_code_rule:
				owner = frappe.db.get_value("Valve Type", {"item_code_rule": self.item_code_rule}, "name")
				if owner and owner != self.valve_type:
					self.item_code_rule = None
		self._set_code_pattern()

	def _set_code_pattern(self):
		if not self.item_code_rule:
			self.code_pattern = None
			return
		self.code_pattern = frappe.db.get_value("Item Code Rule", self.item_code_rule, "preview_template")

	def _guard_item_created_requires_item(self):
		"""Last resort if item creation did not run or did not record the Item."""
		if (
			self.workflow_state == "Item Created"
			and not self.created_item
			and self.has_value_changed("workflow_state")
		):
			frappe.throw(
				_(
					"The Item was not created, so this request cannot move to Item Created. "
					"Select a Valve Type that has an Item Code Rule, then use Create Item again."
				)
			)
