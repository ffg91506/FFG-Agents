import json, re, sys, html
from collections import defaultdict, OrderedDict
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

TODAY = "2026-10-26"
SCR = sys.argv[1]
OUT_DOCX = sys.argv[2]
OUT_HTML = sys.argv[3]

MB = "https://thefivefoldgroup-team.monday.com/boards/18421619257/pulses/"
TB = "https://thefivefoldgroup-team.monday.com/boards/18389952810/pulses/"
PB = "https://thefivefoldgroup-team.monday.com/boards/18389952830/pulses/"
QB = "https://thefivefoldgroup-team.monday.com/boards/18389952868/pulses/"

CLIENTS = OrderedDict([
    ("JVP", "JVP – Johnston Vidal Projects"),
    ("DMCS", "DMCS – Design Management & Construction"),
    ("JLI", "JLI – Johnston Landscapes Inc"),
    ("Cintima", "Cintima"),
    ("Shelfie", "Shelfie"),
    ("The Feel", "The Feel"),
    ("Seymour Butz", "Seymour Butz"),
    ("FFG", "FFG – Five Fold Group (internal books)"),
])

def fmt(d):
    return f"{int(d[5:7])}/{int(d[8:10])}" if d else "no due date"

def short_rep(p):
    if not p: return "UNASSIGNED"
    names = [x.strip() for x in p.split(",")]
    m = {"Jay pithiya": "Jay", "Customer Support": "Customer Support", "Ayrica Avery": "Ayrica",
         "Joanie Guadalyn Abella-Poserio": "Joanie"}
    out = []
    for n in names:
        s = m.get(n, n)
        if s not in out: out.append(s)
    return " + ".join(out)

def client_of(name):
    for k in CLIENTS:
        if name.upper().startswith(k.upper()): return k
    return "Other"

def task_of(name):
    return re.sub(r"^\s*[^—\-:]+?\s*[—\-:]\s*", "", name, count=1).strip()

def status_of(v):
    if isinstance(v, dict): return "INVALID LABEL"
    return v or "No status"

items = json.load(open(f"{SCR}/monthly.json"))["items"]
rows = []
for it in items:
    cv = it["column_values"]
    rows.append(dict(id=it["id"], name=it["name"].strip(), group=it["group"]["title"],
                     due=(cv.get("date4") or "")[:10], status=status_of(cv.get("status")),
                     rep=short_rep(cv.get("person")), note=(cv.get("text_mm567v3c") or "").replace("\n", " ").strip()))

# ---------------------------------------------------------------- doc model
# Each section: title, intro, list of (heading or None, [ (main, [subs]) ])
sections = []

# ---------- Section 0: Ayrica
def L(main, *subs): return (main, [("Link: " + s if s.startswith("https://") else s) for s in subs if s])

