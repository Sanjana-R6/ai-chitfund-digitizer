import gradio as gr
import json
import os
import sys
import tempfile
from PIL import Image
from datetime import date

sys.path.append('..')
try:
    from agent.agent import process_image
    AI_AVAILABLE = True
except:
    AI_AVAILABLE = False

DATA_DIR = "data"
INDEX_FILE = os.path.join(DATA_DIR, "chits_index.json")

SUGGESTED_FIELDS_EN = ["Phone", "Address", "Guarantor", "Loan Taken", "Notes",
                        "Occupation", "Aadhar Number", "Bank Account", "Email", "Emergency Contact"]
SUGGESTED_FIELDS_TE = ["ఫోన్", "చిరునామా", "గ్యారెంటర్", "అప్పు తీసుకున్నారా", "గమనికలు",
                        "వృత్తి", "ఆధార్ నంబర్", "బ్యాంక్ అకౌంట్", "ఇమెయిల్", "అత్యవసర సంప్రదింపు"]

os.makedirs(DATA_DIR, exist_ok=True)

SAMPLE_CHIT = {
    "chit_name": "Sample Chit Fund",
    "chit_value": 100000,
    "members": 10,
    "monthly_sub": 5000,
    "commission_pct": 5,
    "winning_bid": 15000,
    "current_month": 3,
    "start_date": "2024-01-01",
    "custom_fields": ["Phone", "Address", "Guarantor", "Loan Taken", "Notes"],
    "members_list": [
        {"name": "Ravi",    "paid": True,  "due": 0,    "months_paid": 3, "missed": 0, "Phone": "", "Address": "", "Guarantor": "", "Loan Taken": "No",  "Notes": ""},
        {"name": "Lakshmi", "paid": True,  "due": 0,    "months_paid": 3, "missed": 0, "Phone": "", "Address": "", "Guarantor": "", "Loan Taken": "No",  "Notes": ""},
        {"name": "Suresh",  "paid": False, "due": 5000, "months_paid": 2, "missed": 2, "Phone": "", "Address": "", "Guarantor": "", "Loan Taken": "Yes", "Notes": ""},
        {"name": "Priya",   "paid": True,  "due": 0,    "months_paid": 3, "missed": 0, "Phone": "", "Address": "", "Guarantor": "", "Loan Taken": "No",  "Notes": ""},
        {"name": "Ramesh",  "paid": False, "due": 5000, "months_paid": 1, "missed": 3, "Phone": "", "Address": "", "Guarantor": "", "Loan Taken": "Yes", "Notes": ""},
        {"name": "Sita",    "paid": True,  "due": 0,    "months_paid": 3, "missed": 0, "Phone": "", "Address": "", "Guarantor": "", "Loan Taken": "No",  "Notes": ""},
        {"name": "Kiran",   "paid": True,  "due": 0,    "months_paid": 3, "missed": 0, "Phone": "", "Address": "", "Guarantor": "", "Loan Taken": "No",  "Notes": ""},
        {"name": "Deepa",   "paid": False, "due": 5000, "months_paid": 2, "missed": 2, "Phone": "", "Address": "", "Guarantor": "", "Loan Taken": "No",  "Notes": ""},
        {"name": "Arjun",   "paid": True,  "due": 0,    "months_paid": 3, "missed": 0, "Phone": "", "Address": "", "Guarantor": "", "Loan Taken": "No",  "Notes": ""},
        {"name": "Meena",   "paid": True,  "due": 0,    "months_paid": 3, "missed": 0, "Phone": "", "Address": "", "Guarantor": "", "Loan Taken": "No",  "Notes": ""},
    ]
}

