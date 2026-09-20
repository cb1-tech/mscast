# -*- coding: utf-8 -*-
"""The installed base and the bid history.

Neither touches the ledger. Together they are the two things a ten-person
machine builder most needs and least often writes down: every machine it has
built (the revamp and spares pipeline) and why it lost the jobs it lost.
"""
import frappe

def ensure_customer(name):
    if not frappe.db.exists("Customer", name):
        c = frappe.new_doc("Customer")
        c.customer_name = name
        c.customer_type = "Company"
        t = frappe.get_all("Customer", fields=["customer_group", "territory"], limit=1)
        if t:
            c.customer_group = t[0].customer_group
            c.territory = t[0].territory
        c.flags.ignore_permissions = True
        c.insert()
    return name

# ---------------------------------------------------------- installed machines
# serial, customer, site, type, strands, section, commissioned, status,
# last contact, spares billed, contract value, notes
MACHINES = [
    ("MS/CCM/2009/01", "Konark Alloys Pvt Ltd (DEMO)", "Wardha works, Maharashtra", "Billet caster", 2, "100 sq",
     "2009-11-18", "Revamped by us", "2024-03-14", 1840000, 8600000,
     "Original 2-strand. We revamped the WSU and oscillator in 2019. Due another look."),
    ("MS/CCM/2011/02", "Sahyadri Steels Ltd (DEMO)", "Jalna works, Maharashtra", "Billet caster", 2, "110 sq",
     "2011-06-02", "Running", "2025-11-20", 2260000, 9400000,
     "Their first machine with us. Led directly to the 2026 order."),
    ("MS/CCM/2013/03", "Bhilai Rolling Mills Pvt Ltd", "Bhilai, Chhattisgarh", "Billet caster", 3, "125 sq",
     "2013-09-27", "Running", "2024-08-09", 3120000, 14200000,
     "Three strand. Mould level control upgraded 2020. No contact in over a year."),
    ("MS/CCM/2014/04", "Godavari Ispat Ltd", "Peddapalli, Telangana", "Billet caster", 2, "130 sq",
     "2014-12-11", "Running", "2025-06-30", 1470000, 11800000,
     "Asked about a torch cutting upgrade last year. Never followed up."),
    ("MS/CCM/2016/05", "Nagpur Steel & Power Ltd", "Nagpur, Maharashtra", "Billet caster", 4, "130 sq",
     "2016-04-19", "Running", "2026-01-15", 4380000, 19600000,
     "Largest machine we have built. Four strand. Good relationship."),
    ("MS/CCM/2017/06", "Vidarbha Alloys Pvt Ltd", "Chandrapur, Maharashtra", "Round caster", 2, "150 dia",
     "2017-08-30", "Idle", "2024-11-02", 620000, 10200000,
     "Plant running below capacity since 2023. Machine idle, not scrapped."),
    ("MS/CCM/2018/07", "Kalinga Casting Works", "Rourkela, Odisha", "Billet caster", 2, "120 sq",
     "2018-02-14", "Running", "2025-09-18", 980000, 9800000,
     "Buys spares regularly. Candidate for an annual maintenance contract."),
    ("MS/CCM/2019/08", "Surya Metallics Pvt Ltd", "Bhavnagar, Gujarat", "Billet caster", 3, "125 sq",
     "2019-07-22", "Running", "2024-05-27", 1520000, 15400000,
     "Gujarat plant. Long haul for site work but they pay on time."),
    ("MS/CCM/2020/09", "Konark Alloys Pvt Ltd (DEMO)", "Wardha works, Maharashtra", "Billet caster", 2, "130 sq",
     "2020-10-05", "Running", "2026-02-11", 2140000, 13600000,
     "Second machine at the same plant. They buy mould tubes from us every quarter."),
    ("MS/CCM/2021/10", "Bhilai Rolling Mills Pvt Ltd", "Bhilai, Chhattisgarh", "Bloom caster", 2, "200x200",
     "2021-05-16", "Running", "2025-04-08", 1760000, 22400000,
     "Our only bloom caster. Learned a lot; costed badly."),
    ("MS/CCM/2022/11", "Godavari Ispat Ltd", "Peddapalli, Telangana", "Billet caster", 3, "130 sq",
     "2022-11-29", "Running", "2026-03-02", 890000, 17200000,
     "Still inside warranty tail. Spares just starting."),
    ("MS/CCM/2023/12", "Kalinga Casting Works", "Rourkela, Odisha", "Round caster", 2, "180 dia",
     "2023-06-11", "Running", "2025-12-19", 410000, 12900000,
     "Round caster. First of its kind for this customer."),
    ("MS/CCM/2024/13", "Nagpur Steel & Power Ltd", "Nagpur, Maharashtra", "Billet caster", 2, "150 sq",
     "2024-09-03", "Running", "2026-04-22", 260000, 16800000,
     "Newest machine before the two in build."),
    ("MS/CCM/2012/14", "Deccan Extrusions Pvt Ltd (DEMO)", "Aurangabad, Maharashtra", "Billet caster", 1, "7 in dia",
     "2012-03-08", "Decommissioned", "2023-07-30", 340000, 5600000,
     "Aluminium billet caster, replaced by the machine now in build."),
]