ayrica = [
 ("Tax returns approved & paid (\"Waiting to Submit\") but not filed – P1 Compliance", [
  L("PhotosGraphix Inc (Steven Webster) – 2025 C-Corp return – last update 9/2", "Action: send to Ke for e-file today and set status to Submitted when confirmed.", TB + "11583142147"),
  L("PhotosGraphix Inc (Steven Webster) – 2024 C-Corp return – last update 8/31", "Action: send to Ke for e-file today.", TB + "11720040595"),
  L("M Webb Entertainment Inc (Marlon Webb) – 2023 S-Corp return – last update 9/14", "Action: send to Ke for e-file today.", TB + "11992617869"),
  L("M Webb Entertainment Inc (Marlon Webb) – 2024 S-Corp return – last update 9/11", "Action: send to Ke for e-file today.", TB + "11992588593"),
  L("M Webb Entertainment Inc (Marlon Webb) – 2025 S-Corp return – last update 9/14", "Action: send to Ke for e-file today.", TB + "11983063730"),
  L("Montlake Studios (Steven Xiao) – 2025 LLC return – last update 10/7", "Action: confirm the filer and submit.", TB + "11633157619"),
  L("Gorgeous by Zeina Hair Salon (Zeina Sobh) – 2025 return – last update 10/22", "Action: confirm the filer and submit. Entity Type is blank, so fill it in.", TB + "13165870695"),
  L("The Baby Lounge LLC (Zeina Sobh) – 2025 return – last update 10/22", "Action: confirm the filer and submit. Entity Type is blank.", TB + "13165824972"),
  L("Your Nursing Career LLC (Zeina Sobh) – 2025 return – last update 10/22", "Action: confirm the filer and submit. Entity Type is blank.", TB + "13165869177"),
 ]),
 ("Approvals waiting on you – P1", [
  L("Breanna Colvin – IRS lien warning – reply draft waiting on you since 10/5",
    "Action: approve or edit Customer Support's draft so they can send it.",
    "Fix first: the item title says 2023 but the draft says 2024. Confirm the year.", TB + "13200570673"),
  L("BDGE Enterprise – California Statement of Information final notice (was due ~8/31)",
    "Action: reply \"yes, file it\" so Customer Support can file the SOI today. A late SOI risks penalties and suspension.", PB + "12887191441"),
  L("AJ Wealth LLC – FTB suspension – revivor plan waiting on you since 9/16",
    "Action: approve the plan: file the 2023–2025 returns, pay the balance, then file FTB 3557.",
    "Then: Customer Support gathers the docs and Jay prepares the returns.", PB + "12872064342"),
  L("Yehuda Duenyas – 2021 amendment denial (IRS Letter 324C) + 2025 filings + LLC closure + LA business renewal",
    "Action: assign your 4-point plan from 10/13:",
    "• Jay – compare the 2021 1040X to the IRS transcript and recommend a response",
    "• Customer Support – confirm 2025 personal and S-Corp acceptance status",
    "• Ayrica – decide whether 2025 can be the final LLC year",
    "• Customer Support – pull the LA business renewal notice and confirm the reporting year", TB + "13281409383"),
 ]),
 ("Information only you can provide (Jay is blocked)", [
  L("JVP – $80,000 wire in, 10/6 (BOA-4076)", "Action: tell Jay who it's from and what it's for.", MB + "13351637553"),
  L("JVP – $41,000 Crestmont Ave ACH credit, 10/8 (BOA-4076)", "Action: tell Jay which job or customer it applies to."),
  L("JVP – $150 book transfer in, 10/8 (BOA-4076)", "Action: identify the source."),
  L("JVP – $145 mobile deposit, 10/12 (BOA-4076)", "Action: identify the customer."),
  L("JVP – Check #1595, $8,135, 10/5 (BOA-4076)", "Action: tell Jay the payee and job."),
  L("JVP – Check #4094, $4,419, 10/5 (BOA-4089, JGA Electric)", "Action: confirm the job, and whether it cleared."),
  L("JVP – Check #4097, $400, 10/13 (BOA-4089, F G Trucking)", "Action: confirm the job, and whether it cleared."),
  L("DMCS – $404.30 ATM deposit, 9/22 (BOA-0986)", "Action: tell Jay what the deposit is.", MB + "13351641029"),
 ]),
 ("JVP – September 2026 Corrections – Jay replied 10/9, waiting on you", [
  L("Recommended status change: Sent for Review → Missing Information (needs your OK)",
    "Update to post: \"Need Glen Oaks escrow statement to reconcile September. Also need the September loan statements (Rivian R1T, Chevy Tahoe, Transit Van).\"", MB + "13233867684"),
  L("Escrow $288,139.71 (jumped $232,825 in August)", "Action: send Jay the Glen Oaks escrow statements."),
  L("Undeposited Funds – Liz Katzer – $38,180 payment (5/17) – no matching bank deposit", "Action: tell Jay whether to delete it."),
  L("Undeposited Funds – Josh Shenk – $81,650 payment (5/17) – no matching bank deposit", "Action: tell Jay whether to delete it."),
  L("BOA-4089 uncleared check #4089 – Magnolia Hernandez – $150 (8/5)", "Action: confirm whether it's valid or voided. The 3 uncleared checks cause the −$1,755.30 balance."),
  L("BOA-4089 uncleared check #4094 – JGA Electric – $4,419 (8/24)", "Action: confirm whether it's valid or voided."),
  L("BOA-4089 uncleared check #4097 – F G Trucking – $400 (9/16)", "Action: confirm whether it's valid or voided."),
  L("Petty Cash $26,220 – all withdrawals were booked to petty cash, but no cash expenses are recorded", "Action: send the cash expenses, or confirm the cash on hand."),
  L("Intercompany – Jay says DMCS now owes JVP $39,887 (after the 7/31/25 offset)", "Action: confirm the balance with DMCS."),
  L("D.W. Johnston Construction −$139,430 credit (91+ days) – no open invoices", "Action: tell Jay whether to create an invoice or reclass it."),
  L("Michael Balzary NKSFB LLC −$6,375 credit – no open invoices", "Action: tell Jay whether to create an invoice or reclass it."),
  L("Other Tax Payable $16,920.08 – growing monthly, Jay can't find the source in ADP", "Action: tell Jay how to clear it, and whether to adjust for the CPA's 2025 payroll tax JE."),
  L("Other Deduction $12,136.48 – growing monthly, Jay can't find the source in ADP", "Action: tell Jay how to clear it."),
  L("Rivian R1T loan – September payment missing (balance $12,515.77 since August)", "Action: send Jay the September statement."),
  L("Chevrolet Tahoe loan – September payment missing (balance $48,233.76 since August)", "Action: send Jay the September statement."),
  L("Transit Van loan – September payment missing (balance $37,679.76 since August)", "Action: send Jay the September statement."),
  L("Loan payments total – $4,625.63 recorded in September vs $10,000 monthly budget", "Action: confirm the correct monthly debt payments."),
  L("Interest expense −$2,696.24 – Tahoe (5599) May and Sept payments weren't paid from the business account", "Action: tell Jay how those payments were made."),
  L("Travel $6,339.14 vs $2,833 budget", "Action: mark which travel is job travel and which is personal (Jay attached the report)."),
  L("Billable Expense Income $6,359.63 vs $12,417 budget", "Action: review Jay's unbilled charges list and say which to invoice."),
 ]),
 ("JVP – 2025 Corrections & Close – Jay replied 10/8, waiting on you", [
  L("Recommended status change: Sent for Review → Missing Information (needs your OK)",
    "Update to post: \"Reclasses done. Need Ayrica's guidance on 3 items before closing 2025.\"", MB + "13233890457"),
  L("Unapplied Cash $153,748.65 – the remaining difference is 2024 payments vs 2025 invoices", "Action: tell Jay how to handle the year crossover."),
  L("Employer 401(k) contributions $5,652 – Jay can't find them in Office Expense", "Action: tell Jay where the CPA booked them."),
  L("401(k) plan setup costs $2,250 – Jay can't find them in QuickBooks", "Action: tell Jay where they were coded."),
 ]),
 ("Your other open items", [
  L("Lorie Nijjar – send the register of deposits you promised 10/8", "Action: send it, then decide whether the 2024 return needs an amendment.", TB + "13245127158"),
  L("Latiesha Martin – choose a collections agency (stale since 8/28)",
    "Options: Mesa Revenue Partners at 20% (35% if litigation; client pays filing fees). Benjamin, Chaise & Associates at 30% (up to 50% on small claims, arbitration clause, delayed payouts). Lawson Hamilton at 40%.",
    "Suggested action: pick Mesa Revenue (lowest rate). Customer Support then sends the signed assignment and tells Latiesha.", PB + "12916131287"),
  L("James Cherry – abandoned corporation request (stale since 7/27)",
    "Facts: he says he paid via Cash App years ago. No records exist in Dubsado or Dropbox.",
    "Suggested action: have Customer Support ask him for the Cash App receipt. If it's verified, open a new formation order. If not, send a polite close-out reply and close the item.", PB + "12472519909"),
  L("JLI (Chad Johnston) – LA City tax notices (stale since 7/22)",
    "Suggested action: give Chad a deadline (e.g. 11/2) to confirm the address change with the City. If he doesn't, ask his OK to file the $200 zero return, which stops the notices.", PB + "12606997236"),
  L("Amex employee card ending 11013 – identity confirmation (60-day notice sent 8/11, deadline ~10/10)",
    "Suggested action: check whether the card is still active. If it is and still needed, call Amex directly with the employee's details (never put SSNs in monday). If it was cancelled, close the item.", PB + "12774691382"),
  L("Regus – any extra names for mail and parcel delivery? (stale since 8/11)",
    "Suggested action: reply \"no additions\" or list the names, so Customer Support can update MyRegus and close the item.", PB + "12774877167"),
  L("Southbay Electrophysiology (Duane Bridges) – in Urgent with no status and no date received",
    "Action: set the status and the received date.", TB + "13139262935"),
 ]),
]
sections.append(("For Ayrica – Decisions & Your Items",
                 "Only items that need you. One bullet per customer or task.", ayrica))

