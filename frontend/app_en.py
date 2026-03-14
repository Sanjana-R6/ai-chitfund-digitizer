import gradio as gr
import pandas as pd

sample_data = [
    {"name": "Ravi",    "amount": 5000, "paid": True,  "dividend": 500, "due": 0,    "months_paid": 3, "missed": 0},
    {"name": "Lakshmi","amount": 5000, "paid": True,  "dividend": 500, "due": 0,    "months_paid": 3, "missed": 0},
    {"name": "Suresh", "amount": 5000, "paid": False, "dividend": 500, "due": 5000, "months_paid": 2, "missed": 2},
    {"name": "Priya",  "amount": 5000, "paid": True,  "dividend": 500, "due": 0,    "months_paid": 3, "missed": 0},
    {"name": "Ramesh", "amount": 5000, "paid": False, "dividend": 500, "due": 5000, "months_paid": 1, "missed": 3},
    {"name": "Sita",   "amount": 5000, "paid": True,  "dividend": 500, "due": 0,    "months_paid": 3, "missed": 0},
    {"name": "Kiran",  "amount": 5000, "paid": True,  "dividend": 500, "due": 0,    "months_paid": 3, "missed": 0},
    {"name": "Deepa",  "amount": 5000, "paid": False, "dividend": 500, "due": 5000, "months_paid": 2, "missed": 2},
    {"name": "Arjun",  "amount": 5000, "paid": True,  "dividend": 500, "due": 0,    "months_paid": 3, "missed": 0},
    {"name": "Meena",  "amount": 5000, "paid": True,  "dividend": 500, "due": 0,    "months_paid": 3, "missed": 0},
]

CHIT_VALUE = 100000
MEMBERS = 10
COMMISSION_PCT = 5
WINNING_BID = 15000
CURRENT_MONTH = 3

def calculate_summary():
    commission = (COMMISSION_PCT / 100) * CHIT_VALUE
    dividend = (WINNING_BID - commission) / MEMBERS
    prized_amount = CHIT_VALUE - WINNING_BID
    total_collected = sum(m["amount"] for m in sample_data if m["paid"])
    pending = sum(m["due"] for m in sample_data)
    paid_count = sum(1 for m in sample_data if m["paid"])
    return commission, dividend, prized_amount, total_collected, pending, paid_count

def show_ledger(image, search=""):
    rows = []
    for m in sample_data:
        if search and search.lower() not in m["name"].lower():
            continue
        if m["missed"] >= 2:
            status = "⚠️ Flagged"
        elif m["paid"]:
            status = "✅ Paid"
        else:
            status = "❌ Unpaid"
        rows.append({
            "Member": m["name"],
            "Monthly (₹)": f"₹{m['amount']:,}",
            "Status": status,
            "Dividend (₹)": f"₹{m['dividend']:,}",
            "Due (₹)": f"₹{m['due']:,}",
            "Months Paid": f"{m['months_paid']}/{CURRENT_MONTH}",
            "Missed": m["missed"]
        })
    return pd.DataFrame(rows)

def calculate_auction(winning_bid):
    if not winning_bid:
        return ""
    winning_bid = float(winning_bid)
    commission = (COMMISSION_PCT / 100) * CHIT_VALUE
    dividend = (winning_bid - commission) / MEMBERS
    prized_amount = CHIT_VALUE - winning_bid
    net_installment = 5000 - dividend
    return f"""
### 🔨 Auction Result

| Detail | Amount |
|---|---|
| Chit Value | ₹{CHIT_VALUE:,} |
| Winning Bid | ₹{winning_bid:,.0f} |
| **Prized Amount** | **₹{prized_amount:,.0f}** |
| Foreman Commission (5%) | ₹{commission:,.0f} |
| **Dividend per Member** | **₹{dividend:,.0f}** |
| Net Installment to Pay | ₹{net_installment:,.0f} |

> 💡 Each member pays ₹{net_installment:,.0f} this month instead of ₹5,000
"""