added_m = []
for (sn, cust, site, mtype, strands, section, comm, status, last, spares, value, notes) in MACHINES:
    if frappe.db.exists("MSCAST Installed Machine", {"machine_sn": sn}):
        continue
    ensure_customer(cust)
    m = frappe.new_doc("MSCAST Installed Machine")
    m.machine_sn = sn
    m.customer = cust
    m.site_location = site
    m.machine_type = mtype
    m.strands = strands
    m.section_size = section
    m.commissioned_on = comm
    m.warranty_end = frappe.utils.add_years(comm, 2)
    m.status = status
    m.last_contact = last
    m.spares_since = spares
    m.contract_value = value
    m.notes = notes
    # a caster past ten years is a revamp conversation
    age_days = frappe.utils.date_diff(frappe.utils.nowdate(), comm)
    if age_days > 3650 and status in ("Running", "Idle"):
        m.revamp_due = frappe.utils.add_days(frappe.utils.nowdate(), 30)
    m.flags.ignore_permissions = True
    m.insert()
    added_m.append(sn)

print("installed machines added:", len(added_m))

# ------------------------------------------------------------------ bid history
# prospect, machine, strands, section, outcome, quoted, decision, our price,
# our weeks, winner, their price, their weeks, reason, feedback, learning
BIDS = [
    ("Sahyadri Steels Ltd (DEMO)", "Billet caster", 2, "130 sq", "Won", "2026-05-12", "2026-07-03",
     20265000, 44, None, 0, 0, None,
     "Wanted us because the 2011 machine has never given trouble.",
     "Incumbency won it, not price. Protect the installed base."),
    ("Deccan Extrusions Pvt Ltd (DEMO)", "Billet caster", 1, "7 in dia", "Won", "2026-07-08", "2026-08-24",
     14200000, 40, None, 0, 0, None,
     "Replacing the 2012 machine. Asked for the same layout.", ""),
    ("Jindal Panther Steels", "Billet caster", 4, "150 sq", "Lost", "2026-04-02", "2026-06-18",
     34500000, 52, "Concast (India)", 31800000, 44, "Lead time",
     "They said eight weeks earlier delivery was worth the difference.",
     "We lose four-strand jobs on lead time, not price. Fabrication capacity is the constraint."),
    ("Raipur Ispat Udyog", "Billet caster", 2, "125 sq", "Lost", "2026-03-19", "2026-05-06",
     11900000, 42, "Inducto Concast", 10450000, 40, "Price",
     "Twelve percent apart. They bought on price alone.",
     "At the small end we are not competitive against a furnace-plus-caster package."),
    ("Ambika Steel Rolling Mills", "Revamp / upgrade", 2, "110 sq", "Won", "2026-06-25", "2026-08-01",
     3850000, 16, None, 0, 0, None,
     "Chose us because we had the original drawings.", "Revamps are where our history pays."),
    ("Odisha Sponge & Power Ltd", "Billet caster", 3, "130 sq", "Lost", "2026-02-11", "2026-04-28",
     18700000, 48, "Electrotherm (India)", 17900000, 46, "Technical scope",
     "They wanted the melt shop and the caster from one supplier.",
     "We cannot bid a whole melt shop. Partner, or stay out of these."),
    ("Konark Alloys Pvt Ltd (DEMO)", "Spares only", 0, "", "Won", "2026-08-30", "2026-09-06",
     1812480, 4, None, 0, 0, None, "Repeat mould tube order.", ""),
    ("Shakti Steel & Alloys", "Billet caster", 2, "120 sq", "Lost", "2026-01-22", "2026-03-15",
     10800000, 40, "HANI Metallurgy", 8900000, 36, "Price",
     "A Chinese builder quoted eighteen percent below us with shorter delivery.",
     "Chinese pricing at the low end is not something we can answer. Do not chase these."),
    ("Gulf Aluminium Rolling Mill", "Billet caster", 2, "8 in dia", "In progress", "2026-09-04", None,
     16400000, 46, None, 0, 0, None,
     "Export enquiry through the Bahrain agent. Asked for references.",
     ""),
    ("Marathwada Steels Pvt Ltd", "Billet caster", 2, "130 sq", "No bid", "2026-05-28", "2026-06-02",
     0, 0, None, 0, 0, "Capacity - we could not take it",
     "Delivery wanted in twenty weeks. We had nothing free.",
     "Two live projects is our ceiling. Turning work away is a capacity problem, not a sales one."),
    ("Kalinga Casting Works", "Revamp / upgrade", 2, "120 sq", "Won", "2026-07-19", "2026-08-12",
     2940000, 12, None, 0, 0, None, "Mould and oscillator refurbishment.", ""),
    ("Chhattisgarh Metallics Ltd", "Bloom caster", 2, "200x200", "Lost", "2025-12-04", "2026-02-20",
     26800000, 56, "Simplex Castings", 25100000, 50, "References / track record",
     "We have built one bloom caster. They wanted someone who had built ten.",
     "Bloom is not our market until we have three or four references."),
    ("Nagpur Steel & Power Ltd", "Spares only", 0, "", "Won", "2026-06-11", "2026-06-20",
     684000, 6, None, 0, 0, None, "Roll and bearing set.", ""),
    ("Telangana Alloy Steels", "Billet caster", 3, "125 sq", "Lost", "2026-04-30", "2026-07-11",
     19400000, 50, "Concast (India)", 18600000, 42, "Lead time",
     "Four percent on price, eight weeks on delivery. Delivery decided it.",
     "Second loss this year on lead time. The pattern is the point."),
]