# ---------- Section 1: Inbound
inbound = [
 ("Monthly Client Board › Inbound", [
  L("JVP – Deposit Details Clarification – Customer Support / Ayrica",
    "Next step: duplicate of \"JVP – get transaction details from Ayrica\". Merge into one item; the details are in Ayrica's list above.",
    "Update to post: \"Merged with the W/E 10/20 missing-info item. Waiting on Ayrica for deposit and check details.\"",
    "Recommended status: Waiting On Internal Team", MB + "13306212468"),
  L("JVP – Get Transaction Details from Ayrica – Customer Support / Ayrica",
    "Next step: keep this as the main item. Close it once Ayrica sends the details to Jay.",
    "Update to post: \"Waiting on Ayrica: $80,000 wire, $41,000 ACH, $150, $145, checks #1595, #4094, #4097.\"", MB + "13351637553"),
  L("JVP – Unclear Transactions – Jay – no due date",
    "Next step: compare Jay's 9/28 list with the W/E 10/20 list. Merge it if it's the same, otherwise add a due date.",
    "Update to post: \"Jay asked for review on 9/28. Checking overlap with the W/E 10/20 list.\"", MB + "13153886583"),
  L("JVP – September 2026 Corrections – Jay",
    "Next step: Ayrica answers the open questions (see For Ayrica).",
    "Recommended status: Missing Information. Update: \"Need escrow statement to reconcile September.\"", MB + "13233867684"),
  L("JVP – 2025 Corrections & Close – Jay",
    "Next step: Ayrica answers the 3 open questions (see For Ayrica).",
    "Recommended status: Missing Information.", MB + "13233890457"),
  L("DMCS – Get Deposit Details from Ayrica – Customer Support",
    "Next step: Ayrica identifies the $404.30 ATM deposit from 9/22.",
    "Update to post: \"Waiting on Ayrica: $404.30 ATM deposit 9/22 (BOA-0986).\"", MB + "13351641029"),
  L("DMCS – Payroll Reconciliation – Jay",
    "Next step: Customer Support requests the missing payroll reports from DMCS (the client).",
    "Update to post: \"Requested from client: payroll reports for check #50607 ($4,412.99, 9/2), check #50608 ($438.90, 9/18), and the April 2026 payroll report.\"",
    "Recommended status: Waiting on Client", MB + "12941281239"),
  L("Anomaly Studios Inc – S-Corp Election Letter & $800 Estimated Tax – Customer Support / Ayrica",
    "Next step: Ayrica put this on hold 9/28. Schedule the Q3 meeting Emily asked for, then close.",
    "Update to post: \"IRS accepted S-Corp eff. 1/1/26. Advice sent 9/24. Client requested a Q3 meeting.\"", MB + "13072552633"),
 ]),
 ("Tax Board › Inbound", [
  L("Dany R – LA County Letter – Customer Support",
    "Next step: follow up for the scanned letter (promised 10/4) and confirm the 10/15 payment came in.",
    "Update to post: \"Installments: $500 paid 10/3, next due 10/15. Waiting on the scanned LA County letter.\"",
    "Recommended status: Waiting on Client", TB + "13200566530"),
  L("Breanna Colvin – IRS Notice / Taxes Not Filed – Customer Support",
    "Next step: send the reply once Ayrica approves it. Fix the year in the title.",
    "Update to post: \"Reply draft sent to Ayrica 10/5 for approval.\"", TB + "13200570673"),
  L("JVP – J&M 2024 Associates (Cannonball) K-1 – Ayrica",
    "Next step: save the K-1 to the partner's 2025 tax folder, fill in Tax Year and Entity Type, then move the item out of Inbound.",
    "Update to post: \"K-1 received from Chad 9/15. Saved to [folder].\"", TB + "13072539802"),
  L("PhotosGraphix Inc – \"DRAFT: 2025 Tax Return Filing\" – Customer Support",
    "Next step: this looks like a duplicate of the Urgent PhotosGraphix 2025 item. Confirm, then close.",
    "Update to post: \"Duplicate of 11583142147. Closed.\"", TB + "13107760195"),
  L("Lorie Nijjar – 2024 Business Income Question – Ayrica",
    "Next step: Ayrica sends the register of deposits.",
    "Update to post: \"Client questioned Schedule C income. Explained 10/8. Deposit register to follow.\"", TB + "13245127158"),
  L("Yehuda Duenyas – Claim Denial & Other Items – Ayrica",
    "Next step: assign the 4 tasks (see For Ayrica) and create a Project Management item.",
    "Update to post: \"Tasks assigned: [names/dates].\"", TB + "13281409383"),
 ]),
 ("Project Management › Inbound Orders", [
  L("Crista Jackson – 2025 Tax Return Filing – Customer Support", "Next step: write the Summary and say what we're waiting on from the client.", PB + "13270036251"),
  L("Crista Jackson – Tax Reduction Service – Customer Support + Jay", "Next step: write the Summary. Statements were saved 10/14, so Jay starts the review.", PB + "13284045918"),
  L("Mariah Williams – Corporate Compliance Lead – Customer Support", "Next step: rename to \"Mariah Williams – [service]\", write the Summary, and follow up with the lead today.", PB + "13342103158"),
  L("Antiwne Grant – 2021 Tax Return Filing – Customer Support", "Next step: rewrite the Summary for 2021. It currently shows the 2025 text.", PB + "12584348952"),
  L("Antiwne Grant – 2022 Tax Return Filing – Customer Support", "Next step: rewrite the Summary for 2022.", PB + "12584359866"),
  L("Antiwne Grant – 2023 Tax Return Filing – Customer Support", "Next step: rewrite the Summary for 2023.", PB + "12584359880"),
  L("Antiwne Grant – 2024 Tax Amendment – Customer Support + Jay", "Next step: docs were saved 7/27, so Jay can prepare the amendment.", PB + "12584357235"),
  L("Antiwne Grant – 2025 Tax Return Filing – Customer Support", "Next step: follow up on the PWWS decision and resubmit the rejected return per Ayrica.", PB + "11996023497"),
  L("Devonte Gordon – 2025 Tax Return Filing – Customer Support", "Next step: post the outcome of the 7/22 client meeting.", PB + "11714370855"),
  L("Dany Rizkallah – 2025 Tax Return Filing – Customer Support", "Next step: link to the Tax Board item (installment plan) and post a current update.", PB + "11552462532"),
  L("Oren Harris – 2025 Tax Return Filing – Customer Support", "Next step: check the Tax Board \"Review Notes\" status and follow up with the client.", PB + "12047757574"),
  L("Richard Lewis – 2025 Tax Return Filing – Sent to Account Manager", "Next step: Ayrica confirms the payment/approval status for 2019–2025.", PB + "11280184164"),
  L("Eric & Mary – 2023 Tax Amendment – Sent to Account Manager", "Next step: Ayrica confirms whether the amendment is still active.", PB + "10803619764"),
  L("Shakinah Starks – Reconnect QBO Bank Accounts – Customer Support", "Next step: follow-up #4 for accounts 4224 and 4047. Escalate to Ayrica if there's no reply by Friday.", PB + "12706414617"),
  L("Tax Archive Project (Dropbox → Dubsado) – Customer Support", "Next step: post the remaining count (21 as of 8/21) and a target completion date.", PB + "12338469140"),
  L("American Express – Replacement Card – Customer Support", "Next step: confirm the new card arrived, then close.", PB + "12645615672"),
  L("JVP Loan – Create Bylaws for JLI – Ayrica", "Next step: post the closing status of the Sunwest loan and confirm the $23.80 invoice was paid.", PB + "12587353817"),
 ]),
 ("QBO CRM › Inbound", [
  L("Jean Roberts – Declined Payment (10/21) – Customer Support – no status",
    "Next step: set the status to Declined and send the 1st reminder.",
    "Update to post: \"Declined 10/21. 1st reminder sent [date].\"", QB + "13352417037"),
  L("Glatzer Prod – Cancelled in QBO – resolved", "Next step: move to October 2026.", QB + "12937813633"),
  L("Rayshawn Reed – Declined Payment (8/31) – now Successful", "Next step: move to October 2026.", QB + "12938055021"),
  L("Rayshawn Reed – Send 2nd Text Reminder – Successful", "Next step: move to October 2026.", QB + "12970042847"),
  L("Rayshawn Reed – Email Reminder to Update CC – Successful", "Next step: move to October 2026.", QB + "12969987168"),
  L("Rayshawn Reed – Send 3rd Text Reminder – Successful", "Next step: move to October 2026.", QB + "13001087081"),
  L("Ray Reed – Update Credit Card Information – Successful", "Next step: move to October 2026.", QB + "13020531347"),
  L("Rayshawn Reed – Declined Payment, August Subscription – Cancelled", "Next step: move to October 2026.", QB + "13042983889"),
  L("Rayshawn Reed – Declined Payment (9/17) – Cancelled", "Next step: move to October 2026.", QB + "13072575688"),
  L("Aaron & Danielle – Cancel QBO – Cancelled", "Next step: confirm cancellation notice and approval are documented, then move to October 2026.", QB + "13128692092"),
  L("FFG – Pay QBO Using Capital One Spark – Successful", "Next step: move to October 2026.", QB + "13128721749"),
  L("Peter Glatzer – Update Credit Card Info – Cancelled", "Next step: confirm whether this is Glatzer Productions or Shft Media (Shft shows Declined in October), then move.", QB + "13200570582"),
  L("BDGE – Update Credit Card Info (10/13) – Cancelled", "Next step: confirm the BDGE subscription status (see Organization), then move.", QB + "13274354003"),
  L("BDGE – Update Credit Card Info (10/20) – Cancelled", "Next step: duplicate of the 10/13 item. Close or merge.", QB + "13334034710"),
 ]),
]
sections.append(("Inbound Customer Service to Resolve",
                 "One bullet per item: the next step, plus the update to post.", inbound))