def show_member(name):
    if not name:
        return "", gr.update(visible=False)
    for m in sample_data:
        if m["name"] == name:
            commission, dividend, prized_amount, _, _, _ = calculate_summary()
            status_text = "✅ Paid this month" if m["paid"] else "❌ Payment pending"
            flag_text = f"\n> ⚠️ **Warning:** This member has missed {m['missed']} payments!" if m["missed"] >= 2 else ""
            whatsapp = f"""📱 *WhatsApp Alert Preview*

Hello {m['name']}! 🙏

Your Chit Fund Details:
- Monthly: ₹{m['amount']:,}
- Dividend: ₹{dividend:.0f}
- Amount Due: ₹{m['amount'] - dividend:.0f}
- Status: {status_text}

_ChitSync_✨"""

            info = f"""
## 👤 {m['name']}
{flag_text}

| Detail | Value |
|--------|-------|
| Monthly Contribution | ₹{m['amount']:,} |
| Payment Status | {'✅ Paid' if m['paid'] else '❌ Unpaid'} |
| Months Paid | {m['months_paid']} of {CURRENT_MONTH} |
| Missed Payments | {m['missed']} |
| Dividend This Month | ₹{dividend:.0f} |
| Net Amount Due | ₹{m['amount'] - dividend:.0f} |
| Outstanding | ₹{m['due']:,} |

---

{whatsapp}
"""
            return info, gr.update(visible=True)
    return "Member not found", gr.update(visible=False)

def send_alert(name):
    if not name:
        return "⚠️ Please select a member first"
    return f"✅ WhatsApp alert sent to {name} successfully!"

def edit_member(name, new_amount, new_status):
    if not name:
        return "⚠️ Please select a member first"
    for m in sample_data:
        if m["name"] == name:
            if new_amount:
                m["amount"] = int(new_amount)
            if new_status == "Paid":
                m["paid"] = True
                m["due"] = 0
            elif new_status == "Unpaid":
                m["paid"] = False
                m["due"] = m["amount"]
            return f"✅ Record updated for {name}!"
    return "Member not found"

commission, dividend, prized_amount, total_collected, pending, paid_count = calculate_summary()

def get_home_cards():
    return f"""
<div style='display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px'>
    <div style='background:#f0f9ff;padding:20px;border-radius:12px;text-align:center;border:1px solid #bae6fd'>
        <div style='font-size:32px;font-weight:bold;color:#0369a1'>{MEMBERS}</div>
        <div style='color:#64748b;font-size:13px;margin-top:4px'>Total Members</div>
    </div>
    <div style='background:#f0fdf4;padding:20px;border-radius:12px;text-align:center;border:1px solid #86efac'>
        <div style='font-size:32px;font-weight:bold;color:#15803d'>₹{total_collected:,}</div>
        <div style='color:#64748b;font-size:13px;margin-top:4px'>Total Collected</div>
    </div>
    <div style='background:#fff7ed;padding:20px;border-radius:12px;text-align:center;border:1px solid #fed7aa'>
        <div style='font-size:32px;font-weight:bold;color:#c2410c'>₹{pending:,}</div>
        <div style='color:#64748b;font-size:13px;margin-top:4px'>Pending Dues</div>
    </div>
    <div style='background:#fdf4ff;padding:20px;border-radius:12px;text-align:center;border:1px solid #e9d5ff'>
        <div style='font-size:32px;font-weight:bold;color:#7e22ce'>₹{dividend:.0f}</div>
        <div style='color:#64748b;font-size:13px;margin-top:4px'>Dividend / Member</div>
    </div>
</div>"""

