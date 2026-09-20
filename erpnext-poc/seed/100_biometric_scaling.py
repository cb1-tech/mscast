"""MSCAST POC - 100: M-03 biometric attendance and M-02 finance scaling management.

M-03 ASSUMPTION: no device model was supplied, so the POC models the common pattern - an access
controller that pushes punches into Employee Checkin (device_id on each punch), with ERPNext's
own auto-attendance converting punches into Attendance against a shift. Swapping in a real ESSL /
Matrix / ZKTeco device means pointing it at the same endpoint; nothing downstream changes.

M-02 ASSUMPTION: 'Finance Scaling Management' was never defined by MSCAST. Read here as: can the
business fund the order book it is chasing? The report projects collections from the milestone
schedule against committed outflows and the sanctioned bank limit, and flags the funding gap.
"""
import frappe
from frappe.utils import add_days, add_to_date, flt, get_datetime, nowdate

COMPANY = "MSCAST Engineering Pvt Ltd"
TODAY = nowdate()
DEVICE = "MSCAST-DOOR-01"
BANK_LIMIT = 25000000.0        # HDFC charge of Rs 2.5 Cr per the MCA filing (knowledge base)
log = lambda m: print("[100] " + m, flush=True)


def step(name, fn, *a, **kw):
    try:
        out = fn(*a, **kw)
        frappe.db.commit()
        log("OK   " + name + ((" -> " + str(out)) if out else ""))
        return out or True
    except Exception as e:
        frappe.db.rollback()
        log("FAIL " + name + " :: " + repr(e)[:400])
        return None


def ins(doc, submit=False):
    d = frappe.get_doc(doc)
    d.flags.ignore_permissions = True
    d.flags.ignore_mandatory = True
    d.insert(ignore_if_duplicate=True)
    if submit:
        d.submit()
    return d


def qreport(name, ref_dt, sql, roles=("System Manager", "Accounts Manager", "MSCAST Director")):
    exists = frappe.db.exists("Report", name)
    d = frappe.get_doc("Report", name) if exists else frappe.new_doc("Report")
    d.update({"report_name": name, "ref_doctype": ref_dt, "report_type": "Query Report",
              "is_standard": "No", "module": "Custom", "disabled": 0, "add_total_row": 0,
              "query": sql})
    d.set("roles", [{"role": r} for r in roles])
    d.flags.ignore_permissions = True
    d.save() if exists else d.insert()
    return name