# ── Index helpers ──────────────────────────────────────────────
def load_index():
    if os.path.exists(INDEX_FILE):
        try:
            with open(INDEX_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
        except:
            pass
    # Bootstrap with sample
    index = {"chits": ["Sample Chit Fund"], "active": "Sample Chit Fund"}
    save_index(index)
    save_chit("Sample Chit Fund", SAMPLE_CHIT)
    return index

def save_index(index):
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

def chit_filename(name):
    safe = name.replace(" ", "_").replace("/", "-")
    return os.path.join(DATA_DIR, f"chit_{safe}.json")

def load_chit(name):
    path = chit_filename(name)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
        except:
            pass
    return None

def save_chit(name, data):
    with open(chit_filename(name), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def delete_chit_file(name):
    path = chit_filename(name)
    if os.path.exists(path):
        os.remove(path)

def get_all_chits():
    return load_index().get("chits", [])

def get_active_chit():
    return load_index().get("active", None)

def set_active_chit(name):
    index = load_index()
    index["active"] = name
    save_index(index)

# ── Calculations ───────────────────────────────────────────────
def calculate_summary(data):
    chit_value   = data["chit_value"]
    winning_bid  = data.get("winning_bid", 0)
    num_members  = data["members"]
    commission   = round(chit_value * data["commission_pct"] / 100, 2)
    dividend     = round((winning_bid - commission) / num_members, 2) if winning_bid > 0 else 0
    prized_amount = chit_value - winning_bid
    total_collected = sum(m["months_paid"] * data["monthly_sub"] for m in data["members_list"])
    pending      = sum(m["due"] for m in data["members_list"])
    paid_count   = sum(1 for m in data["members_list"] if m["paid"])
    return commission, dividend, prized_amount, total_collected, pending, paid_count

def get_custom_fields_list(chit_name=None):
    if not chit_name:
        chit_name = get_active_chit()
    if not chit_name:
        return []
    data = load_chit(chit_name)
    return data.get("custom_fields", []) if data else []

# ── Empty state HTML ───────────────────────────────────────────
EMPTY_HOME = """
<div style='text-align:center;padding:60px 20px;color:var(--text-muted)'>
    <div style='font-size:60px;margin-bottom:16px'>🏦</div>
    <div style='font-size:20px;font-weight:700;color:var(--text-main);margin-bottom:8px'>No Chit Fund selected</div>
    <div style='font-size:14px'>Create a new chit fund or select one from the dropdown above.</div>
</div>"""

EMPTY_TABLE = """
<div style='text-align:center;padding:40px;color:var(--text-muted);font-size:14px'>
    No chit fund selected. Please select or create one first.
</div>"""

# ── Home cards ─────────────────────────────────────────────────
def get_home_cards_en(chit_name=None):
    if not chit_name:
        return EMPTY_HOME
    data = load_chit(chit_name)
    if not data:
        return EMPTY_HOME
    commission, dividend, prized_amount, total_collected, pending, paid_count = calculate_summary(data)
    return f"""
<div style='display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:24px'>
    <div class='metric-box'><div class='metric-value'>&#8377;{total_collected:,.0f}</div>
        <div style='font-size:13px;margin-top:4px;color:var(--text-muted);font-weight:500'>Total Collected</div></div>
    <div class='metric-box'><div class='metric-value'>&#8377;{pending:,.0f}</div>
        <div style='font-size:13px;margin-top:4px;color:var(--text-muted);font-weight:500'>Pending Dues</div></div>
    <div class='metric-box'><div class='metric-value'>&#8377;{prized_amount:,.0f}</div>
        <div style='font-size:13px;margin-top:4px;color:var(--text-muted);font-weight:500'>Prized Amount</div></div>
    <div class='metric-box'><div class='metric-value'>&#8377;{dividend:,.0f}</div>
        <div style='font-size:13px;margin-top:4px;color:var(--text-muted);font-weight:500'>Dividend / Member</div></div>
</div>
<div style='background:rgba(0,242,254,0.05);border:1px solid var(--primary);border-radius:12px;padding:12px 20px;font-size:14px;color:var(--text-main)'>
    <span style="color:var(--primary)">&#9679;</span> <b>{data['chit_name']}</b> &nbsp;|&nbsp; Month {data['current_month']}
    &nbsp;|&nbsp; {paid_count}/{data['members']} members paid &nbsp;|&nbsp; Value: &#8377;{data['chit_value']:,}
</div>"""

def get_home_cards_te(chit_name=None):
    if not chit_name:
        return EMPTY_HOME
    data = load_chit(chit_name)
    if not data:
        return EMPTY_HOME
    commission, dividend, prized_amount, total_collected, pending, paid_count = calculate_summary(data)
    return f"""
<div style='display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:24px'>
    <div class='metric-box'><div class='metric-value'>&#8377;{total_collected:,.0f}</div>
        <div style='font-size:13px;margin-top:4px;color:var(--text-muted);font-weight:500'>మొత్తం సేకరించినది</div></div>
    <div class='metric-box'><div class='metric-value'>&#8377;{pending:,.0f}</div>
        <div style='font-size:13px;margin-top:4px;color:var(--text-muted);font-weight:500'>పెండింగ్ బకాయిలు</div></div>
    <div class='metric-box'><div class='metric-value'>&#8377;{prized_amount:,.0f}</div>
        <div style='font-size:13px;margin-top:4px;color:var(--text-muted);font-weight:500'>ప్రైజ్డ్ మొత్తం</div></div>
    <div class='metric-box'><div class='metric-value'>&#8377;{dividend:,.0f}</div>
        <div style='font-size:13px;margin-top:4px;color:var(--text-muted);font-weight:500'>డివిడెండ్ / సభ్యుడు</div></div>
</div>
<div style='background:rgba(0,242,254,0.05);border:1px solid var(--primary);border-radius:12px;padding:12px 20px;font-size:14px;color:var(--text-main)'>
    <span style="color:var(--primary)">&#9679;</span> <b>{data['chit_name']}</b> &nbsp;|&nbsp; నెల {data['current_month']}
    &nbsp;|&nbsp; {paid_count}/{data['members']} సభ్యులు చెల్లించారు &nbsp;|&nbsp; విలువ: &#8377;{data['chit_value']:,}
</div>"""

# ── Member table ───────────────────────────────────────────────
def _member_rows(members_list, custom_fields, monthly_sub, current_month, dividend, selector_id, lang):
    rows_html = ""
    for i, m in enumerate(members_list):
        if m["missed"] >= 2:
            status_badge = ("<span style='background:#fff3cd;color:#856404;padding:4px 12px;border-radius:12px;font-size:12px;font-weight:600'>&#9888; హెచ్చరిక</span>"
                            if lang == "te" else
                            "<span style='background:#fff3cd;color:#856404;padding:4px 12px;border-radius:12px;font-size:12px;font-weight:600'>&#9888; Flagged</span>")
        elif m["paid"]:
            status_badge = ("<span style='background:#d1fae5;color:#065f46;padding:4px 12px;border-radius:12px;font-size:12px;font-weight:600'>&#9989; చెల్లించారు</span>"
                            if lang == "te" else
                            "<span style='background:#d1fae5;color:#065f46;padding:4px 12px;border-radius:12px;font-size:12px;font-weight:600'>&#9989; Paid</span>")
        else:
            status_badge = ("<span style='background:#fee2e2;color:#991b1b;padding:4px 12px;border-radius:12px;font-size:12px;font-weight:600'>&#10060; చెల్లించలేదు</span>"
                            if lang == "te" else
                            "<span style='background:#fee2e2;color:#991b1b;padding:4px 12px;border-radius:12px;font-size:12px;font-weight:600'>&#10060; Unpaid</span>")
        row_bg = "#ffffff" if i % 2 == 0 else "#f8fffe"
        custom_cells = "".join([
            f"<td style='padding:12px 16px;font-size:13px;color:#1a1a1a;border-bottom:1px solid #e2f4f1;border-right:1px solid #e2f4f1'>{m.get(field, '')}</td>"
            for field in custom_fields
        ])
        due_color = "#e76f51" if m["due"] > 0 else "#2a9d8f"
        safe_name = m['name'].replace("'", "\\'").replace('"', '&quot;')
        # Build custom fields JSON for autofill
        custom_json = json.dumps({f: m.get(f, "") for f in custom_fields}, ensure_ascii=False).replace("'", "\\'").replace('"', '&quot;')
        paid_status = ("చెల్లించారు" if m["paid"] else "చెల్లించలేదు") if lang == "te" else ("Paid" if m["paid"] else "Unpaid")
        rows_html += f"""
        <tr style='background:{row_bg};cursor:pointer'
            onmouseover="this.style.background='#e8f5f3'"
            onmouseout="this.style.background='{row_bg}'"
            onclick="(function(){{
                var dd = document.querySelector('#{selector_id} input');
                if(dd) {{
                    var lastValue = dd.value;
                    dd.value = '{safe_name}';
                    var ev = new Event('input', {{ bubbles: true }});
                    ev.simulated = true;
                    var tracker = dd._valueTracker;
                    if(tracker) tracker.setValue(lastValue);
                    dd.dispatchEvent(ev);
                    dd.dispatchEvent(new Event('change', { bubbles: true }));
                }}
            }})()">
            <td style='padding:12px 16px;font-size:13px;color:#2a9d8f;font-weight:700;border-bottom:1px solid #e2f4f1;border-right:1px solid #e2f4f1'>{i+1}</td>
            <td style='padding:12px 16px;font-size:13px;color:#1a1a1a;font-weight:600;border-bottom:1px solid #e2f4f1;border-right:1px solid #e2f4f1'>{m['name']}</td>
            <td style='padding:12px 16px;font-size:13px;color:#1a1a1a;border-bottom:1px solid #e2f4f1;border-right:1px solid #e2f4f1'>&#8377;{monthly_sub:,}</td>
            <td style='padding:12px 16px;border-bottom:1px solid #e2f4f1;border-right:1px solid #e2f4f1'>{status_badge}</td>
            <td style='padding:12px 16px;font-size:13px;color:#2a9d8f;font-weight:600;border-bottom:1px solid #e2f4f1;border-right:1px solid #e2f4f1'>&#8377;{dividend:,.0f}</td>
            <td style='padding:12px 16px;font-size:13px;color:{due_color};font-weight:600;border-bottom:1px solid #e2f4f1;border-right:1px solid #e2f4f1'>&#8377;{m["due"]:,}</td>
            <td style='padding:12px 16px;font-size:13px;color:#1a1a1a;border-bottom:1px solid #e2f4f1;border-right:1px solid #e2f4f1'>{m["months_paid"]}/{current_month}</td>
            {custom_cells}
        </tr>"""
    return rows_html

def make_excel_table_en(chit_name=None, search=""):
    if not chit_name:
        return EMPTY_TABLE
    data = load_chit(chit_name)
    if not data:
        return EMPTY_TABLE
    _, dividend, _, _, _, _ = calculate_summary(data)
    members_list = data["members_list"]
    custom_fields = data.get("custom_fields", [])
    if search:
        members_list = [m for m in members_list if search.lower() in m["name"].lower()]
    header_cols = ["#", "Member Name", "Monthly (&#8377;)", "Status", "Dividend (&#8377;)", "Due (&#8377;)", "Months Paid"] + custom_fields
    headers = "".join([f"<th style='background:#2a9d8f;color:#ffffff;padding:12px 16px;text-align:left;font-weight:600;font-size:13px;white-space:nowrap;border-right:1px solid #1e7d72'>{h}</th>" for h in header_cols])
    rows_html = _member_rows(members_list, custom_fields, data["monthly_sub"], data["current_month"], dividend, "member_select_en", "en")
    return f"""<div style='overflow-x:auto;border-radius:12px;border:1.5px solid #2a9d8f;margin-top:8px;box-shadow:0 2px 8px rgba(42,157,143,0.1)'>
    <table style='width:100%;border-collapse:collapse;font-family:sans-serif'>
        <thead><tr>{headers}</tr></thead><tbody>{rows_html}</tbody>
    </table></div>
<p style='font-size:12px;color:#64748b;margin-top:6px'>&#128161; Click any row to auto-fill the edit form below</p>"""

def make_excel_table_te(chit_name=None, search=""):
    if not chit_name:
        return EMPTY_TABLE
    data = load_chit(chit_name)
    if not data:
        return EMPTY_TABLE
    _, dividend, _, _, _, _ = calculate_summary(data)
    members_list = data["members_list"]
    custom_fields = data.get("custom_fields", [])
    if search:
        members_list = [m for m in members_list if search.lower() in m["name"].lower()]
    header_cols = ["#", "సభ్యుని పేరు", "నెలవారీ (&#8377;)", "స్థితి", "డివిడెండ్ (&#8377;)", "బకాయి (&#8377;)", "చెల్లించిన నెలలు"] + custom_fields
    headers = "".join([f"<th style='background:#2a9d8f;color:#ffffff;padding:12px 16px;text-align:left;font-weight:600;font-size:13px;white-space:nowrap;border-right:1px solid #1e7d72'>{h}</th>" for h in header_cols])
    rows_html = _member_rows(members_list, custom_fields, data["monthly_sub"], data["current_month"], dividend, "member_select_te", "te")
    return f"""<div style='overflow-x:auto;border-radius:12px;border:1.5px solid #2a9d8f;margin-top:8px;box-shadow:0 2px 8px rgba(42,157,143,0.1)'>
    <table style='width:100%;border-collapse:collapse;font-family:sans-serif'>
        <thead><tr>{headers}</tr></thead><tbody>{rows_html}</tbody>
    </table></div>
<p style='font-size:12px;color:#64748b;margin-top:6px'>&#128161; ఏదైనా వరుసపై క్లిక్ చేయండి — ఫారమ్ ఆటోమేటిక్‌గా నింపబడుతుంది</p>"""

# ── Switch chit fund ───────────────────────────────────────────
def switch_chit_en(chit_name):
    if not chit_name:
        return (EMPTY_HOME, EMPTY_TABLE, EMPTY_TABLE,
                gr.update(choices=[], value=None), "", gr.update(value=""), gr.update(choices=get_all_chits(), value=None))
    set_active_chit(chit_name)
    data = load_chit(chit_name)
    if not data:
        return (EMPTY_HOME, EMPTY_TABLE, EMPTY_TABLE,
                gr.update(choices=[], value=None), "", gr.update(value=""), gr.update(choices=get_all_chits(), value=chit_name))
    member_names = [m["name"] for m in data["members_list"]]
    first = member_names[0] if member_names else None
    auction_result = calculate_auction_for_en(chit_name, data.get("winning_bid", 0))
    return (
        get_home_cards_en(chit_name),
        make_excel_table_en(chit_name),
        make_excel_table_en(chit_name),
        gr.update(choices=member_names, value=first),
        auction_result,
        gr.update(value=f"Switched to **{chit_name}**"),
        gr.update(choices=get_all_chits(), value=chit_name),
    )

def switch_chit_te(chit_name):
    if not chit_name:
        return (EMPTY_HOME, EMPTY_TABLE, EMPTY_TABLE,
                gr.update(choices=[], value=None), "", gr.update(value=""), gr.update(choices=get_all_chits(), value=None))
    set_active_chit(chit_name)
    data = load_chit(chit_name)
    if not data:
        return (EMPTY_HOME, EMPTY_TABLE, EMPTY_TABLE,
                gr.update(choices=[], value=None), "", gr.update(value=""), gr.update(choices=get_all_chits(), value=chit_name))
    member_names = [m["name"] for m in data["members_list"]]
    first = member_names[0] if member_names else None
    auction_result = calculate_auction_for_te(chit_name, data.get("winning_bid", 0))
    return (
        get_home_cards_te(chit_name),
        make_excel_table_te(chit_name),
        make_excel_table_te(chit_name),
        gr.update(choices=member_names, value=first),
        auction_result,
        gr.update(value=f"**{chit_name}** కి మారారు"),
        gr.update(choices=get_all_chits(), value=chit_name),
    )

# ── Delete chit fund ───────────────────────────────────────────
def delete_chit_en(chit_name):
    if not chit_name:
        return ("⚠️ No chit fund selected.",
                gr.update(), gr.update(), EMPTY_HOME, EMPTY_TABLE, EMPTY_TABLE,
                gr.update(choices=[], value=None), "")
    index = load_index()
    if chit_name in index["chits"]:
        index["chits"].remove(chit_name)
    delete_chit_file(chit_name)
    # Pick next active
    new_active = index["chits"][0] if index["chits"] else None
    index["active"] = new_active
    save_index(index)
    all_chits = index["chits"]
    if new_active:
        data = load_chit(new_active)
        member_names = [m["name"] for m in data["members_list"]] if data else []
        first = member_names[0] if member_names else None
        return (
            f"✅ '{chit_name}' deleted.",
            gr.update(choices=all_chits, value=new_active),
            gr.update(choices=all_chits, value=new_active),
            get_home_cards_en(new_active),
            make_excel_table_en(new_active),
            make_excel_table_en(new_active),
            gr.update(choices=member_names, value=first),
            calculate_auction_for_en(new_active, load_chit(new_active).get("winning_bid", 0)) if load_chit(new_active) else "",
        )
    return (
        f"✅ '{chit_name}' deleted. No chit funds remaining.",
        gr.update(choices=[], value=None),
        gr.update(choices=[], value=None),
        EMPTY_HOME, EMPTY_TABLE, EMPTY_TABLE,
        gr.update(choices=[], value=None),
        "",
    )

def delete_chit_te(chit_name):
    if not chit_name:
        return ("⚠️ చిట్ ఫండ్ ఎంచుకోలేదు.",
                gr.update(), gr.update(), EMPTY_HOME, EMPTY_TABLE, EMPTY_TABLE,
                gr.update(choices=[], value=None), "")
    index = load_index()
    if chit_name in index["chits"]:
        index["chits"].remove(chit_name)
    delete_chit_file(chit_name)
    new_active = index["chits"][0] if index["chits"] else None
    index["active"] = new_active
    save_index(index)
    all_chits = index["chits"]
    if new_active:
        data = load_chit(new_active)
        member_names = [m["name"] for m in data["members_list"]] if data else []
        first = member_names[0] if member_names else None
        return (
            f"✅ '{chit_name}' తొలగించబడింది.",
            gr.update(choices=all_chits, value=new_active),
            gr.update(choices=all_chits, value=new_active),
            get_home_cards_te(new_active),
            make_excel_table_te(new_active),
            make_excel_table_te(new_active),
            gr.update(choices=member_names, value=first),
            calculate_auction_for_te(new_active, load_chit(new_active).get("winning_bid", 0)) if load_chit(new_active) else "",
        )
    return (
        f"✅ '{chit_name}' తొలగించబడింది. చిట్ ఫండ్‌లు లేవు.",
        gr.update(choices=[], value=None),
        gr.update(choices=[], value=None),
        EMPTY_HOME, EMPTY_TABLE, EMPTY_TABLE,
        gr.update(choices=[], value=None),
        "",
    )

# ── Auction ────────────────────────────────────────────────────
def calculate_auction_for_en(chit_name, winning_bid):
    if not winning_bid or not chit_name:
        return ""
    data = load_chit(chit_name)
    if not data:
        return ""
    winning_bid = float(winning_bid)
    commission = round(data["chit_value"] * data["commission_pct"] / 100, 2)
    dividend = round((winning_bid - commission) / data["members"], 2)
    prized_amount = data["chit_value"] - winning_bid
    net_installment = data["monthly_sub"] - dividend
    data["winning_bid"] = int(winning_bid)
    save_chit(chit_name, data)
    return f"""### 🔨 Auction Result\n\n| Detail | Amount |\n|---|---|\n| Chit Value | &#8377;{data['chit_value']:,} |\n| Winning Bid | &#8377;{winning_bid:,.0f} |\n| **Prized Amount** | **&#8377;{prized_amount:,.0f}** |\n| Foreman Commission ({data['commission_pct']}%) | &#8377;{commission:,.0f} |\n| **Dividend per Member** | **&#8377;{dividend:,.0f}** |\n| Net Installment to Pay | &#8377;{net_installment:,.0f} |\n\n> 💡 Each member pays &#8377;{net_installment:,.0f} this month instead of &#8377;{data['monthly_sub']:,}"""

def calculate_auction_for_te(chit_name, winning_bid):
    if not winning_bid or not chit_name:
        return ""
    data = load_chit(chit_name)
    if not data:
        return ""
    winning_bid = float(winning_bid)
    commission = round(data["chit_value"] * data["commission_pct"] / 100, 2)
    dividend = round((winning_bid - commission) / data["members"], 2)
    prized_amount = data["chit_value"] - winning_bid
    net_installment = data["monthly_sub"] - dividend
    data["winning_bid"] = int(winning_bid)
    save_chit(chit_name, data)
    return f"""### 🔨 వేలం ఫలితం\n\n| వివరాలు | మొత్తం |\n|---|---|\n| చిట్ విలువ | &#8377;{data['chit_value']:,} |\n| గెలిచిన బిడ్ | &#8377;{winning_bid:,.0f} |\n| **ప్రైజ్డ్ మొత్తం** | **&#8377;{prized_amount:,.0f}** |\n| ఫోర్‌మన్ కమీషన్ ({data['commission_pct']}%) | &#8377;{commission:,.0f} |\n| **సభ్యుడికి డివిడెండ్** | **&#8377;{dividend:,.0f}** |\n| చెల్లించాల్సిన నికర మొత్తం | &#8377;{net_installment:,.0f} |\n\n> 💡 ప్రతి సభ్యుడు ఈ నెల &#8377;{data['monthly_sub']:,} బదులు &#8377;{net_installment:,.0f} చెల్లిస్తారు"""

def calculate_auction_en(winning_bid, chit_name=None):
    if not chit_name:
        chit_name = get_active_chit()
    return calculate_auction_for_en(chit_name, winning_bid)

def calculate_auction_te(winning_bid, chit_name=None):
    if not chit_name:
        chit_name = get_active_chit()
    return calculate_auction_for_te(chit_name, winning_bid)

# ── Member detail ──────────────────────────────────────────────
def show_member_en(name, chit_name=None):
    if not name or not chit_name:
        return "", gr.update(visible=False), None, "Paid", "{}"
    data = load_chit(chit_name)
    if not data:
        return "", gr.update(visible=False), None, "Paid", "{}"
    _, dividend, _, _, _, _ = calculate_summary(data)
    for m in data["members_list"]:
        if m["name"] == name:
            flag_text = f"\n> ⚠️ **Warning:** This member has missed {m['missed']} payments!" if m["missed"] >= 2 else ""
            custom_rows = "".join([f"| {field} | {m.get(field, '-')} |\n" for field in data.get("custom_fields", [])])
            whatsapp = f"📱 *WhatsApp Alert Preview*\n\nHello {m['name']}! 🙏\n\nYour Chit Fund Details:\n- Monthly: ₹{data['monthly_sub']:,}\n- Dividend: ₹{dividend:.0f}\n- Amount Due: ₹{m['due']:,}\n- Status: {'✅ Paid' if m['paid'] else '❌ Unpaid'}\n\n_ChitSync_ ✨"
            info = f"## 👤 {m['name']}\n{flag_text}\n\n| Detail | Value |\n|--------|-------|\n| Monthly Contribution | ₹{data['monthly_sub']:,} |\n| Payment Status | {'✅ Paid' if m['paid'] else '❌ Unpaid'} |\n| Months Paid | {m['months_paid']} of {data['current_month']} |\n| Missed Payments | {m['missed']} |\n| Dividend This Month | ₹{dividend:.0f} |\n| Net Amount Due | ₹{m['due']:,} |\n{custom_rows}\n---\n{whatsapp}\n"
            custom_vals = json.dumps({f: m.get(f, "") for f in data.get("custom_fields", [])})
            return info, gr.update(visible=True), data['monthly_sub'], "Paid" if m['paid'] else "Unpaid", custom_vals
    return "Member not found", gr.update(visible=False), None, "Paid", "{}"

def show_member_te(name, chit_name=None):
    if not name or not chit_name:
        return "", gr.update(visible=False), None, "చెల్లించారు", "{}"
    data = load_chit(chit_name)
    if not data:
        return "", gr.update(visible=False), None, "చెల్లించారు", "{}"
    _, dividend, _, _, _, _ = calculate_summary(data)
    for m in data["members_list"]:
        if m["name"] == name:
            flag_text = f"\n> ⚠️ **హెచ్చరిక:** ఈ సభ్యుడు {m['missed']} చెల్లింపులు మిస్ చేశాడు!" if m["missed"] >= 2 else ""
            custom_rows = "".join([f"| {field} | {m.get(field, '-')} |\n" for field in data.get("custom_fields", [])])
            whatsapp = f"📱 *వాట్సాప్ అలర్ట్ ప్రివ్యూ*\n\nనమస్కారం {m['name']} గారు! 🙏\n\nమీ చిట్ ఫండ్ వివరాలు:\n- నెలవారీ: ₹{data['monthly_sub']:,}\n- డివిడెండ్: ₹{dividend:.0f}\n- బకాయి: ₹{m['due']:,}\n- స్థితి: {'✅ చెల్లించారు' if m['paid'] else '❌ చెల్లించలేదు'}\n\n_చిట్‌సింక్_ ✨"
            info = f"## 👤 {m['name']}\n{flag_text}\n\n| వివరాలు | విలువ |\n|--------|-------|\n| నెలవారీ చందా | ₹{data['monthly_sub']:,} |\n| చెల్లింపు స్థితి | {'✅ చెల్లించారు' if m['paid'] else '❌ చెల్లించలేదు'} |\n| చెల్లించిన నెలలు | {m['months_paid']} లో {data['current_month']} |\n| మిస్ అయిన చెల్లింపులు | {m['missed']} |\n| ఈ నెల డివిడెండ్ | ₹{dividend:.0f} |\n| చెల్లించాల్సిన నికర మొత్తం | ₹{m['due']:,} |\n{custom_rows}\n---\n{whatsapp}\n"
            custom_vals = json.dumps({f: m.get(f, "") for f in data.get("custom_fields", [])}, ensure_ascii=False)
            return info, gr.update(visible=True), data['monthly_sub'], "చెల్లించారు" if m['paid'] else "చెల్లించలేదు", custom_vals
    return "సభ్యుడు కనుగొనబడలేదు", gr.update(visible=False), None, "చెల్లించారు", "{}"

def send_alert_en(name):
    return f"✅ WhatsApp alert sent to {name} successfully!" if name else "⚠️ Please select a member first"

def send_alert_te(name):
    return f"✅ {name} కి వాట్సాప్ అలర్ట్ పంపబడింది!" if name else "⚠️ దయచేసి ముందు సభ్యుడిని ఎంచుకోండి"

def _apply_edit(m, data, new_amount, new_status, custom_vals_json, paid_kw, unpaid_kw):
    if new_amount:
        data["monthly_sub"] = int(new_amount)
    if new_status == paid_kw:
        m["paid"] = True; m["due"] = 0; m["months_paid"] += 1; m["missed"] = 0
    elif new_status == unpaid_kw:
        m["paid"] = False; m["due"] = data["monthly_sub"]; m["missed"] += 1
    try:
        custom_vals = json.loads(custom_vals_json) if custom_vals_json else {}
        for field, val in custom_vals.items():
            if field in data["custom_fields"]:
                m[field] = val
    except:
        pass

def edit_member_en(name, new_amount, new_status, custom_vals_json, chit_name=None):
    if not name:
        return "⚠️ Please select a member first", make_excel_table_en(chit_name)
    if not chit_name:
        chit_name = get_active_chit()
    data = load_chit(chit_name)
    if not data:
        return "⚠️ Chit fund not found", EMPTY_TABLE
    for m in data["members_list"]:
        if m["name"] == name:
            _apply_edit(m, data, new_amount, new_status, custom_vals_json, "Paid", "Unpaid")
            save_chit(chit_name, data)
            try:
                table = make_excel_table_en(chit_name)
            except Exception as e:
                table = f"<p style='color:red'>Table error: {e}</p>"
            return f"✅ Record updated for {name}!", table
    return "Member not found", make_excel_table_en(chit_name)

def edit_member_te(name, new_amount, new_status, custom_vals_json, chit_name=None):
    if not name:
        return "⚠️ దయచేసి ముందు సభ్యుడిని ఎంచుకోండి", make_excel_table_te(chit_name)
    if not chit_name:
        chit_name = get_active_chit()
    data = load_chit(chit_name)
    if not data:
        return "⚠️ చిట్ ఫండ్ కనుగొనబడలేదు", EMPTY_TABLE
    for m in data["members_list"]:
        if m["name"] == name:
            _apply_edit(m, data, new_amount, new_status, custom_vals_json, "చెల్లించారు", "చెల్లించలేదు")
            save_chit(chit_name, data)
            return f"✅ {name} రికార్డ్ అప్‌డేట్ అయింది!", make_excel_table_te(chit_name)
    return "సభ్యుడు కనుగొనబడలేదు", make_excel_table_te(chit_name)

# ── AI Ledger ──────────────────────────────────────────────────
def _process_ai_image(image, chit_name):
    if not chit_name:
        return
    data = load_chit(chit_name)
    if not data or image is None or not AI_AVAILABLE:
        return
    try:
        img = Image.fromarray(image.astype('uint8'))
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        img.save(tmp.name)
        result = process_image(tmp.name)
        os.unlink(tmp.name)
        for m in data["members_list"]:
            for ai_m in result.get("members", []):
                if ai_m.get("name", "").lower() in m["name"].lower():
                    m["paid"] = ai_m.get("amount_paid", 0) > 0
                    m["due"] = 0 if m["paid"] else data["monthly_sub"]
        save_chit(chit_name, data)
    except Exception as e:
        print(f"AI processing failed: {e}")

def show_ledger_ai_en(image, search="", chit_name=None):
    if not chit_name: chit_name = get_active_chit()
    _process_ai_image(image, chit_name)
    return make_excel_table_en(chit_name, search)

def show_ledger_ai_te(image, search="", chit_name=None):
    if not chit_name: chit_name = get_active_chit()
    _process_ai_image(image, chit_name)
    return make_excel_table_te(chit_name, search)

# ── Create new chit ────────────────────────────────────────────
def _create_chit_core(chit_name, chit_value, num_members, monthly_sub, commission_pct, start_date, member_names_text, default_fields, member_details_json="{}"):
    names = [n.strip() for n in member_names_text.strip().split("\n") if n.strip()]
    if len(names) != int(num_members):
        return None, len(names)
    try:
        details = json.loads(member_details_json) if member_details_json else {}
    except:
        details = {}
    members_list = [{"name": n, "paid": False, "due": int(monthly_sub), "months_paid": 0, "missed": 0,
                     **{f: details.get(n, {}).get(f, "") for f in default_fields}} for n in names]
    new_data = {
        "chit_name": chit_name, "chit_value": int(chit_value), "members": int(num_members),
        "monthly_sub": int(monthly_sub), "commission_pct": float(commission_pct),
        "winning_bid": 0, "current_month": 1, "start_date": str(start_date),
        "custom_fields": list(default_fields), "members_list": members_list
    }
    save_chit(chit_name, new_data)
    index = load_index()
    if chit_name not in index["chits"]:
        index["chits"].append(chit_name)
    index["active"] = chit_name
    save_index(index)
    return new_data, None

def create_new_chit_en(chit_name, chit_value, num_members, monthly_sub, commission_pct, start_date, member_names_text, member_details_json="{}"):
    if not all([chit_name, chit_value, num_members, monthly_sub, member_names_text]):
        return "⚠️ Please fill all required fields!", gr.update(), gr.update(), EMPTY_HOME, gr.Tabs(selected=1)
    result, err = _create_chit_core(chit_name, chit_value, num_members, monthly_sub, commission_pct,
                                    start_date, member_names_text, ["Phone", "Address", "Guarantor", "Loan Taken", "Notes"], member_details_json)
    if err is not None:
        return f"⚠️ You entered {err} names but specified {int(num_members)} members!", gr.update(), gr.update(), EMPTY_HOME, gr.Tabs(selected=1)
    all_chits = get_all_chits()
    return (
        f"✅ '{chit_name}' created with {int(num_members)} members!",
        gr.update(choices=all_chits, value=chit_name),
        gr.update(choices=all_chits, value=chit_name),
        get_home_cards_en(chit_name),
        gr.Tabs(selected=3),   # switch to Home tab
    )

def create_new_chit_te(chit_name, chit_value, num_members, monthly_sub, commission_pct, start_date, member_names_text, member_details_json="{}"):
    if not all([chit_name, chit_value, num_members, monthly_sub, member_names_text]):
        return "⚠️ దయచేసి అన్ని అవసరమైన ఫీల్డ్‌లను పూరించండి!", gr.update(), gr.update(), EMPTY_HOME, gr.Tabs(selected=1)
    result, err = _create_chit_core(chit_name, chit_value, num_members, monthly_sub, commission_pct,
                                    start_date, member_names_text, ["ఫోన్", "చిరునామా", "గ్యారెంటర్", "అప్పు తీసుకున్నారా", "గమనికలు"], member_details_json)
    if err is not None:
        return f"⚠️ మీరు {err} పేర్లు నమోదు చేశారు కానీ {int(num_members)} సభ్యులు పేర్కొన్నారు!", gr.update(), gr.update(), EMPTY_HOME, gr.Tabs(selected=1)
    all_chits = get_all_chits()
    return (
        f"✅ '{chit_name}' {int(num_members)} సభ్యులతో సృష్టించబడింది!",
        gr.update(choices=all_chits, value=chit_name),
        gr.update(choices=all_chits, value=chit_name),
        get_home_cards_te(chit_name),
        gr.Tabs(selected=3),   # switch to Home tab
    )

# ── Custom fields ──────────────────────────────────────────────
def _add_field(field, chit_name):
    data = load_chit(chit_name)
    if not data or field in data["custom_fields"]:
        return data, False
    data["custom_fields"].append(field)
    for m in data["members_list"]:
        m[field] = ""
    save_chit(chit_name, data)
    return data, True

def _remove_field(field, chit_name):
    data = load_chit(chit_name)
    if not data or field not in data["custom_fields"]:
        return data, False
    data["custom_fields"].remove(field)
    for m in data["members_list"]:
        m.pop(field, None)
    save_chit(chit_name, data)
    return data, True

def add_custom_field_en(field_name, suggested, chit_name=None):
    field = field_name.strip() if field_name and field_name.strip() else suggested
    if not field: return "⚠️ Enter a field name first!", gr.update(), gr.update(), make_excel_table_en(chit_name)
    if not chit_name: chit_name = get_active_chit()
    data, ok = _add_field(field, chit_name)
    if not ok: return f"⚠️ '{field}' already exists!", gr.update(), gr.update(), make_excel_table_en(chit_name)
    f = data["custom_fields"]
    return f"✅ Field '{field}' added!", gr.update(choices=f), gr.update(choices=f), make_excel_table_en(chit_name)

def remove_custom_field_en(field_name, chit_name=None):
    if not field_name: return "⚠️ Select a field to remove!", gr.update(), gr.update(), make_excel_table_en(chit_name)
    if not chit_name: chit_name = get_active_chit()
    data, ok = _remove_field(field_name, chit_name)
    if not ok: return "Field not found!", gr.update(), gr.update(), make_excel_table_en(chit_name)
    f = data["custom_fields"]
    return f"✅ Field '{field_name}' removed!", gr.update(choices=f), gr.update(choices=f), make_excel_table_en(chit_name)

def add_custom_field_te(field_name, suggested, chit_name=None):
    field = field_name.strip() if field_name and field_name.strip() else suggested
    if not field: return "⚠️ ముందు ఫీల్డ్ పేరు నమోదు చేయండి!", gr.update(), gr.update(), make_excel_table_te(chit_name)
    if not chit_name: chit_name = get_active_chit()
    data, ok = _add_field(field, chit_name)
    if not ok: return f"⚠️ '{field}' ఇప్పటికే ఉంది!", gr.update(), gr.update(), make_excel_table_te(chit_name)
    f = data["custom_fields"]
    return f"✅ ఫీల్డ్ '{field}' జోడించబడింది!", gr.update(choices=f), gr.update(choices=f), make_excel_table_te(chit_name)

def remove_custom_field_te(field_name, chit_name=None):
    if not field_name: return "⚠️ తొలగించడానికి ఫీల్డ్ ఎంచుకోండి!", gr.update(), gr.update(), make_excel_table_te(chit_name)
    if not chit_name: chit_name = get_active_chit()
    data, ok = _remove_field(field_name, chit_name)
    if not ok: return "ఫీల్డ్ కనుగొనబడలేదు!", gr.update(), gr.update(), make_excel_table_te(chit_name)
    f = data["custom_fields"]
    return f"✅ ఫీల్డ్ '{field_name}' తొలగించబడింది!", gr.update(choices=f), gr.update(choices=f), make_excel_table_te(chit_name)

# ── Member details form generator ─────────────────────────────
def generate_member_fields_en(member_names_text):
    names = [n.strip() for n in member_names_text.strip().split("\n") if n.strip()]
    if not names:
        return gr.update(visible=False), "{}"
    fields = ["Phone", "Address", "Guarantor", "Loan Taken", "Notes"]
    sections = ""
    for name in names:
        field_inputs = "".join([f"""
            <div style='margin-bottom:8px'>
                <label style='font-size:12px;color:#94a3b8;display:block;margin-bottom:4px'>{f}</label>
                <input type='text' id='field_{name}_{f}' placeholder='{f}'
                    style='width:100%;padding:8px 12px;border-radius:8px;border:1px solid rgba(255,255,255,0.1);
                    background:rgba(255,255,255,0.05);color:white;font-size:13px;box-sizing:border-box'
                    oninput='updateMemberDetails()'>
            </div>""" for f in fields])
        sections += f"""
        <details style='margin-bottom:10px;border:1px solid rgba(0,242,254,0.2);border-radius:12px;padding:12px 16px;background:rgba(0,242,254,0.03)'>
            <summary style='cursor:pointer;font-weight:600;color:#00f2fe;font-size:14px'>👤 {name}</summary>
            <div style='margin-top:12px'>{field_inputs}</div>
        </details>"""
    names_json = json.dumps(names)
    fields_json = json.dumps(fields)
    html = f"""
    <div id='member_details_wrapper'>
        {sections}
    </div>
    <script>
    window._memberNames = {names_json};
    window._memberFields = {fields_json};
    function updateMemberDetails() {{
        var result = {{}};
        window._memberNames.forEach(function(name) {{
            result[name] = {{}};
            window._memberFields.forEach(function(field) {{
                var el = document.getElementById('field_' + name + '_' + field);
                result[name][field] = el ? el.value : '';
            }});
        }});
        var jsonStr = JSON.stringify(result);
        // push into the hidden gradio textbox
        var tb = document.querySelector('textarea[data-testid="member_details_json_en"], textarea[label="member_details_json_en"]');
        if(!tb) tb = Array.from(document.querySelectorAll('textarea')).find(el => el.closest('[data-testid]') && el.closest('[data-testid]').getAttribute('data-testid') === 'member_details_json_en');
        if(!tb) {{
            // fallback: find by label proximity — use a global store instead
            window._latestMemberDetailsEN = jsonStr;
        }} else {{
            var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
            nativeInputValueSetter.call(tb, jsonStr);
            tb.dispatchEvent(new Event('input', {{ bubbles: true }}));
        }}
    }}
    </script>"""
    return gr.update(visible=True, value=html), "{}"

def generate_member_fields_te(member_names_text):
    names = [n.strip() for n in member_names_text.strip().split("\n") if n.strip()]
    if not names:
        return gr.update(visible=False), "{}"
    fields = ["ఫోన్", "చిరునామా", "గ్యారెంటర్", "అప్పు తీసుకున్నారా", "గమనికలు"]
    sections = ""
    for name in names:
        field_inputs = "".join([f"""
            <div style='margin-bottom:8px'>
                <label style='font-size:12px;color:#94a3b8;display:block;margin-bottom:4px'>{f}</label>
                <input type='text' id='field_{name}_{f}' placeholder='{f}'
                    style='width:100%;padding:8px 12px;border-radius:8px;border:1px solid rgba(255,255,255,0.1);
                    background:rgba(255,255,255,0.05);color:white;font-size:13px;box-sizing:border-box'
                    oninput='updateMemberDetailsTe()'>
            </div>""" for f in fields])
        sections += f"""
        <details style='margin-bottom:10px;border:1px solid rgba(0,242,254,0.2);border-radius:12px;padding:12px 16px;background:rgba(0,242,254,0.03)'>
            <summary style='cursor:pointer;font-weight:600;color:#00f2fe;font-size:14px'>👤 {name}</summary>
            <div style='margin-top:12px'>{field_inputs}</div>
        </details>"""
    names_json = json.dumps(names, ensure_ascii=False)
    fields_json = json.dumps(fields, ensure_ascii=False)
    html = f"""
    <div id='member_details_wrapper_te'>
        {sections}
    </div>
    <script>
    window._memberNamesTe = {names_json};
    window._memberFieldsTe = {fields_json};
    function updateMemberDetailsTe() {{
        var result = {{}};
        window._memberNamesTe.forEach(function(name) {{
            result[name] = {{}};
            window._memberFieldsTe.forEach(function(field) {{
                var el = document.getElementById('field_' + name + '_' + field);
                result[name][field] = el ? el.value : '';
            }});
        }});
        window._latestMemberDetailsTE = JSON.stringify(result);
    }}
    </script>"""
    return gr.update(visible=True, value=html), "{}"

# ── CSS ────────────────────────────────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
:root {
    --primary: #00f2fe; --secondary: #3a7bd5; --bg-dark: #0b0e14;
    --card-bg: rgba(255,255,255,0.04); --glass-border: rgba(255,255,255,0.1);
    --text-main: #f8fafc; --text-muted: #94a3b8;
}
body, .gradio-container {
    background: radial-gradient(circle at top right, #1e293b 0%, var(--bg-dark) 100%) !important;
    font-family: 'Times New Roman', Times, serif !important; color: var(--text-main) !important;
}
.action-card {
    background: var(--card-bg) !important; backdrop-filter: blur(12px) !important;
    border: 1px solid var(--glass-border) !important; border-radius: 20px !important;
    transition: all 0.4s cubic-bezier(0.4,0,0.2,1) !important; cursor: pointer !important;
    padding: 30px 20px !important; text-align: center; height: 100% !important;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.action-card:hover {
    transform: translateY(-10px) scale(1.02); background: rgba(255,255,255,0.08) !important;
    border-color: var(--primary) !important; box-shadow: 0 15px 40px rgba(0,242,254,0.15) !important;
}
.nav-bar button, .tab-nav button {
    border: none !important; background: transparent !important;
    color: var(--text-muted) !important; font-weight: 600 !important; transition: 0.3s !important;
}
.nav-bar button:hover, .tab-nav button:hover { color: var(--primary) !important; }
.tab-nav button[aria-selected="true"] { color: var(--primary) !important; border-bottom: 2px solid var(--primary) !important; }
.metric-box {
    background: rgba(255,255,255,0.03) !important; border-radius: 16px !important;
    border-left: 4px solid var(--primary) !important; padding: 20px !important;
    border: 1px solid var(--glass-border);
}
.metric-value { color: var(--primary); font-size: 28px; font-weight: 800; }
.gr-textbox, .gr-number, .gr-dropdown {
    background: rgba(255,255,255,0.05) !important; border: 1px solid var(--glass-border) !important;
    border-radius: 12px !important; color: white !important;
}
.gr-button-primary {
    background: linear-gradient(135deg, var(--secondary) 0%, #2563eb 100%) !important;
    border: none !important; box-shadow: 0 4px 15px rgba(37,99,235,0.2) !important; border-radius: 12px !important;
}
.gr-button-primary:hover { box-shadow: 0 8px 20px rgba(37,99,235,0.4) !important; transform: translateY(-2px); }
#chit-selector-en, #chit-selector-te {
    background: rgba(0,242,254,0.05) !important; border: 1.5px solid var(--primary) !important;
    border-radius: 12px !important; font-weight: 600 !important; color: var(--primary) !important;
}
.lang-toggle-btn {
    background: rgba(0,242,254,0.1) !important; border: 1.5px solid var(--primary) !important;
    border-radius: 20px !important; color: var(--primary) !important; font-weight: 700 !important;
    font-size: 13px !important; padding: 6px 18px !important; cursor: pointer !important;
    transition: all 0.3s ease !important;
}
.lang-toggle-btn:hover { background: rgba(0,242,254,0.2) !important; box-shadow: 0 4px 15px rgba(0,242,254,0.2) !important; }
.delete-btn button { background: rgba(239,68,68,0.15) !important; border: 1px solid rgba(239,68,68,0.4) !important;
    color: #f87171 !important; border-radius: 12px !important; }
.delete-btn button:hover { background: rgba(239,68,68,0.3) !important; }
footer { display: none !important; }
"""

# ── Bootstrap ──────────────────────────────────────────────────
_index   = load_index()
_active  = _index.get("active")
_all     = _index.get("chits", [])
_data    = load_chit(_active) if _active else None
_members = [m["name"] for m in _data["members_list"]] if _data else []

# ── App ────────────────────────────────────────────────────────
with gr.Blocks(title="Chit Fund", css=CSS) as app:

    lang_state = gr.State("en")

    def toggle_language(current_lang):
        if current_lang == "en":
            return "te", gr.update(visible=False), gr.update(visible=True), gr.update(value="తెలుగు → English")
        else:
            return "en", gr.update(visible=True), gr.update(visible=False), gr.update(value="English → తెలుగు")

    # ══════════════════════════════
    # ENGLISH PANEL
    # ══════════════════════════════
    with gr.Column(visible=True) as en_panel:
        with gr.Row(equal_height=True):
            with gr.Column(scale=5):
                gr.HTML("<div style='font-size:32px;font-weight:800;color:var(--primary);font-family:\"Times New Roman\",serif'>🏦 Chit Fund</div>")
                gr.Markdown("### Transparent. Digital. Instant. — Built for India")
            with gr.Column(scale=3):
                chit_sel_en = gr.Dropdown(choices=_all, value=_active, label="Currently viewing", elem_id="chit-selector-en")
            with gr.Column(scale=1, min_width=90):
                del_btn_en = gr.Button("🗑️ Delete", variant="stop", elem_classes=["delete-btn"])
            with gr.Column(scale=1, min_width=110):
                lang_btn = gr.Button("English → తెలుగు", elem_classes=["lang-toggle-btn"])

        del_status_en = gr.Markdown()
        switch_status_en = gr.Markdown()

        with gr.Tabs() as tabs_en:
            with gr.TabItem("🏠 Home", id=0):
                home_en = gr.HTML(get_home_cards_en(_active))
                gr.Markdown("---")
                with gr.Row():
                    with gr.Column(elem_classes=["action-card"]):
                        nc_en = gr.Button("➕\n\nNew Chit Fund\nSetup schema and members", variant="secondary", elem_classes=["action-card"])
                    with gr.Column(elem_classes=["action-card"]):
                        ul_en = gr.Button("📤\n\nUpload & Digitize\nAI extraction from ledgers", variant="secondary", elem_classes=["action-card"])
                with gr.Row():
                    with gr.Column(elem_classes=["action-card"]):
                        db_en = gr.Button("👤\n\nMember Dashboard\nTrack payments and alerts", variant="secondary", elem_classes=["action-card"])
                    with gr.Column(elem_classes=["action-card"]):
                        ac_en = gr.Button("🔨\n\nAuction Calculator\nCalculate bids and dividends", variant="secondary", elem_classes=["action-card"])
                nc_en.click(lambda: gr.Tabs(selected=1), None, tabs_en)
                ul_en.click(lambda: gr.Tabs(selected=2), None, tabs_en)
                db_en.click(lambda: gr.Tabs(selected=3), None, tabs_en)
                ac_en.click(lambda: gr.Tabs(selected=4), None, tabs_en)
                gr.Markdown("<div style='text-align:center;margin-top:24px;color:var(--text-muted);font-size:12px'>Powered by Ollama + EasyOCR + Gradio</div>")

            with gr.TabItem("➕ New Chit Fund", id=1):
                gr.Markdown("### Create a New Chit Fund")
                with gr.Row():
                    cn_en = gr.Textbox(label="Chit Fund Name", placeholder="e.g. Lakshmi Chit Fund")
                    sd_en = gr.Textbox(label="Start Date", value=str(date.today()))
                with gr.Row():
                    cv_en = gr.Number(label="Chit Value (₹)", value=100000)
                    nm_en = gr.Number(label="Number of Members", value=10, precision=0)
                with gr.Row():
                    ms_en = gr.Number(label="Monthly Subscription (₹)", value=5000)
                    cp_en = gr.Number(label="Foreman Commission (%)", value=5)
                gr.Markdown("### Member Names *(one per line)*")
                mn_en = gr.Textbox(label="Member Names", placeholder="Ravi\nLakshmi\nSuresh\n...", lines=10)
                gen_fields_btn_en = gr.Button("📋 Fill Member Details (optional)", variant="secondary")
                member_details_html_en = gr.HTML(value="", visible=False)
                member_details_json_en = gr.Textbox(value="{}", visible=False, label="member_details_json_en")
                cb_en = gr.Button("✅ Create Chit Fund", variant="primary", size="lg")
                co_en = gr.Markdown()
                gr.Markdown("---")
                gr.Markdown("### ⚙️ Manage Fields *(for currently selected chit fund)*")
                with gr.Row():
                    sug_en = gr.Dropdown(choices=SUGGESTED_FIELDS_EN, label="Pick from suggestions", scale=2)
                    cfi_en = gr.Textbox(label="Or type your own field name", scale=2)
                    afb_en = gr.Button("➕ Add Field", variant="primary", scale=1)
                with gr.Row():
                    rfd_en = gr.Dropdown(choices=get_custom_fields_list(_active), label="Select field to remove")
                    rfb_en = gr.Button("🗑️ Remove Field", variant="stop")
                fo_en = gr.Markdown()
                ft_en = gr.HTML()

            with gr.TabItem("📤 Upload & Digitize", id=2):
                gr.Markdown("### Upload a photo of your physical Chit Book")
                gr.Markdown("*The AI agent will read and extract all member data automatically*")
                srch_en = gr.Textbox(label="🔍 Search member by name", placeholder="Type a name...")
                img_en  = gr.Image(label="Chit Book Photo", height=250)
                sub_en  = gr.Button("✨ Digitize with AI", variant="primary", size="lg")
                upl_en  = gr.HTML()
                sub_en.click(show_ledger_ai_en, inputs=[img_en, srch_en, chit_sel_en], outputs=upl_en)
                srch_en.change(lambda s, c: make_excel_table_en(c, s), inputs=[srch_en, chit_sel_en], outputs=upl_en)
                app.load(lambda: make_excel_table_en(get_active_chit()), outputs=upl_en)

            with gr.TabItem("👤 Member Dashboard", id=3):
                gr.Markdown("### Member Ledger")
                gr.Markdown("*Click any row to auto-fill the edit form below*")
                dash_en = gr.HTML()
                gr.Markdown("---")
                mdd_en = gr.Dropdown(choices=_members, label="Select Member",
                                     value=_members[0] if _members else None, elem_id="member_select_en")
                mo_en  = gr.Markdown()
                with gr.Row():
                    sb_en = gr.Button("📱 Send WhatsApp Alert", variant="primary", visible=False)
                ao_en  = gr.Markdown()
                gr.Markdown("---")
                gr.Markdown("### ✏️ Edit Member Record")
                with gr.Row():
                    ea_en = gr.Number(label="Monthly Amount (₹)", precision=0)
                    es_en = gr.Dropdown(choices=["Paid", "Unpaid"], label="Payment Status")
                cfe_en = gr.Textbox(label="Custom Field Values (JSON — auto filled on row click)", lines=3,
                                    placeholder='{"Phone": "9999999999", "Address": "Hyderabad"}')
                eb_en  = gr.Button("💾 Save Changes", variant="primary")
                eo_en  = gr.Markdown()
                mdd_en.change(lambda n, c: show_member_en(n, c), inputs=[mdd_en, chit_sel_en],
                              outputs=[mo_en, sb_en, ea_en, es_en, cfe_en])
                sb_en.click(send_alert_en, inputs=mdd_en, outputs=ao_en)
                eb_en.click(edit_member_en, inputs=[mdd_en, ea_en, es_en, cfe_en, chit_sel_en],
                            outputs=[eo_en, dash_en])
                app.load(lambda: make_excel_table_en(get_active_chit()), outputs=dash_en)
                app.load(lambda: show_member_en(_members[0] if _members else "", get_active_chit()),
                         outputs=[mo_en, sb_en, ea_en, es_en, cfe_en])

            with gr.TabItem("🔨 Auction Calculator", id=4):
                gr.Markdown("### Calculate dividend for any winning bid")
                bid_en  = gr.Number(label="Enter Winning Bid (₹)", value=15000, minimum=1000, maximum=99000)
                calb_en = gr.Button("Calculate", variant="primary")
                auco_en = gr.Markdown()
                calb_en.click(calculate_auction_en, inputs=[bid_en, chit_sel_en], outputs=auco_en)
                app.load(lambda: calculate_auction_en(15000, get_active_chit()), outputs=auco_en)

        # Wire EN buttons
        gen_fields_btn_en.click(generate_member_fields_en,
            inputs=[mn_en],
            outputs=[member_details_html_en, member_details_json_en])
        cb_en.click(create_new_chit_en,
            inputs=[cn_en, cv_en, nm_en, ms_en, cp_en, sd_en, mn_en, member_details_json_en],
            outputs=[co_en, chit_sel_en, chit_sel_en, home_en, tabs_en])
        afb_en.click(add_custom_field_en, inputs=[cfi_en, sug_en, chit_sel_en], outputs=[fo_en, sug_en, rfd_en, ft_en])
        rfb_en.click(remove_custom_field_en, inputs=[rfd_en, chit_sel_en], outputs=[fo_en, sug_en, rfd_en, ft_en])
        chit_sel_en.change(switch_chit_en, inputs=chit_sel_en,
            outputs=[home_en, upl_en, dash_en, mdd_en, auco_en, switch_status_en, chit_sel_en])
        del_btn_en.click(delete_chit_en, inputs=chit_sel_en,
            outputs=[del_status_en, chit_sel_en, chit_sel_en, home_en, upl_en, dash_en, mdd_en, auco_en])

    # ══════════════════════════════
    # TELUGU PANEL
    # ══════════════════════════════
    with gr.Column(visible=False) as te_panel:
        with gr.Row(equal_height=True):
            with gr.Column(scale=5):
                gr.HTML("<div style='font-size:32px;font-weight:800;color:var(--primary);font-family:\"Times New Roman\",serif'>🏦 చిట్‌ఫండ్</div>")
                gr.Markdown("### పారదర్శకంగా. డిజిటల్‌గా. తక్షణమే. — భారతదేశం కోసం")
            with gr.Column(scale=3):
                chit_sel_te = gr.Dropdown(choices=_all, value=_active, label="ప్రస్తుతం చూస్తున్నది", elem_id="chit-selector-te")
            with gr.Column(scale=1, min_width=90):
                del_btn_te = gr.Button("🗑️ తొలగించు", variant="stop", elem_classes=["delete-btn"])
            with gr.Column(scale=1, min_width=110):
                lang_btn_te = gr.Button("తెలుగు → English", elem_classes=["lang-toggle-btn"])

        del_status_te = gr.Markdown()
        switch_status_te = gr.Markdown()

        with gr.Tabs() as tabs_te:
            with gr.TabItem("🏠 హోమ్", id=0):
                home_te = gr.HTML(get_home_cards_te(_active))
                gr.Markdown("---")
                with gr.Row():
                    with gr.Column(elem_classes=["action-card"]):
                        nc_te = gr.Button("➕\n\nకొత్త చిట్ ఫండ్\nస్కీమా మరియు సభ్యుల సెటప్", variant="secondary", elem_classes=["action-card"])
                    with gr.Column(elem_classes=["action-card"]):
                        ul_te = gr.Button("📤\n\nఅప్‌లోడ్ & డిజిటైజ్\nAI ద్వారా లెడ్జర్ వెలికితీత", variant="secondary", elem_classes=["action-card"])
                with gr.Row():
                    with gr.Column(elem_classes=["action-card"]):
                        db_te = gr.Button("👤\n\nసభ్యుల డాష్‌బోర్డ్\nచెల్లింపులు మరియు హెచ్చరికలు", variant="secondary", elem_classes=["action-card"])
                    with gr.Column(elem_classes=["action-card"]):
                        ac_te = gr.Button("🔨\n\nవేలం కాలిక్యులేటర్\nబిడ్‌లు మరియు డివిడెండ్‌లు", variant="secondary", elem_classes=["action-card"])
                nc_te.click(lambda: gr.Tabs(selected=1), None, tabs_te)
                ul_te.click(lambda: gr.Tabs(selected=2), None, tabs_te)
                db_te.click(lambda: gr.Tabs(selected=3), None, tabs_te)
                ac_te.click(lambda: gr.Tabs(selected=4), None, tabs_te)
                gr.Markdown("<div style='text-align:center;margin-top:24px;color:var(--text-muted);font-size:12px'>Ollama + EasyOCR + Gradio తో నిర్మించబడింది</div>")

            with gr.TabItem("➕ కొత్త చిట్ ఫండ్", id=1):
                gr.Markdown("### కొత్త చిట్ ఫండ్ సృష్టించండి")
                with gr.Row():
                    cn_te = gr.Textbox(label="చిట్ ఫండ్ పేరు", placeholder="ఉదా: లక్ష్మి చిట్ ఫండ్")
                    sd_te = gr.Textbox(label="ప్రారంభ తేదీ", value=str(date.today()))
                with gr.Row():
                    cv_te = gr.Number(label="చిట్ విలువ (₹)", value=100000)
                    nm_te = gr.Number(label="సభ్యుల సంఖ్య", value=10, precision=0)
                with gr.Row():
                    ms_te = gr.Number(label="నెలవారీ చందా (₹)", value=5000)
                    cp_te = gr.Number(label="ఫోర్‌మన్ కమీషన్ (%)", value=5)
                gr.Markdown("### సభ్యుల పేర్లు *(ఒక్కో వరుసలో)*")
                mn_te = gr.Textbox(label="సభ్యుల పేర్లు", placeholder="రవి\nలక్ష్మి\nసురేష్\n...", lines=10)
                gen_fields_btn_te = gr.Button("📋 సభ్యుల వివరాలు నింపండి (ఐచ్ఛికం)", variant="secondary")
                member_details_html_te = gr.HTML(value="", visible=False)
                member_details_json_te = gr.Textbox(value="{}", visible=False, label="member_details_json_te")
                cb_te = gr.Button("✅ చిట్ ఫండ్ సృష్టించండి", variant="primary", size="lg")
                co_te = gr.Markdown()
                gr.Markdown("---")
                gr.Markdown("### ⚙️ ఫీల్డ్‌లు నిర్వహించండి")
                with gr.Row():
                    sug_te = gr.Dropdown(choices=SUGGESTED_FIELDS_TE, label="సూచనల నుండి ఎంచుకోండి", scale=2)
                    cfi_te = gr.Textbox(label="లేదా మీ స్వంత ఫీల్డ్ పేరు టైప్ చేయండి", scale=2)
                    afb_te = gr.Button("➕ ఫీల్డ్ జోడించు", variant="primary", scale=1)
                with gr.Row():
                    rfd_te = gr.Dropdown(choices=get_custom_fields_list(_active), label="తొలగించడానికి ఫీల్డ్ ఎంచుకోండి")
                    rfb_te = gr.Button("🗑️ ఫీల్డ్ తొలగించు", variant="stop")
                fo_te = gr.Markdown()
                ft_te = gr.HTML()

            with gr.TabItem("📤 అప్‌లోడ్ & డిజిటైజ్", id=2):
                gr.Markdown("### మీ చిట్ బుక్ ఫోటో అప్‌లోడ్ చేయండి")
                srch_te = gr.Textbox(label="🔍 పేరు ద్వారా వెతకండి", placeholder="పేరు టైప్ చేయండి...")
                img_te  = gr.Image(label="చిట్ బుక్ ఫోటో", height=250)
                sub_te  = gr.Button("✨ AI తో డిజిటైజ్ చేయండి", variant="primary", size="lg")
                upl_te  = gr.HTML()
                sub_te.click(show_ledger_ai_te, inputs=[img_te, srch_te, chit_sel_te], outputs=upl_te)
                srch_te.change(lambda s, c: make_excel_table_te(c, s), inputs=[srch_te, chit_sel_te], outputs=upl_te)
                app.load(lambda: make_excel_table_te(get_active_chit()), outputs=upl_te)

            with gr.TabItem("👤 సభ్యుల డాష్‌బోర్డ్", id=3):
                gr.Markdown("### సభ్యుల లెడ్జర్")
                gr.Markdown("*ఏదైనా వరుసపై క్లిక్ చేయండి — ఫారమ్ ఆటోమేటిక్‌గా నింపబడుతుంది*")
                dash_te = gr.HTML()
                gr.Markdown("---")
                mdd_te = gr.Dropdown(choices=_members, label="సభ్యుడిని ఎంచుకోండి",
                                     value=_members[0] if _members else None, elem_id="member_select_te")
                mo_te  = gr.Markdown()
                with gr.Row():
                    sb_te = gr.Button("📱 వాట్సాప్ అలర్ట్ పంపండి", variant="primary", visible=False)
                ao_te  = gr.Markdown()
                gr.Markdown("---")
                gr.Markdown("### ✏️ రికార్డ్ సవరించు")
                with gr.Row():
                    ea_te = gr.Number(label="నెలవారీ మొత్తం (₹)", precision=0)
                    es_te = gr.Dropdown(choices=["చెల్లించారు", "చెల్లించలేదు"], label="చెల్లింపు స్థితి")
                cfe_te = gr.Textbox(label="కస్టమ్ ఫీల్డ్ విలువలు (JSON)", lines=3, placeholder='{"ఫోన్": "9999999999"}')
                eb_te  = gr.Button("💾 మార్పులు సేవ్ చేయండి", variant="primary")
                eo_te  = gr.Markdown()
                mdd_te.change(lambda n, c: show_member_te(n, c), inputs=[mdd_te, chit_sel_te],
                              outputs=[mo_te, sb_te, ea_te, es_te, cfe_te])
                sb_te.click(send_alert_te, inputs=mdd_te, outputs=ao_te)
                eb_te.click(edit_member_te, inputs=[mdd_te, ea_te, es_te, cfe_te, chit_sel_te],
                            outputs=[eo_te, dash_te])
                app.load(lambda: make_excel_table_te(get_active_chit()), outputs=dash_te)
                app.load(lambda: show_member_te(_members[0] if _members else "", get_active_chit()),
                         outputs=[mo_te, sb_te, ea_te, es_te, cfe_te])

            with gr.TabItem("🔨 వేలం కాలిక్యులేటర్", id=4):
                gr.Markdown("### గెలిచిన బిడ్‌కు డివిడెండ్ లెక్కించండి")
                bid_te  = gr.Number(label="గెలిచిన బిడ్ నమోదు చేయండి (₹)", value=15000, minimum=1000, maximum=99000)
                calb_te = gr.Button("లెక్కించండి", variant="primary")
                auco_te = gr.Markdown()
                calb_te.click(calculate_auction_te, inputs=[bid_te, chit_sel_te], outputs=auco_te)
                app.load(lambda: calculate_auction_te(15000, get_active_chit()), outputs=auco_te)

        # Wire TE buttons
        gen_fields_btn_te.click(generate_member_fields_te,
            inputs=[mn_te],
            outputs=[member_details_html_te, member_details_json_te])
        cb_te.click(create_new_chit_te,
            inputs=[cn_te, cv_te, nm_te, ms_te, cp_te, sd_te, mn_te, member_details_json_te],
            outputs=[co_te, chit_sel_te, chit_sel_en, home_te, tabs_te])
        afb_te.click(add_custom_field_te, inputs=[cfi_te, sug_te, chit_sel_te], outputs=[fo_te, sug_te, rfd_te, ft_te])
        rfb_te.click(remove_custom_field_te, inputs=[rfd_te, chit_sel_te], outputs=[fo_te, sug_te, rfd_te, ft_te])
        chit_sel_te.change(switch_chit_te, inputs=chit_sel_te,
            outputs=[home_te, upl_te, dash_te, mdd_te, auco_te, switch_status_te, chit_sel_te])
        del_btn_te.click(delete_chit_te, inputs=chit_sel_te,
            outputs=[del_status_te, chit_sel_te, chit_sel_en, home_te, upl_te, dash_te, mdd_te, auco_te])

    # ── Cross-sync selectors ───────────────────────────────────
    chit_sel_en.change(lambda c: gr.update(choices=get_all_chits(), value=c), inputs=chit_sel_en, outputs=chit_sel_te)
    chit_sel_te.change(lambda c: gr.update(choices=get_all_chits(), value=c), inputs=chit_sel_te, outputs=chit_sel_en)

    # ── Language toggle ────────────────────────────────────────
    lang_btn.click(toggle_language, inputs=lang_state, outputs=[lang_state, en_panel, te_panel, lang_btn])
    lang_btn_te.click(toggle_language, inputs=lang_state, outputs=[lang_state, en_panel, te_panel, lang_btn])

if __name__ == "__main__":
    app.launch(server_port=7860)