# ---------- Section 2: Missing info
wc_lines = []
for r in sorted([r for r in rows if r["status"] == "Waiting on Client"], key=lambda x: (x["name"], x["due"])):
    c = client_of(r["name"])
    acct = re.sub(r"^(Download/Request|Reconcile)\s*-?\s*", "", task_of(r["name"])).strip()
    act = ("Internal FFG account: Ayrica or Customer Support downloads the statement." if c == "FFG"
           else "Send the client a reminder and log the date in the update.")
    wc_lines.append(L(f"{CLIENTS.get(c, c)} – {acct} – due {fmt(r['due'])} ({r['group']})", f"Rep: {r['rep']}. Action: {act}", MB + r["id"]))
wc_lines += [
 L("DMCS – payroll reports for check #50607 ($4,412.99) and #50608 ($438.90), plus the April 2026 report – requested 10/9", "Rep: Customer Support. Action: request them from the client and log the date.", MB + "12941281239"),
 L("Dany R – scanned LA County letter – promised 10/4", "Rep: Customer Support. Action: follow up.", TB + "13200566530"),
 L("Dany R – 10/15 installment payment", "Rep: Customer Support. Action: confirm it was received.", TB + "13200566530"),
 L("Yolanda Bevini – response on the IRS letter for the 2025 return – waiting since 10/2", "Rep: Customer Support. Action: note exactly what we need, then follow up.", TB + "13072548678"),
 L("Beth Bassil Argueta – 2025 federal return status – waiting since 10/2", "Rep: Ayrica. Action: note what we're waiting on, then follow up.", TB + "13153965629"),
 L("Shakinah Starks – reconnect QBO bank account 4224", "Rep: Customer Support. Action: follow up #4.", PB + "12706414617"),
 L("Shakinah Starks – reconnect QBO bank account 4047", "Rep: Customer Support. Action: follow up #4.", PB + "12706414617"),
 L("JLI (Chad Johnston) – confirm the registered address with LA City", "Rep: Ayrica. Action: follow up with a deadline.", PB + "12606997236"),
]