added_b = []
for (cust, mtype, strands, section, outcome, bid_date, decision, our_price, our_weeks,
     winner, their_price, their_weeks, reason, feedback, learning) in BIDS:
    if frappe.db.exists("MSCAST Bid Outcome", {"customer_name": cust, "bid_date": bid_date}):
        continue
    b = frappe.new_doc("MSCAST Bid Outcome")
    b.customer_name = cust
    if frappe.db.exists("Customer", cust):
        b.customer = cust
    b.machine_type = mtype
    b.strands = strands
    b.section_size = section
    b.outcome = outcome
    b.bid_date = bid_date
    b.decision_date = decision
    b.our_price = our_price
    b.our_lead_weeks = our_weeks
    if winner:
        b.winner = winner
        b.winner_price = their_price
        b.winner_lead_weeks = their_weeks
    b.reason_lost = reason
    b.customer_feedback = feedback
    b.learning = learning
    if our_price and their_price:
        b.price_gap = round((our_price - their_price) * 100.0 / their_price, 1)
    b.flags.ignore_permissions = True
    b.insert()
    added_b.append(cust)

frappe.db.commit()
print("bid outcomes added:", len(added_b))
print()

won = frappe.db.count("MSCAST Bid Outcome", {"outcome": "Won"})
lost = frappe.db.count("MSCAST Bid Outcome", {"outcome": "Lost"})
print("win / loss so far: %d won, %d lost" % (won, lost))
print("reasons we lose:", frappe.db.sql("""select reason_lost, count(*) c from `tabMSCAST Bid Outcome`
    where outcome='Lost' group by reason_lost order by c desc""", as_dict=True))
print()
print("installed base:", frappe.db.count("MSCAST Installed Machine"), "machines,",
      "revamp leads:", frappe.db.count("MSCAST Installed Machine", {"revamp_due": ["is", "set"]}))
