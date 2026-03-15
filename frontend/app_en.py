import gradio as gr
import pandas as pd
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

DATA_FILE = "../data/chit_data.json"
DEFAULT_FIELDS = ["Phone", "Address", "Guarantor", "Loan Taken", "Notes"]
SUGGESTED_FIELDS = ["Occupation", "Aadhar Number", "Bank Account", "Email", "Emergency Contact"]

os.makedirs("../data", exist_ok=True)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
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
            {"name": "Lakshmi","paid": True,  "due": 0,    "months_paid": 3, "missed": 0, "Phone": "", "Address": "", "Guarantor": "", "Loan Taken": "No",  "Notes": ""},
            {"name": "Suresh", "paid": False, "due": 5000, "months_paid": 2, "missed": 2, "Phone": "", "Address": "", "Guarantor": "", "Loan Taken": "Yes", "Notes": ""},
            {"name": "Priya",  "paid": True,  "due": 0,    "months_paid": 3, "missed": 0, "Phone": "", "Address": "", "Guarantor": "", "Loan Taken": "No",  "Notes": ""},
            {"name": "Ramesh", "paid": False, "due": 5000, "months_paid": 1, "missed": 3, "Phone": "", "Address": "", "Guarantor": "", "Loan Taken": "Yes", "Notes": ""},
            {"name": "Sita",   "paid": True,  "due": 0,    "months_paid": 3, "missed": 0, "Phone": "", "Address": "", "Guarantor": "", "Loan Taken": "No",  "Notes": ""},
            {"name": "Kiran",  "paid": True,  "due": 0,    "months_paid": 3, "missed": 0, "Phone": "", "Address": "", "Guarantor": "", "Loan Taken": "No",  "Notes": ""},
            {"name": "Deepa",  "paid": False, "due": 5000, "months_paid": 2, "missed": 2, "Phone": "", "Address": "", "Guarantor": "", "Loan Taken": "No",  "Notes": ""},
            {"name": "Arjun",  "paid": True,  "due": 0,    "months_paid": 3, "missed": 0, "Phone": "", "Address": "", "Guarantor": "", "Loan Taken": "No",  "Notes": ""},
            {"name": "Meena",  "paid": True,  "due": 0,    "months_paid": 3, "missed": 0, "Phone": "", "Address": "", "Guarantor": "", "Loan Taken": "No",  "Notes": ""},
        ]
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def calculate_summary(data):
    chit_value = data["chit_value"]
    winning_bid = data.get("winning_bid", 0)
    num_members = data["members"]
    commission = round(chit_value * data["commission_pct"] / 100, 2)
    dividend = round((winning_bid - commission) / num_members, 2) if winning_bid > 0 else 0
    prized_amount = chit_value - winning_bid
    total_collected = sum(m["months_paid"] * data["monthly_sub"] for m in data["members_list"])
    pending = sum(m["due"] for m in data["members_list"])
    paid_count = sum(1 for m in data["members_list"] if m["paid"])
    return commission, dividend, prized_amount, total_collected, pending, paid_count

def get_home_cards():
    data = load_data()
    commission, dividend, prized_amount, total_collected, pending, paid_count = calculate_summary(data)
    return f"""
<div style='display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px'>
    <div style='background:#e8f5f3;padding:20px;border-radius:12px;text-align:center;border:1.5px solid #2a9d8f'>
        <div style='font-size:32px;font-weight:bold;color:#2a9d8f'>{data['members']}</div>
        <div style='font-size:13px;margin-top:4px;color:#264653;font-weight:500'>Total Members</div>
    </div>
    <div style='background:#fefae0;padding:20px;border-radius:12px;text-align:center;border:1.5px solid #e9c46a'>
        <div style='font-size:32px;font-weight:bold;color:#e76f51'>₹{total_collected:,}</div>
        <div style='font-size:13px;margin-top:4px;color:#264653;font-weight:500'>Total Collected</div>
    </div>
    <div style='background:#fff0e6;padding:20px;border-radius:12px;text-align:center;border:1.5px solid #f4a261'>
        <div style='font-size:32px;font-weight:bold;color:#f4a261'>₹{pending:,}</div>
        <div style='font-size:13px;margin-top:4px;color:#264653;font-weight:500'>Pending Dues</div>
    </div>
    <div style='background:#e8f5f3;padding:20px;border-radius:12px;text-align:center;border:1.5px solid #2a9d8f'>
        <div style='font-size:32px;font-weight:bold;color:#264653'>₹{dividend:,.0f}</div>
        <div style='font-size:13px;margin-top:4px;color:#264653;font-weight:500'>Dividend / Member</div>
    </div>
</div>"""