# ------------------------------------------------------------------ M-03
def biometric():
    made = []
    shift = "General Shift (Biometric)"
    if not frappe.db.exists("Shift Type", shift):
        ins({"doctype": "Shift Type", "name": shift, "start_time": "09:00:00",
             "end_time": "18:00:00", "enable_auto_attendance": 1,
             "determine_check_in_and_check_out": "Alternating entries as IN and OUT during the same shift",
             "working_hours_calculation_based_on": "First Check-in and Last Check-out",
             "begin_check_in_before_shift_start_time": 60,
             "allow_check_out_after_shift_end_time": 60,
             "working_hours_threshold_for_half_day": 4,
             "working_hours_threshold_for_absent": 2,
             "process_attendance_after": add_days(TODAY, -30),
             "last_sync_of_checkin": add_to_date(get_datetime(), hours=1)})
        made.append("shift type")

    emps = frappe.get_all("Employee", filters={"status": "Active"}, fields=["name", "employee_name"])
    for e in emps:
        frappe.db.set_value("Employee", e.name, "default_shift", shift)
    frappe.db.commit()

    if frappe.db.count("Employee Checkin"):
        made.append("%d punches already loaded" % frappe.db.count("Employee Checkin"))
    else:
        n = 0
        for day in range(1, 8):
            d = add_days(TODAY, -day)
            if get_datetime(d).weekday() == 6:        # Sunday - holiday list
                continue
            for i, e in enumerate(emps):
                in_t = "%s 09:%02d:00" % (d, 2 + (i * 3) % 25)
                out_t = "%s 18:%02d:00" % (d, 5 + (i * 7) % 40)
                for t, lt in ((in_t, "IN"), (out_t, "OUT")):
                    ins({"doctype": "Employee Checkin", "employee": e.name, "time": t,
                         "device_id": DEVICE, "log_type": lt, "shift": shift,
                         "skip_auto_attendance": 0})
                    n += 1
        made.append("%d punches from device %s" % (n, DEVICE))
    frappe.db.commit()

    before = frappe.db.count("Attendance")
    try:
        frappe.get_doc("Shift Type", shift).process_auto_attendance()
        frappe.db.commit()
        made.append("auto attendance: %d -> %d records" % (before, frappe.db.count("Attendance")))
    except Exception as e:
        made.append("auto attendance failed: " + repr(e)[:160])

    if not frappe.db.exists("Server Script", "MSCAST biometric pull"):
        ins({"doctype": "Server Script", "name": "MSCAST biometric pull",
             "script_type": "Scheduler Event", "event_frequency": "Hourly", "disabled": 1,
             "module": "Custom",
             "script": "# Placeholder for the access-control pull.\n"
                       "# A real ESSL / Matrix / ZKTeco controller pushes punches to\n"
                       "#   /api/method/hrms.hr.doctype.employee_checkin.employee_checkin"
                       ".add_log_based_on_employee_field\n"
                       "# with employee_field_value, timestamp, device_id and log_type.\n"
                       "# Enable this job only if the device cannot push and has to be polled.\n"
                       "frappe.logger().info('MSCAST biometric pull placeholder')\n"})
        made.append("pull job placeholder (disabled)")

    qreport("MSCAST Biometric Attendance Audit", "Employee Checkin", """
select
  c.employee                                      as "Employee:Link/Employee:130",
  c.employee_name                                 as "Name::200",
  date(c.time)                                    as "Date:Date:95",
  c.device_id                                     as "Device::150",
  min(case when c.log_type = 'IN' then time(c.time) end)   as "First IN::100",
  max(case when c.log_type = 'OUT' then time(c.time) end)  as "Last OUT::100",
  count(*)                                        as "Punches:Int:80",
  ifnull((select a.status from `tabAttendance` a where a.employee = c.employee
          and a.attendance_date = date(c.time) and a.docstatus = 1 limit 1), 'not marked')
                                                  as "Attendance::130",
  ifnull((select round(a.working_hours,2) from `tabAttendance` a where a.employee = c.employee
          and a.attendance_date = date(c.time) and a.docstatus = 1 limit 1), 0)
                                                  as "Hours:Float:90"
from `tabEmployee Checkin` c
group by c.employee, date(c.time), c.device_id
order by date(c.time) desc, c.employee
""", ("System Manager", "HR Manager", "HR User", "MSCAST Director"))
    return "; ".join(made)