wi_lines = []
for r in sorted([r for r in rows if r["status"] in ("Waiting On Internal Team", "Missing Information")], key=lambda x: (x["name"], x["due"])):
    c = client_of(r["name"])
    wi_lines.append(L(f"{CLIENTS.get(c, c)} – {task_of(r['name'])} – due {fmt(r['due'])} ({r['group']})",
                      f"Rep: {r['rep']}. Action: name who internally owes what, or mark Done if it's already complete.", MB + r["id"]))
wi_lines += [
 L("JVP – deposit and check details (7 items) – waiting on Ayrica", "Action: listed one by one under For Ayrica."),
 L("DMCS – $404.30 ATM deposit, 9/22 – waiting on Ayrica", "Action: listed under For Ayrica."),
]

mbs = defaultdict(list)
for r in rows:
    if r["status"] == "Missing Bank Statements":
        acct = re.sub(r"^(Download/Request|Reconcile)\s*-?\s*", "", task_of(r["name"])).strip()
        mbs[(client_of(r["name"]), acct)].append(r)
ORDER = ["June 2026", "July 2026", "August 2026", "September 2026", "October 2026"]
mbs_lines = []
for (c, acct), rs in sorted(mbs.items(), key=lambda kv: (list(CLIENTS).index(kv[0][0]) if kv[0][0] in CLIENTS else 99, kv[0][1])):
    rs = sorted(rs, key=lambda x: x["due"])
    hint = "Note says waiting on client." if any("waiting on client" in x["note"].lower() for x in rs) else "No note says who we're waiting on."
    subs = [f"{hint} Customer Service: change the status to Waiting on Client or Waiting On Internal Team."]
    for x in rs:
        subs.append(f"{x['group']} – {task_of(x['name'])} – due {fmt(x['due'])} – {x['rep']}")
    mbs_lines.append((f"{CLIENTS.get(c, c)} – {acct}", subs))