def make_excel_table(members_list, custom_fields, monthly_sub, current_month):
    header_cols = ["#", "Member Name", "Monthly (₹)", "Status", "Dividend (₹)", "Due (₹)", "Months Paid"] + custom_fields
    headers = "".join([f"<th style='background:#2a9d8f;color:#fefae0;padding:10px 14px;text-align:left;font-weight:600;font-size:13px;white-space:nowrap;border-right:1px solid #1e7d72'>{h}</th>" for h in header_cols])

    rows_html = ""
    data = load_data()
    commission, dividend, _, _, _, _ = calculate_summary(data)

    for i, m in enumerate(members_list):
        if m["missed"] >= 2:
            status_badge = "<span style='background:#fff3cd;color:#856404;padding:3px 10px;border-radius:12px;font-size:12px;font-weight:500'>⚠️ Flagged</span>"
        elif m["paid"]:
            status_badge = "<span style='background:#d1fae5;color:#065f46;padding:3px 10px;border-radius:12px;font-size:12px;font-weight:500'>✅ Paid</span>"
        else:
            status_badge = "<span style='background:#fee2e2;color:#991b1b;padding:3px 10px;border-radius:12px;font-size:12px;font-weight:500'>❌ Unpaid</span>"

        row_bg = "#ffffff" if i % 2 == 0 else "#f8fffe"
        custom_cells = "".join([f"<td style='padding:10px 14px;font-size:13px;border-bottom:1px solid #e2f4f1;border-right:1px solid #e2f4f1'>{m.get(field, '')}</td>" for field in custom_fields])

        rows_html += f"""
        <tr style='background:{row_bg}' onmouseover="this.style.background='#e8f5f3'" onmouseout="this.style.background='{row_bg}'" onclick="document.getElementById('member_select').value='{m['name']}';document.getElementById('member_select').dispatchEvent(new Event('change'))">
            <td style='padding:10px 14px;font-size:13px;color:#2a9d8f;font-weight:600;border-bottom:1px solid #e2f4f1;border-right:1px solid #e2f4f1'>{i+1}</td>
            <td style='padding:10px 14px;font-size:13px;font-weight:500;border-bottom:1px solid #e2f4f1;border-right:1px solid #e2f4f1'>{m['name']}</td>
            <td style='padding:10px 14px;font-size:13px;border-bottom:1px solid #e2f4f1;border-right:1px solid #e2f4f1'>₹{monthly_sub:,}</td>
            <td style='padding:10px 14px;border-bottom:1px solid #e2f4f1;border-right:1px solid #e2f4f1'>{status_badge}</td>
            <td style='padding:10px 14px;font-size:13px;color:#2a9d8f;font-weight:500;border-bottom:1px solid #e2f4f1;border-right:1px solid #e2f4f1'>₹{dividend:,.0f}</td>
            <td style='padding:10px 14px;font-size:13px;color:{"#e76f51" if m["due"] > 0 else "#2a9d8f"};font-weight:500;border-bottom:1px solid #e2f4f1;border-right:1px solid #e2f4f1'>₹{m["due"]:,}</td>
            <td style='padding:10px 14px;font-size:13px;border-bottom:1px solid #e2f4f1;border-right:1px solid #e2f4f1'>{m["months_paid"]}/{current_month}</td>
            {custom_cells}
        </tr>"""

    return f"""
<div style='overflow-x:auto;border-radius:12px;border:1.5px solid #2a9d8f;margin-top:8px'>
    <table style='width:100%;border-collapse:collapse;font-family:sans-serif'>
        <thead><tr>{headers}</tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
</div>
<p style='font-size:12px;color:#64748b;margin-top:6px'>💡 Click any row to view member details below</p>"""

