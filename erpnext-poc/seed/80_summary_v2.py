"""MSCAST POC - 80: rebuild the daily management summary - correct status logic,
Indian money formatting, and an Attention column so the eye lands on what needs action."""
import frappe

log = lambda m: print("[sum2] " + m, flush=True)
NAME = "MSCAST Daily Management Summary"

SQL = """
select
  d.area                                                    as "Area::120",
  d.indicator                                               as "Indicator::340",
  case
    when d.kind = 'text'  then d.txt
    when d.kind = 'count' then format(d.val, 0)
    when d.val = 0        then 'Rs 0'
    when abs(d.val) >= 10000000 then concat('Rs ', format(d.val / 10000000, 2), ' Cr')
    when abs(d.val) >= 100000   then concat('Rs ', format(d.val / 100000, 2), ' L')
    else concat('Rs ', format(d.val, 0))
  end                                                       as "Value::150",
  d.attn                                                    as "Attention::120"
from (
  select 1 as seq, 'Report' as area, 'Position as at' as indicator, 0 as val, 'text' as kind,
         date_format(curdate(), '%%d %%b %%Y') as txt, '' as attn

  union all select 2, 'Cash', 'Cash and bank balance',
    ifnull((select sum(gl.debit - gl.credit) from `tabGL Entry` gl
       inner join `tabAccount` a on a.name = gl.account
       where gl.is_cancelled = 0 and a.account_type in ('Bank','Cash')), 0),
    'money', '',
    case when ifnull((select sum(gl.debit - gl.credit) from `tabGL Entry` gl
       inner join `tabAccount` a on a.name = gl.account
       where gl.is_cancelled = 0 and a.account_type in ('Bank','Cash')), 0) < 500000
         then 'ACT - low' else 'OK' end

  union all select 3, 'Receivables', 'Outstanding from customers',
    ifnull((select sum(outstanding_amount) from `tabSales Invoice`
       where docstatus = 1 and is_return = 0), 0), 'money', '', 'OK'

  union all select 4, 'Receivables', 'Overdue beyond due date',
    ifnull((select sum(outstanding_amount) from `tabSales Invoice`
       where docstatus = 1 and is_return = 0 and due_date < curdate()), 0), 'money', '',
    case when ifnull((select sum(outstanding_amount) from `tabSales Invoice`
       where docstatus = 1 and is_return = 0 and due_date < curdate()), 0) > 0
         then 'ACT - chase' else 'OK' end

  union all select 5, 'Receivables', 'Falling due in the next 7 days',
    ifnull((select sum(outstanding_amount) from `tabSales Invoice`
       where docstatus = 1 and is_return = 0
         and due_date between curdate() and date_add(curdate(), interval 7 day)), 0), 'money', '',
    case when ifnull((select sum(outstanding_amount) from `tabSales Invoice`
       where docstatus = 1 and is_return = 0
         and due_date between curdate() and date_add(curdate(), interval 7 day)), 0) > 0
         then 'WATCH' else 'OK' end

  union all select 6, 'Receivables', 'Retention held by customers',
    ifnull((select sum(gl.debit - gl.credit) from `tabGL Entry` gl
       where gl.is_cancelled = 0 and gl.account like '%%Retention%%'), 0), 'money', '',
    case when ifnull((select sum(gl.debit - gl.credit) from `tabGL Entry` gl
       where gl.is_cancelled = 0 and gl.account like '%%Retention%%'), 0) > 0
         then 'WATCH - release on certificate' else 'OK' end

  union all select 7, 'Payables', 'Outstanding to suppliers',
    ifnull((select sum(outstanding_amount) from `tabPurchase Invoice` where docstatus = 1), 0),
    'money', '', 'OK'

  union all select 8, 'Payables', 'MSME dues beyond 45 days (s.43B(h) risk)',
    ifnull((select sum(pi.outstanding_amount) from `tabPurchase Invoice` pi
       inner join `tabSupplier` s on s.name = pi.supplier
       where pi.docstatus = 1 and ifnull(s.msme_type,'') != '' and pi.outstanding_amount > 0
         and datediff(curdate(), ifnull(pi.bill_date, pi.posting_date)) > 45), 0), 'money', '',
    case when ifnull((select sum(pi.outstanding_amount) from `tabPurchase Invoice` pi
       inner join `tabSupplier` s on s.name = pi.supplier
       where pi.docstatus = 1 and ifnull(s.msme_type,'') != '' and pi.outstanding_amount > 0
         and datediff(curdate(), ifnull(pi.bill_date, pi.posting_date)) > 45), 0) > 0
         then 'ACT - pay or lose the deduction' else 'OK' end

  union all select 9, 'Payables', 'MSME dues due within the next 15 days',
    ifnull((select sum(pi.outstanding_amount) from `tabPurchase Invoice` pi
       inner join `tabSupplier` s on s.name = pi.supplier
       where pi.docstatus = 1 and ifnull(s.msme_type,'') != '' and pi.outstanding_amount > 0
         and datediff(curdate(), ifnull(pi.bill_date, pi.posting_date)) between 30 and 45), 0),
    'money', '',
    case when ifnull((select sum(pi.outstanding_amount) from `tabPurchase Invoice` pi
       inner join `tabSupplier` s on s.name = pi.supplier
       where pi.docstatus = 1 and ifnull(s.msme_type,'') != '' and pi.outstanding_amount > 0
         and datediff(curdate(), ifnull(pi.bill_date, pi.posting_date)) between 30 and 45), 0) > 0
         then 'WATCH' else 'OK' end

  union all select 10, 'Order book', 'Orders in hand (booked less billed)',
    ifnull((select sum(so.grand_total * (100 - ifnull(so.per_billed,0)) / 100)
       from `tabSales Order` so where so.docstatus = 1 and so.status != 'Closed'), 0), 'money', '', 'OK'

  union all select 11, 'Order book', 'Billed this month',
    ifnull((select sum(grand_total) from `tabSales Invoice`
       where docstatus = 1 and is_return = 0 and month(posting_date) = month(curdate())
         and year(posting_date) = year(curdate())), 0), 'money', '', 'OK'

  union all select 12, 'Projects', 'Open projects',
    (select count(*) from `tabProject` where status = 'Open'), 'count', '', 'OK'

  union all select 13, 'Engineering', 'Drawings sitting with the customer for approval',
    (select count(*) from `tabMSCAST Drawing` where status = 'For Customer Approval'),
    'count', '',
    case when (select count(*) from `tabMSCAST Drawing`
                 where status = 'For Customer Approval') > 0
         then 'WATCH - schedule risk' else 'OK' end

  union all select 14, 'Engineering', 'Drawings still in draft with us',
    (select count(*) from `tabMSCAST Drawing` where status = 'Draft'), 'count', '',
    case when (select count(*) from `tabMSCAST Drawing` where status = 'Draft') > 0
         then 'WATCH' else 'OK' end

  union all select 15, 'Quality', 'Inspection stages pending',
    (select count(*) from `tabMSCAST Inspection Plan` where ifnull(result,'Pending') = 'Pending'),
    'count', '',
    case when (select count(*) from `tabMSCAST Inspection Plan`
                 where ifnull(result,'Pending') = 'Pending'
                   and ifnull(planned_date, curdate()) < curdate()) > 0
         then 'ACT - stage overdue'
         when (select count(*) from `tabMSCAST Inspection Plan`
                 where ifnull(result,'Pending') = 'Pending') > 0 then 'WATCH' else 'OK' end

  union all select 16, 'Quality', 'Inspections rejected or accepted with deviation',
    (select count(*) from `tabMSCAST Inspection Plan`
       where result in ('Rejected','Accepted with deviation')), 'count', '',
    case when (select count(*) from `tabMSCAST Inspection Plan`
                 where result = 'Rejected') > 0 then 'ACT' else 'OK' end

  union all select 17, 'Purchase', 'Purchase orders not fully received',
    (select count(*) from `tabPurchase Order`
       where docstatus = 1 and ifnull(per_received,0) < 100), 'count', '', 'OK'

  union all select 18, 'Billing control', 'BRMs pending certification (payment blocked)',
    (select count(*) from `tabMSCAST BRM` where status = 'Pending'), 'count', '',
    case when (select count(*) from `tabMSCAST BRM` where status = 'Pending') > 0
         then 'ACT - supplier cannot be paid' else 'OK' end

  union all select 19, 'Claims', 'Client claims open',
    (select count(*) from `tabMSCAST Client Claim`
       where status in ('Open','Under discussion','Agreed')), 'count', '',
    case when (select count(*) from `tabMSCAST Client Claim`
                 where status in ('Open','Under discussion','Agreed')) > 0
         then 'WATCH - money on the table' else 'OK' end

  union all select 20, 'Contracts', 'Acceptance certificates awaited from customers',
    (select count(*) from `tabMSCAST Project Certificate` where status = 'Awaited'), 'count', '',
    case when (select count(*) from `tabMSCAST Project Certificate` where status = 'Awaited') > 0
         then 'WATCH - retention locked' else 'OK' end
) d
order by d.seq
"""

d = frappe.get_doc("Report", NAME)
d.query = SQL
d.flags.ignore_permissions = True
d.save()
frappe.db.commit()
log("report query replaced")

rows = frappe.db.sql(SQL)
for r in rows:
    log("  %-14s %-52s %-16s %s" % r)
log("%d rows" % len(rows))
log("DONE")