sections.append(("Missing Information – Waiting on Client", "Client – Document missing – Due date", [(None, wc_lines)]))
sections.append(("Missing Information – Waiting on Internal Team", "Client – Item missing – Due date", [(None, wi_lines)]))
sections.append(("ALERT: \"Missing Bank Statements\" – Customer Service to Confirm Client vs. Internal",
                 f"{sum(len(v) for v in mbs.values())} tasks on {len(mbs)} accounts. One bullet per account, with each open task underneath.",
                 [(None, mbs_lines)]))

# ---------- Section 3: Organization
nodate = [r for r in rows if not r["due"]]
invalid = [r for r in rows if r["status"] == "INVALID LABEL"]
pause = [r for r in rows if r["status"] == "Pause Work"]
old_nostatus = [r for r in rows if r["group"] in ORDER[:4] and r["status"] == "No status"]
old_sfr = [r for r in rows if r["group"] in ORDER[:4] and r["status"] == "Sent for Review"]
oct_nostatus_future = [r for r in rows if r["group"] == "October 2026" and r["status"] == "No status" and r["due"] and r["due"] > TODAY]

pause_by = defaultdict(list)
for r in pause:
    pause_by[re.split(r"\s+[-–—]\s+", r["name"])[0].strip()].append(r)

org = []
org.append(("Monthly Client Board – Due Date Missing", [
    L(f"{r['group']} – {r['name']} – Due Date Missing", f"Rep: {r['rep']}. Action: add a due date.") for r in sorted(nodate, key=lambda x: x["name"])]))
org.append(("Monthly Client Board – Status Label Deleted (shows blank)", [
    L(f"{r['group']} – {r['name']} – due {fmt(r['due'])}", f"Rep: {r['rep']}. Action: pick a real status.") for r in sorted(invalid, key=lambda x: (x["due"] or "9", x["name"]))]))
org.append(("Monthly Client Board – Paused Clients", [
    L(f"{k} – {len(v)} task{'s' if len(v)>1 else ''} on \"Pause Work\" ({', '.join(sorted({x['group'].split()[0] for x in v}))})",
      "Rep: Ayrica. Action: confirm whether this client is still active. If not, approve archiving these tasks.") for k, v in sorted(pause_by.items())]))
org.append(("Monthly Client Board – Old Months & Template", [
  L(f"June–September – {len(old_nostatus)} tasks with no status – Status Missing",
    "Each one is listed individually under Past Due.", "Action: owner marks it Done (with the deliverable) or explains why it's still open."),
  L(f"June–September – {len(old_sfr)} tasks stuck in \"Sent for Review\" – Summary Missing (no specific question or approval request)",
    "Each one is listed individually under Past Due.", "Action: Jay posts the exact question or approval needed and tags the reviewer."),
  L("Template group – October FFG and JVP tasks were created with no due date", "Rep: Customer Support. Action: add due date rules in the Template group."),
  L("Template group – July notes are being copied into every new month", "Rep: Customer Support. Action: clear the old notes from the Template group."),
]))
org.append(("Project Management Board", [
  L("Inbound Orders – Crista Jackson – 2025 Tax Return Filing – Summary Missing", "Rep: Customer Support. Action: write the Summary."),
  L("Inbound Orders – Crista Jackson – Tax Reduction Service – Summary Missing", "Rep: Customer Support. Action: write the Summary."),
  L("Inbound Orders – Mariah Williams – Corporate Compliance Lead – Summary Missing", "Rep: Customer Support. Action: write the Summary."),
  L("Inbound Orders – Antiwne Grant 2021 – Summary incorrect (copied from 2025)", "Rep: Customer Support. Action: rewrite it."),
  L("Inbound Orders – Antiwne Grant 2022 – Summary incorrect (copied from 2025)", "Rep: Customer Support. Action: rewrite it."),
  L("Inbound Orders – Antiwne Grant 2023 – Summary incorrect (copied from 2025)", "Rep: Customer Support. Action: rewrite it."),
  L("Board – no \"October 2026\" completed group exists", "Rep: Customer Support. Action: create it."),
]))
urgent_stale = [
 ("SHFT Media LLC (Peter Glatzer) – 2025 – Pending Preview", "8/31", "11716026386"),
 ("Antiwne Grant – 2024 Amendment – Sent to Account Manager", "8/17", "12003596807"),
 ("Grace Lakes Care Group – 2025 – Sent to Account Manager", "8/31", "11203562369"),
 ("Hiiivision Entertainment LLC (Joshua Evans) – 2025 – Sent to Account Manager", "8/31", "11492025966"),
 ("InTheDojo Inc (Tristin Mays) – 2025 – Waiting on Financial Information", "9/22", "11720606862"),
 ("Yolanda Bevini – 2024 – Mailed Return", "9/11", "12237073016"),
]
org.append(("Tax Board", [
  L("Urgent – Southbay Electrophysiology (Duane Bridges) – Status Missing, Date Received Missing", "Rep: Ayrica. Action: set the status and date.", TB + "13139262935")] +
  [L(f"Urgent – {n} – no update since {d} (past the 2-week window)", "Rep: Ayrica. Action: name the bottleneck and the next owner." + (" If it's complete, move it to Completed." if "Mailed" in n else ""), TB + i) for n, d, i in urgent_stale] +
  [L("Urgent – the 9 Waiting to Submit returns", "Listed one by one under For Ayrica.")] +
  [L(f"Inbound – {n} – Tax Year / Entity Type Missing", "Rep: Customer Support. Action: fill them in.") for n in
   ["JVP – J&M 2024 Associates K-1", "PhotosGraphix DRAFT 2025", "Dany R – LA County letter", "Breanna Colvin – IRS notice", "Lorie Nijjar – 2024 income question", "Yehuda Duenyas – claim denial"]]))