def get_ledger_html(search=""):
    data = load_data()
    members = data["members_list"]
    if search:
        members = [m for m in members if search.lower() in m["name"].lower()]
    return make_excel_table(members, data.get("custom_fields", []), data["monthly_sub"], data["current_month"])

def show_ledger_ai(image, search=""):
    data = load_data()
    if image is not None and AI_AVAILABLE:
        try:
            img = Image.fromarray(image.astype('uint8'))
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            img.save(tmp.name)
            result = process_image(tmp.name)
            os.unlink(tmp.name)
            members_from_ai = result.get("members", [])
            if members_from_ai:
                for m in data["members_list"]:
                    for ai_m in members_from_ai:
                        if ai_m.get("name", "").lower() in m["name"].lower():
                            m["paid"] = ai_m.get("amount_paid", 0) > 0
                            m["due"] = 0 if m["paid"] else data["monthly_sub"]
                save_data(data)
        except Exception as e:
            print(f"AI processing failed: {e}")
    return get_ledger_html(search)

def calculate_auction(winning_bid):
    if not winning_bid:
        return ""
    data = load_data()
    winning_bid = float(winning_bid)
    commission = round(data["chit_value"] * data["commission_pct"] / 100, 2)
    dividend = round((winning_bid - commission) / data["members"], 2)
    prized_amount = data["chit_value"] - winning_bid
    net_installment = data["monthly_sub"] - dividend
    data["winning_bid"] = int(winning_bid)
    save_data(data)
    return f"""
### 🔨 Auction Result

| Detail | Amount |
|---|---|
| Chit Value | ₹{data['chit_value']:,} |
| Winning Bid | ₹{winning_bid:,.0f} |
| **Prized Amount** | **₹{prized_amount:,.0f}** |
| Foreman Commission ({data['commission_pct']}%) | ₹{commission:,.0f} |
| **Dividend per Member** | **₹{dividend:,.0f}** |
| Net Installment to Pay | ₹{net_installment:,.0f} |

> 💡 Each member pays ₹{net_installment:,.0f} this month instead of ₹{data['monthly_sub']:,}
"""

def show_member(name):
    if not name:
        return "", gr.update(visible=False)
    data = load_data()
    commission, dividend, _, _, _, _ = calculate_summary(data)
    for m in data["members_list"]:
        if m["name"] == name:
            flag_text = f"\n> ⚠️ **Warning:** This member has missed {m['missed']} payments!" if m["missed"] >= 2 else ""
            custom_rows = "".join([f"| {field} | {m.get(field, '-')} |\n" for field in data.get("custom_fields", [])])
            whatsapp = f"""📱 *WhatsApp Alert Preview*

Hello {m['name']}! 🙏

Your Chit Fund Details:
- Monthly: ₹{data['monthly_sub']:,}
- Dividend: ₹{dividend:.0f}
- Amount Due: ₹{m['due']:,}
- Status: {'✅ Paid' if m['paid'] else '❌ Unpaid'}

_ChitSync_ ✨"""
            info = f"""
## 👤 {m['name']}
{flag_text}

| Detail | Value |
|--------|-------|
| Monthly Contribution | ₹{data['monthly_sub']:,} |
| Payment Status | {'✅ Paid' if m['paid'] else '❌ Unpaid'} |
| Months Paid | {m['months_paid']} of {data['current_month']} |
| Missed Payments | {m['missed']} |
| Dividend This Month | ₹{dividend:.0f} |
| Net Amount Due | ₹{m['due']:,} |
{custom_rows}
---
{whatsapp}
"""
            return info, gr.update(visible=True)
    return "Member not found", gr.update(visible=False)

def send_alert(name):
    if not name:
        return "⚠️ Please select a member first"
    return f"✅ WhatsApp alert sent to {name} successfully!"