# ------------------------------------------------------------------ M-02
def finance_scaling():
    sql = """
select
  d.seq_label                                     as "Horizon::150",
  d.particulars                                   as "Particulars::420",
  d.amt                                           as "Amount:Currency:170",
  d.note                                          as "Basis::400"
from (
  select 1 as seq, 'Order book' as seq_label, 'Confirmed orders in hand (booked less billed)' as particulars,
    ifnull((select round(sum(so.grand_total * (100 - ifnull(so.per_billed,0)) / 100), 0)
       from `tabSales Order` so where so.docstatus = 1 and so.status != 'Closed'), 0) as amt,
    'Sales orders, unbilled portion' as note
  union all select 2, 'Order book', 'Open enquiries and quotations not yet won',
    ifnull((select round(sum(grand_total), 0) from `tabQuotation` where docstatus = 1
            and status not in ('Lost','Ordered')), 0),
    'Quotation pipeline - not committed'
  union all select 3, 'Next 90 days', 'Collections scheduled from milestones',
    ifnull((select round(sum(s.billing_amount), 0) from `tabMSCAST Project Schedule Line` s
       where s.status not in ('Collected')
         and s.planned_dispatch_date between date(convert_tz(utc_timestamp(),'+00:00','+05:30'))
             and date_add(date(convert_tz(utc_timestamp(),'+00:00','+05:30')), interval 90 day)), 0),
    'Billing and dispatch schedule on the projects'
  union all select 4, 'Next 90 days', 'Receivables already due or falling due',
    ifnull((select round(sum(outstanding_amount), 0) from `tabSales Invoice`
       where docstatus = 1 and is_return = 0
         and due_date <= date_add(date(convert_tz(utc_timestamp(),'+00:00','+05:30')), interval 90 day)), 0),
    'Open sales invoices by due date'
  union all select 5, 'Next 90 days', 'Committed outflow - open purchase orders not received',
    ifnull((select round(sum(po.grand_total * (100 - ifnull(po.per_received,0)) / 100), 0)
       from `tabPurchase Order` po where po.docstatus = 1 and ifnull(po.per_received,0) < 100), 0),
    'Purchase orders, undelivered portion'
  union all select 6, 'Next 90 days', 'Committed outflow - supplier bills payable',
    ifnull((select round(sum(outstanding_amount), 0) from `tabPurchase Invoice` where docstatus = 1), 0),
    'Open purchase invoices, MSME first'
  union all select 7, 'Next 90 days', 'Committed outflow - payroll and statutory (3 months)',
    ifnull((select round(sum(ss.gross_pay), 0) * 3 from `tabSalary Slip` ss
       where ss.docstatus = 1 and ss.start_date = (select max(start_date) from `tabSalary Slip`
                                                   where docstatus = 1)), 0),
    'Last payroll run extrapolated for a quarter'
  union all select 8, 'Position', 'Cash and bank today',
    ifnull((select round(sum(gl.debit - gl.credit), 0) from `tabGL Entry` gl
       inner join `tabAccount` a on a.name = gl.account
       where gl.is_cancelled = 0 and a.account_type in ('Bank','Cash')), 0),
    'General ledger'
  union all select 9, 'Position', 'Sanctioned bank limit (HDFC charge)',
    {limit}, 'MCA charge register - Rs 2.5 Cr, per the knowledge base'
  union all select 10, 'Headroom', 'Projected net cash over 90 days',
    (
      ifnull((select round(sum(gl.debit - gl.credit), 0) from `tabGL Entry` gl
         inner join `tabAccount` a on a.name = gl.account
         where gl.is_cancelled = 0 and a.account_type in ('Bank','Cash')), 0)
    + ifnull((select round(sum(s.billing_amount), 0) from `tabMSCAST Project Schedule Line` s
         where s.status not in ('Collected')
           and s.planned_dispatch_date between date(convert_tz(utc_timestamp(),'+00:00','+05:30'))
               and date_add(date(convert_tz(utc_timestamp(),'+00:00','+05:30')), interval 90 day)), 0)
    - ifnull((select round(sum(po.grand_total * (100 - ifnull(po.per_received,0)) / 100), 0)
         from `tabPurchase Order` po where po.docstatus = 1 and ifnull(po.per_received,0) < 100), 0)
    - ifnull((select round(sum(outstanding_amount), 0) from `tabPurchase Invoice` where docstatus = 1), 0)
    - ifnull((select round(sum(ss.gross_pay), 0) * 3 from `tabSalary Slip` ss
         where ss.docstatus = 1 and ss.start_date = (select max(start_date) from `tabSalary Slip`
                                                     where docstatus = 1)), 0)
    ),
    'Cash + scheduled collections - committed outflows. Negative means the bank limit has to carry it.'
  union all select 11, 'Capacity', 'Order book covered by one years revenue run rate',
    ifnull((select round(sum(grand_total), 0) from `tabSales Invoice`
       where docstatus = 1 and is_return = 0), 0) * 12,
    'Billed to date annualised - how much of the order book the current run rate can absorb'
) d order by d.seq
""".replace("{limit}", str(BANK_LIMIT))
    name = qreport("MSCAST Finance Scaling - Funding and Capacity", "Sales Order", sql,
                   ("System Manager", "Accounts Manager", "MSCAST Director",
                    "MSCAST Statutory Auditor"))
    for r in frappe.db.sql(sql):
        log("  %-12s %-56s %14s" % (r[0], r[1][:56], r[2]))
    return name


def run():
    step("M-03 biometric attendance chain", biometric)
    step("M-02 finance scaling - funding and capacity", finance_scaling)
    frappe.clear_cache()
    log("SCRIPT 100 DONE")


run()