qbo_nostatus = ["Benard Home 1 LLC QBO", "Benard Home 1 LLC Payroll", "First Class Lifestyle Entertainment & Productions", "Jazee Campaigns LLC Payroll + Employees",
                "Jazee Campaigns LLC QBO", "Lash Art by Pricilla", "Oren Harris", "Splack Entertainment Inc", "S3CR3T WEAPON, Inc", "Seymour Butz Inc",
                "So Cal Training Team QBO", "SoCal Training Payroll + Employees", "SoCal Behavioral QBO", "SoCal Behavioral Payroll + Employees",
                "The Feel", "PBF Music", "Richard Lewis", "Mae Media", "Pure Joy Productions, Inc", "FFG Business Management Inc"]
qbo_price = ["Jazee Campaigns LLC QBO", "Lash Art by Pricilla", "Oren Harris", "Splack Entertainment Inc", "S3CR3T WEAPON, Inc", "Seymour Butz Inc",
             "So Cal Training Team QBO", "SoCal Behavioral QBO", "The Feel", "PBF Music", "Richard Lewis", "Mae Media", "Pure Joy Productions, Inc", "FFG Business Management Inc"]
org.append(("QBO CRM", [
  L(f"October 2026 – {n} – October payment status missing", "Rep: Customer Support. Action: verify payment in QBO and update the status.") for n in qbo_nostatus] +
  [L(f"October 2026 – {n} – Price shows $75, roster shows $85", "Rep: Ayrica. Action: confirm the correct price (P3 Cash Flow). Mo will not change billing.") for n in qbo_price] +
  [L("BDGE Enterprises – roster has no subscription status, October shows Declined, Inbound shows Cancelled", "Rep: Customer Support. Action: confirm the real status and record it in one place.")]))
sections.append(("Organization Items That Need Updated",
                 f"One bullet per task. Not flagged: {len(oct_nostatus_future)} October tasks with no status whose due date hasn't arrived yet.",
                 org))

# ---------- Section 4/5: due today & past due (Monthly)
listed_elsewhere = {"Waiting on Client", "Waiting On Internal Team", "Missing Information", "Missing Bank Statements", "Pause Work"}
MONTHS = {"June 2026": 6, "July 2026": 7, "August 2026": 8, "September 2026": 9, "October 2026": 10}
def stale_note(r):
    gm = MONTHS.get(r["group"])
    if not gm: return False
    ms = [int(m) for m in re.findall(r"\b(\d{1,2})/\d{1,2}/(?:20)?26\b", r["note"])]
    return bool(ms) and max(ms) < gm - 1

def by_client(rs, with_due):
    out = []
    grouped = defaultdict(list)
    for r in rs: grouped[client_of(r["name"])].append(r)
    for c in list(CLIENTS) + ["Other"]:
        if c not in grouped: continue
        lines = []
        for r in sorted(grouped[c], key=lambda x: (x["rep"], x["due"], x["name"])):
            desc = r["note"][:90] + ("…" if len(r["note"]) > 90 else "") if r["note"] else "—"
            if stale_note(r): desc = "(note copied from an earlier month – needs a current update)"
            main = f"{r['rep']} – {task_of(r['name'])} – {desc}"
            if with_due: main += f" – due {fmt(r['due'])}"
            sub = [f"Status: {r['status']}" + (f" · Period: {r['group']}" if with_due else "")]
            lines.append((main, sub))
        out.append((f"{CLIENTS.get(c, c)}  ({len(lines)})", lines))
    return out