def edit_member(name, new_status):
    if not name:
        return "⚠️ Please select a member first", get_ledger_html()
    data = load_data()
    for m in data["members_list"]:
        if m["name"] == name:
            if new_status == "Paid":
                m["paid"] = True
                m["due"] = 0
                m["months_paid"] += 1
                m["missed"] = 0
            elif new_status == "Unpaid":
                m["paid"] = False
                m["due"] = data["monthly_sub"]
                m["missed"] += 1
            save_data(data)
            return f"✅ Record updated for {name}!", get_ledger_html()
    return "Member not found", get_ledger_html()

def create_new_chit(chit_name, chit_value, num_members, monthly_sub, commission_pct, start_date, member_names_text):
    if not all([chit_name, chit_value, num_members, monthly_sub, member_names_text]):
        return "⚠️ Please fill all required fields!", ""
    names = [n.strip() for n in member_names_text.strip().split("\n") if n.strip()]
    if len(names) != int(num_members):
        return f"⚠️ You entered {len(names)} names but specified {int(num_members)} members!", ""
    members_list = [{"name": n, "paid": False, "due": int(monthly_sub), "months_paid": 0, "missed": 0,
                     "Phone": "", "Address": "", "Guarantor": "", "Loan Taken": "No", "Notes": ""} for n in names]
    new_data = {
        "chit_name": chit_name,
        "chit_value": int(chit_value),
        "members": int(num_members),
        "monthly_sub": int(monthly_sub),
        "commission_pct": float(commission_pct),
        "winning_bid": 0,
        "current_month": 1,
        "start_date": str(start_date),
        "custom_fields": ["Phone", "Address", "Guarantor", "Loan Taken", "Notes"],
        "members_list": members_list
    }
    save_data(new_data)
    table = make_excel_table(members_list, new_data["custom_fields"], int(monthly_sub), 1)
    return f"✅ '{chit_name}' created with {int(num_members)} members!", table

def add_custom_field(field_name, suggested):
    field = field_name if field_name else suggested
    if not field:
        return "⚠️ Enter a field name first!", gr.update(), get_ledger_html()
    data = load_data()
    if field in data["custom_fields"]:
        return f"⚠️ '{field}' already exists!", gr.update(), get_ledger_html()
    data["custom_fields"].append(field)
    for m in data["members_list"]:
        m[field] = ""
    save_data(data)
    return f"✅ Field '{field}' added!", gr.update(choices=data["custom_fields"]), get_ledger_html()

def remove_custom_field(field_name):
    if not field_name:
        return "⚠️ Select a field to remove!", gr.update(), get_ledger_html()
    data = load_data()
    if field_name in DEFAULT_FIELDS:
        return f"⚠️ Cannot remove default field '{field_name}'!", gr.update(), get_ledger_html()
    data["custom_fields"].remove(field_name)
    for m in data["members_list"]:
        m.pop(field_name, None)
    save_data(data)
    return f"✅ Field '{field_name}' removed!", gr.update(choices=data["custom_fields"]), get_ledger_html()

def get_custom_fields_list():
    return load_data().get("custom_fields", DEFAULT_FIELDS)

CSS = """
footer { display: none !important; }
.gradio-container {
    max-width: 1100px !important;
    margin: auto !important;
    padding: 24px !important;
}
.tab-nav button {
    font-size: 14px !important;
    padding: 10px 16px !important;
}
"""

THEME_SCRIPT = """
<script>
function toggleTheme() {
    const root = document.documentElement;
    const isDark = root.classList.contains('dark');
    if (isDark) {
        root.classList.remove('dark');
        document.getElementById('themeBtn').textContent = '🌙';
    } else {
        root.classList.add('dark');
        document.getElementById('themeBtn').textContent = '☀️';
    }
}
</script>
<button id='themeBtn' onclick='toggleTheme()' style='position:fixed;top:12px;right:12px;z-index:9999;
width:38px;height:38px;border-radius:50%;background:#2a9d8f;color:white;border:none;
font-size:16px;cursor:pointer'>🌙</button>
"""

