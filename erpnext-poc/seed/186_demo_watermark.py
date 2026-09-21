# -*- coding: utf-8 -*-
"""Mark this site as a demonstration, so every MSCAST print carries the watermark.

Review finding A2. The watermark itself now lives in the app (mscast_erp.demo)
and is re-applied on every migrate - as a seed script it was stripped by the
first `bench migrate`, found by an upgrade test on 21 Sep 2026. This script only
flips the switch; a production site never has it.
"""
import frappe
from frappe.installer import update_site_config
from mscast_erp import demo

update_site_config("mscast_demo", 1)
frappe.local.conf.mscast_demo = 1
demo.apply()