today = [r for r in rows if r["due"] == TODAY and r["group"] != "Inbound"]
past = [r for r in rows if r["due"] and r["due"] < TODAY and r["group"] != "Inbound" and r["status"] not in listed_elsewhere]
sections.append(("Current Tasks Due Today by Client & Representative",
                 f"{len(today)} tasks due Mon 10/26. Action: complete today, or post an update saying why not.", by_client(today, False)))
sections.append(("Past Due Tasks by Client & Representative",
                 f"{len(past)} past-due tasks. Excludes items already listed under Missing Information and Pause Work. Action: complete, or post why it's late and a new date. If the work was already done, mark it Done with the deliverable attached.",
                 by_client(past, True)))

counts = dict(today=len(today), past=len(past), mbs=sum(len(v) for v in mbs.values()), nodate=len(nodate))

# ---------------------------------------------------------------- render docx
doc = Document()
st = doc.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(10.5)
h = doc.add_heading("FFG Daily Task Review – Monday, October 26, 2026", 0)
p = doc.add_paragraph()
p.add_run("Prepared by Mo (AI Operations Manager) · AUDIT MODE: nothing on the boards has been changed. Every item is a recommendation for approval.").italic = True
p = doc.add_paragraph()
p.add_run(f"Snapshot: {counts['past']} past due · {counts['today']} due today · {counts['mbs']} tasks on Missing Bank Statements · {counts['nodate']} with no due date.").bold = True
doc.add_paragraph("Sources: Monthly Client Board, 2026 Tax List, 2026 Project Management, QBO CRM 2026 (pulled 10/26/26). Delegation emails to reps are drafted only when Ayrica asks.")

for title, intro, groups in sections:
    doc.add_heading(title, 1)
    if intro:
        ip = doc.add_paragraph(); r = ip.add_run(intro); r.italic = True; r.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
    for gtitle, lines in groups:
        if gtitle: doc.add_heading(gtitle, 2)
        for main, subs in lines:
            doc.add_paragraph(main, style="List Bullet")
            for s in subs:
                if s.startswith("• "): doc.add_paragraph(s[2:], style="List Bullet 3")
                elif s: doc.add_paragraph(s, style="List Bullet 2")
doc.save(OUT_DOCX)

# ---------------------------------------------------------------- render email HTML (Ayrica section + summary)
e = html.escape
parts = ['<div style="font-family:Calibri,Arial,sans-serif;font-size:14px;color:#222">',
         "<p>Hi Ayrica,</p>",
         f"<p>Here is today's task review. <b>{counts['past']} past due · {counts['today']} due today · {counts['mbs']} on Missing Bank Statements · {counts['nodate']} missing due dates.</b> "
         "Nothing has been changed on the boards. Every item is one bullet with its action. Monday links and the full past-due task lines are in the Word doc (Mo/reports/2026-10-26_FFG_Daily_Task_Review.docx).</p>"]
def html_section(title, intro, groups, cap=None):
    out = [f'<h3>{e(title)}</h3>']
    if intro: out.append(f'<p><i>{e(intro)}</i></p>')
    for gtitle, lines in groups:
        if gtitle: out.append(f"<p><b>{e(gtitle)}</b></p>")
        out.append("<ul>")
        for i, (main, subs) in enumerate(lines):
            if cap and i >= cap:
                out.append(f"<li><i>+{len(lines)-cap} more in the Word doc</i></li>"); break
            sub = "".join((f"<ul><li>{e(s[2:])}</li></ul>" if s.startswith("• ") else f"<li>{e(s)}</li>") for s in subs if s and not s.startswith("Link: "))
            out.append(f"<li>{e(main)}" + (f"<ul>{sub}</ul>" if sub else "") + "</li>")
        out.append("</ul>")
    return "".join(out)
for idx, (title, intro, groups) in enumerate(sections):
    if title.startswith("For Ayrica") or title.startswith("Inbound"):
        parts.append(html_section(title, intro, groups))
    elif title.startswith("Current Tasks Due Today"):
        parts.append(html_section(title, intro, groups))
    elif title.startswith("Past Due"):
        summ = [(f"{g}", []) for g, _ in groups]
        parts.append(html_section(title, intro + " (counts by client below; task lines are in the Word doc)", [(None, summ)]))
    elif title.startswith("Organization"):
        parts.append(html_section(title, intro, [(g, l) for g, l in groups if not (g.endswith("Due Date Missing") or g.startswith("Monthly Client Board – Status Label"))] +
                                  [("Monthly Client Board – Due Date Missing", [(f"{len(nodate)} tasks (54 FFG, 4 JVP) – each one listed in the Word doc", [])]),
                                   ("Monthly Client Board – Status Label Deleted", [(f"{len(invalid)} tasks – each one listed in the Word doc", [])])]))
    else:
        parts.append(html_section(title, intro, groups))
parts.append("<p>Reply with what you approve, and tell me which sections to draft as delegation emails to Jay, Customer Support, or Joanie.</p><p>– Mo</p></div>")
open(OUT_HTML, "w").write("".join(parts))
print(counts, "sections:", [s[0] for s in sections])