with gr.Blocks(title="ChitSync — English", css=CSS) as en_app:

    gr.HTML(THEME_SCRIPT)

    with gr.Row(equal_height=True):
        with gr.Column(scale=8):
            gr.Markdown("# 🏦 ChitSync")
            gr.Markdown("### Transparent. Digital. Instant. — Built for India")
        with gr.Column(scale=1, min_width=60):
            gr.Markdown("<div style='text-align:right;margin-top:12px;font-size:13px;color:#2a9d8f'>🌐 English</div>")

    with gr.Tabs():

        # HOME
        with gr.TabItem("🏠 Home"):
            home_cards_md = gr.HTML(get_home_cards())
            data = load_data()
            commission, dividend, prized_amount, total_collected, pending, paid_count = calculate_summary(data)
            gr.Markdown(f"**{data['chit_name']}** &nbsp;|&nbsp; **Month {data['current_month']}** &nbsp;|&nbsp; **{paid_count}/{data['members']} members paid** &nbsp;|&nbsp; Chit Value: ₹{data['chit_value']:,}")
            gr.Markdown("---")
            gr.HTML(f"""
<div style='display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:8px'>
    <div onclick="document.querySelectorAll('.tab-nav button')[1].click()"
    style='background:#e8f5f3;border:1.5px solid #2a9d8f;border-radius:16px;padding:28px 20px;text-align:center;cursor:pointer'>
        <div style='font-size:40px'>➕</div>
        <div style='font-size:16px;font-weight:600;margin-top:12px;color:#264653'>New Chit Fund</div>
        <div style='font-size:12px;color:#64748b;margin-top:6px'>Create a new chit fund from scratch</div>
    </div>
    <div onclick="document.querySelectorAll('.tab-nav button')[2].click()"
    style='background:#fefae0;border:1.5px solid #e9c46a;border-radius:16px;padding:28px 20px;text-align:center;cursor:pointer'>
        <div style='font-size:40px'>📤</div>
        <div style='font-size:16px;font-weight:600;margin-top:12px;color:#264653'>Upload & Digitize</div>
        <div style='font-size:12px;color:#64748b;margin-top:6px'>Upload chit book photo and digitize</div>
    </div>
    <div onclick="document.querySelectorAll('.tab-nav button')[3].click()"
    style='background:#e8f5f3;border:1.5px solid #2a9d8f;border-radius:16px;padding:28px 20px;text-align:center;cursor:pointer'>
        <div style='font-size:40px'>👤</div>
        <div style='font-size:16px;font-weight:600;margin-top:12px;color:#264653'>Member Dashboard</div>
        <div style='font-size:12px;color:#64748b;margin-top:6px'>View member details and send alerts</div>
    </div>
</div>""")
            gr.Markdown("<div style='text-align:center;margin-top:24px;color:#94a3b8;font-size:12px'>Powered by Ollama + EasyOCR + Gradio</div>")

        # NEW CHIT FUND
        with gr.TabItem("➕ New Chit Fund"):
            gr.Markdown("### Create a New Chit Fund")
            gr.Markdown("*Fill in the details to start a new chit fund*")
            with gr.Row():
                chit_name_input = gr.Textbox(label="Chit Fund Name", placeholder="e.g. Lakshmi Chit Fund")
                start_date_input = gr.Textbox(label="Start Date", value=str(date.today()))
            with gr.Row():
                chit_value_input = gr.Number(label="Chit Value (₹)", value=100000)
                num_members_input = gr.Number(label="Number of Members", value=10, precision=0)
            with gr.Row():
                monthly_sub_input = gr.Number(label="Monthly Subscription (₹)", value=5000)
                commission_input = gr.Number(label="Foreman Commission (%)", value=5)
            gr.Markdown("### Member Names *(one per line)*")
            member_names_input = gr.Textbox(
                label="Member Names",
                placeholder="Ravi\nLakshmi\nSuresh\n...",
                lines=10
            )
            create_btn = gr.Button("✅ Create Chit Fund", variant="primary", size="lg")
            create_output = gr.Markdown()
            new_chit_table = gr.HTML()

            gr.Markdown("---")
            gr.Markdown("### ⚙️ Manage Custom Fields")
            with gr.Row():
                suggested_dd = gr.Dropdown(choices=SUGGESTED_FIELDS, label="Pick from suggestions", scale=2)
                custom_field_input = gr.Textbox(label="Or type your own field name", scale=2)
                add_field_btn = gr.Button("➕ Add Field", variant="primary", scale=1)
            with gr.Row():
                remove_field_dd = gr.Dropdown(choices=get_custom_fields_list(), label="Select field to remove")
                remove_field_btn = gr.Button("🗑️ Remove Field", variant="stop")
            field_output = gr.Markdown()
            fields_table = gr.HTML()

            create_btn.click(
                create_new_chit,
                inputs=[chit_name_input, chit_value_input, num_members_input,
                        monthly_sub_input, commission_input, start_date_input, member_names_input],
                outputs=[create_output, new_chit_table]
            )
            add_field_btn.click(
                add_custom_field,
                inputs=[custom_field_input, suggested_dd],
                outputs=[field_output, remove_field_dd, fields_table]
            )
            remove_field_btn.click(
                remove_custom_field,
                inputs=[remove_field_dd],
                outputs=[field_output, remove_field_dd, fields_table]
            )

        # UPLOAD & DIGITIZE
        with gr.TabItem("📤 Upload & Digitize"):
            gr.Markdown("### Upload a photo of your physical Chit Book")
            gr.Markdown("*The AI agent will read and extract all member data automatically*")
            search_input = gr.Textbox(label="🔍 Search member by name", placeholder="Type a name...")
            image_input = gr.Image(label="Chit Book Photo", height=250)
            submit_btn = gr.Button("✨ Digitize with AI", variant="primary", size="lg")
            ledger_html = gr.HTML()
            submit_btn.click(show_ledger_ai, inputs=[image_input, search_input], outputs=ledger_html)
            search_input.change(lambda s: get_ledger_html(s), inputs=search_input, outputs=ledger_html)
            en_app.load(lambda: get_ledger_html(), outputs=ledger_html)

        # MEMBER DASHBOARD
        with gr.TabItem("👤 Member Dashboard"):
            gr.Markdown("### Member Ledger")
            dashboard_ledger = gr.HTML()
            gr.Markdown("### Select a member to view details")
            data = load_data()
            member_names_list = [m["name"] for m in data["members_list"]]
            member_dropdown = gr.Dropdown(
                choices=member_names_list,
                label="Select Member",
                value=member_names_list[0],
                elem_id="member_select"
            )
            member_output = gr.Markdown()
            with gr.Row():
                send_btn = gr.Button("📱 Send WhatsApp Alert", variant="primary", visible=False)
            alert_output = gr.Markdown()
            gr.Markdown("---")
            gr.Markdown("### ✏️ Edit Member Record")
            edit_status = gr.Dropdown(choices=["Paid", "Unpaid"], label="Update Payment Status")
            edit_btn = gr.Button("💾 Save Changes", variant="secondary")
            edit_output = gr.Markdown()

            member_dropdown.change(show_member, inputs=member_dropdown, outputs=[member_output, send_btn])
            send_btn.click(send_alert, inputs=member_dropdown, outputs=alert_output)
            edit_btn.click(edit_member, inputs=[member_dropdown, edit_status], outputs=[edit_output, dashboard_ledger])
            en_app.load(lambda: get_ledger_html(), outputs=dashboard_ledger)
            en_app.load(lambda: show_member(load_data()["members_list"][0]["name"]), outputs=[member_output, send_btn])

        # AUCTION CALCULATOR
        with gr.TabItem("🔨 Auction Calculator"):
            gr.Markdown("### Calculate dividend for any winning bid")
            bid_input = gr.Number(label="Enter Winning Bid (₹)", value=15000, minimum=1000, maximum=99000)
            calc_btn = gr.Button("Calculate", variant="primary")
            auction_output = gr.Markdown()
            calc_btn.click(calculate_auction, inputs=bid_input, outputs=auction_output)
            en_app.load(lambda: calculate_auction(15000), outputs=auction_output)

if __name__ == "__main__":
    en_app.launch(server_port=7861, prevent_thread_lock=True, quiet=True)