with gr.Blocks(
    title="ChitSync — English",
    theme=gr.themes.Soft(),
    css="""
    .gradio-container { max-width: 1100px !important; margin: auto !important; padding: 24px !important; }
    footer { display: none !important; }
    .tab-nav button { font-size: 14px !important; padding: 10px 16px !important; }
    """
) as en_app:

    with gr.Row(equal_height=True):
        with gr.Column(scale=8):
            gr.Markdown("# 🏦 ChitSync")
            gr.Markdown("### Transparent. Digital. Instant. — Built for India")
        with gr.Column(scale=1, min_width=120):
            gr.Markdown("<div style='text-align:right;margin-top:12px;font-size:13px;color:#64748b'>🌐 English</div>")

    with gr.Tabs():

        with gr.TabItem("🏠 Home"):
            gr.Markdown(get_home_cards())
            gr.Markdown(f"**Month {CURRENT_MONTH}** &nbsp;|&nbsp; **{paid_count}/{MEMBERS} members paid** &nbsp;|&nbsp; Chit Value: ₹{CHIT_VALUE:,} &nbsp;|&nbsp; Winning Bid: ₹{WINNING_BID:,}")
            gr.Markdown("---")
            gr.Markdown(f"""
<div style='display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:8px'>
    <div onclick="document.querySelectorAll('.tab-nav button')[1].click()"
    style='background:#ffffff;border:1px solid #e2e8f0;border-radius:16px;padding:28px 20px;text-align:center;cursor:pointer;box-shadow:0 1px 3px rgba(0,0,0,0.05)'>
        <div style='font-size:40px'>📤</div>
        <div style='font-size:16px;font-weight:600;margin-top:12px;color:#1e293b'>Upload & Digitize</div>
        <div style='font-size:12px;color:#64748b;margin-top:6px;line-height:1.5'>Upload your chit book photo and get a digital ledger instantly</div>
    </div>
    <div onclick="document.querySelectorAll('.tab-nav button')[2].click()"
    style='background:#ffffff;border:1px solid #e2e8f0;border-radius:16px;padding:28px 20px;text-align:center;cursor:pointer;box-shadow:0 1px 3px rgba(0,0,0,0.05)'>
        <div style='font-size:40px'>👤</div>
        <div style='font-size:16px;font-weight:600;margin-top:12px;color:#1e293b'>Member Dashboard</div>
        <div style='font-size:12px;color:#64748b;margin-top:6px;line-height:1.5'>View any member's payment history and WhatsApp alert</div>
    </div>
    <div onclick="document.querySelectorAll('.tab-nav button')[3].click()"
    style='background:#ffffff;border:1px solid #e2e8f0;border-radius:16px;padding:28px 20px;text-align:center;cursor:pointer;box-shadow:0 1px 3px rgba(0,0,0,0.05)'>
        <div style='font-size:40px'>🔨</div>
        <div style='font-size:16px;font-weight:600;margin-top:12px;color:#1e293b'>Auction Calculator</div>
        <div style='font-size:12px;color:#64748b;margin-top:6px;line-height:1.5'>Calculate dividend and prized amount for any winning bid</div>
    </div>
</div>""")
            gr.Markdown("<div style='text-align:center;margin-top:24px;color:#94a3b8;font-size:12px'>Powered by Ollama + EasyOCR + Gradio</div>")

        with gr.TabItem("📤 Upload & Digitize"):
            gr.Markdown("### Upload a photo of your physical Chit Book")
            gr.Markdown("*The AI agent will read and extract all member data automatically*")
            search_input = gr.Textbox(label="🔍 Search member by name", placeholder="Type a name...")
            image_input = gr.Image(label="Chit Book Photo", height=250)
            submit_btn = gr.Button("✨ Digitize with AI", variant="primary", size="lg")
            output_table = gr.Dataframe(label="📊 Digital Ledger", wrap=True)
            submit_btn.click(show_ledger, inputs=[image_input, search_input], outputs=output_table)
            search_input.change(show_ledger, inputs=[image_input, search_input], outputs=output_table)
            en_app.load(lambda: show_ledger(None, ""), outputs=output_table)

        with gr.TabItem("👤 Member Dashboard"):
            gr.Markdown("### Select a member to view details")
            member_names = [m["name"] for m in sample_data]
            member_dropdown = gr.Dropdown(choices=member_names, label="Select Member", value="Ravi")
            member_output = gr.Markdown()
            with gr.Row():
                send_btn = gr.Button("📱 Send WhatsApp Alert", variant="primary", visible=False)
            alert_output = gr.Markdown()
            gr.Markdown("---")
            gr.Markdown("### ✏️ Edit Member Record")
            with gr.Row():
                edit_amount = gr.Number(label="Update Monthly Amount (₹)", precision=0)
                edit_status = gr.Dropdown(choices=["Paid", "Unpaid"], label="Update Payment Status")
            edit_btn = gr.Button("💾 Save Changes", variant="secondary")
            edit_output = gr.Markdown()
            member_dropdown.change(show_member, inputs=member_dropdown, outputs=[member_output, send_btn])
            send_btn.click(send_alert, inputs=member_dropdown, outputs=alert_output)
            edit_btn.click(edit_member, inputs=[member_dropdown, edit_amount, edit_status], outputs=edit_output)
            en_app.load(lambda: show_member("Ravi"), outputs=[member_output, send_btn])

        with gr.TabItem("🔨 Auction Calculator"):
            gr.Markdown("### Calculate dividend for any winning bid")
            bid_input = gr.Number(label="Enter Winning Bid (₹)", value=15000, minimum=1000, maximum=99000)
            calc_btn = gr.Button("Calculate", variant="primary")
            auction_output = gr.Markdown()
            calc_btn.click(calculate_auction, inputs=bid_input, outputs=auction_output)
            en_app.load(lambda: calculate_auction(15000), outputs=auction_output)

if __name__ == "__main__":
    en_app.launch(server_port=7861)