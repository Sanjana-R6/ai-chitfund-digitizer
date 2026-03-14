import gradio as gr
import pandas as pd

sample_data = [
    {"name": "Ravi",    "amount": 5000, "paid": True,  "dividend": 500, "due": 0,    "months_paid": 3},
    {"name": "Lakshmi","amount": 5000, "paid": True,  "dividend": 500, "due": 0,    "months_paid": 3},
    {"name": "Suresh", "amount": 5000, "paid": False, "dividend": 500, "due": 5000, "months_paid": 2},
    {"name": "Priya",  "amount": 5000, "paid": True,  "dividend": 500, "due": 0,    "months_paid": 3},
    {"name": "Ramesh", "amount": 5000, "paid": False, "dividend": 500, "due": 5000, "months_paid": 1},
    {"name": "Sita",   "amount": 5000, "paid": True,  "dividend": 500, "due": 0,    "months_paid": 3},
    {"name": "Kiran",  "amount": 5000, "paid": True,  "dividend": 500, "due": 0,    "months_paid": 3},
    {"name": "Deepa",  "amount": 5000, "paid": False, "dividend": 500, "due": 5000, "months_paid": 2},
    {"name": "Arjun",  "amount": 5000, "paid": True,  "dividend": 500, "due": 0,    "months_paid": 3},
    {"name": "Meena",  "amount": 5000, "paid": True,  "dividend": 500, "due": 0,    "months_paid": 3},
]

CHIT_VALUE = 100000
MEMBERS = 10
COMMISSION_PCT = 5
WINNING_BID = 15000
CURRENT_MONTH = 3

def calculate_summary(winning_bid=WINNING_BID):
    commission = (COMMISSION_PCT / 100) * CHIT_VALUE
    dividend = (winning_bid - commission) / MEMBERS
    prized_amount = CHIT_VALUE - winning_bid
    total_collected = sum(m["amount"] for m in sample_data if m["paid"])
    pending = sum(m["due"] for m in sample_data)
    paid_count = sum(1 for m in sample_data if m["paid"])
    return commission, dividend, prized_amount, total_collected, pending, paid_count

def show_ledger(image):
    rows = []
    for m in sample_data:
        rows.append({
            "Member": m["name"],
            "Monthly (₹)": f"₹{m['amount']:,}",
            "Status": "✅ Paid" if m["paid"] else "❌ Unpaid",
            "Dividend (₹)": f"₹{m['dividend']:,}",
            "Due (₹)": f"₹{m['due']:,}",
            "Months Paid": f"{m['months_paid']}/{CURRENT_MONTH}"
        })
    df = pd.DataFrame(rows)
    return df

def calculate_auction(winning_bid):
    if not winning_bid:
        return "Enter a bid amount above"
    winning_bid = float(winning_bid)
    commission = (COMMISSION_PCT / 100) * CHIT_VALUE
    dividend = (winning_bid - commission) / MEMBERS
    prized_amount = CHIT_VALUE - winning_bid
    net_installment = 5000 - dividend
    result = f"""
### 🔨 Auction Result

| | Amount |
|---|---|
| Chit Value | ₹{CHIT_VALUE:,} |
| Winning Bid | ₹{winning_bid:,.0f} |
| **Prized Amount** | **₹{prized_amount:,.0f}** |
| Foreman Commission (5%) | ₹{commission:,.0f} |
| **Dividend per Member** | **₹{dividend:,.0f}** |
| Net Installment to Pay | ₹{net_installment:,.0f} |

> 💡 Each member pays ₹{net_installment:,.0f} this month instead of ₹5,000
"""
    return result

def show_member(name):
    if not name:
        return ""
    for m in sample_data:
        if m["name"] == name:
            commission, dividend, prized_amount, _, _, _ = calculate_summary()
            status_text = "✅ Paid this month" if m["paid"] else "❌ Payment pending"
            whatsapp_msg = f"""📱 *WhatsApp Alert Preview*

నమస్కారం {m['name']} గారు! 🙏

మీ చిట్ ఫండ్ వివరాలు:
- నెలవారీ చెల్లింపు: ₹{m['amount']:,}
- డివిడెండ్: ₹{dividend:.0f}
- చెల్లించాల్సిన మొత్తం: ₹{m['amount'] - dividend:.0f}
- స్థితి: {status_text}

_Chit Fund Digitizer_ ✨"""

            info = f"""
## 👤 {m['name']}

| Detail | Value |
|--------|-------|
| Monthly Contribution | ₹{m['amount']:,} |
| Payment Status | {'✅ Paid' if m['paid'] else '❌ Unpaid'} |
| Months Paid | {m['months_paid']} of {CURRENT_MONTH} |
| Dividend This Month | ₹{dividend:.0f} |
| Net Amount Due | ₹{m['amount'] - dividend:.0f} |
| Outstanding | ₹{m['due']:,} |

---

{whatsapp_msg}
"""
            return info
    return "Member not found"

commission, dividend, prized_amount, total_collected, pending, paid_count = calculate_summary()

with gr.Blocks(
    title="Chit Fund Digitizer",
    theme=gr.themes.Soft(),
    css="""
    .gradio-container { max-width: 1000px !important; margin: auto !important; }
    .metric-card { text-align: center; padding: 10px; }
    footer { display: none !important; }
    """
) as app:

    gr.Markdown("""
    # 🏦 AI Chit Fund Digitizer
    ### Transparent. Digital. Instant. — Built for India 
    """)

    # Summary cards
    with gr.Row():
        with gr.Column():
            gr.Markdown(f"""
            <div style='background:#f0f9ff;padding:16px;border-radius:12px;text-align:center;border:1px solid #bae6fd'>
            <div style='font-size:28px;font-weight:bold;color:#0369a1'>{MEMBERS}</div>
            <div style='color:#64748b;font-size:13px'>Total Members</div>
            </div>
            """)
        with gr.Column():
            gr.Markdown(f"""
            <div style='background:#f0fdf4;padding:16px;border-radius:12px;text-align:center;border:1px solid #86efac'>
            <div style='font-size:28px;font-weight:bold;color:#15803d'>₹{total_collected:,}</div>
            <div style='color:#64748b;font-size:13px'>Total Collected</div>
            </div>
            """)
        with gr.Column():
            gr.Markdown(f"""
            <div style='background:#fff7ed;padding:16px;border-radius:12px;text-align:center;border:1px solid #fed7aa'>
            <div style='font-size:28px;font-weight:bold;color:#c2410c'>₹{pending:,}</div>
            <div style='color:#64748b;font-size:13px'>Pending Dues</div>
            </div>
            """)
        with gr.Column():
            gr.Markdown(f"""
            <div style='background:#fdf4ff;padding:16px;border-radius:12px;text-align:center;border:1px solid #e9d5ff'>
            <div style='font-size:28px;font-weight:bold;color:#7e22ce'>₹{dividend:.0f}</div>
            <div style='color:#64748b;font-size:13px'>Dividend / Member</div>
            </div>
            """)

    with gr.Row():
        gr.Markdown(f"**Month {CURRENT_MONTH}** &nbsp;|&nbsp; **{paid_count}/{MEMBERS} members paid** &nbsp;|&nbsp; Chit Value: ₹{CHIT_VALUE:,} &nbsp;|&nbsp; Winning Bid: ₹{WINNING_BID:,}")

    gr.Markdown("---")

    with gr.Tabs():

        # TAB 1 - Upload
        with gr.TabItem("📤 Upload & Digitize"):
            gr.Markdown("### Upload a photo of your physical Chit Book")
            gr.Markdown("*The AI agent will read it and extract all member data automatically*")
            image_input = gr.Image(label="Chit Book Photo", height=300)
            submit_btn = gr.Button("✨ Digitize with AI", variant="primary", size="lg")
            output_table = gr.Dataframe(label="📊 Digital Ledger", wrap=True)
            submit_btn.click(show_ledger, inputs=image_input, outputs=output_table)

        # TAB 2 - Member Dashboard
        with gr.TabItem("👤 Member Dashboard"):
            gr.Markdown("### Select a member to see their full details + WhatsApp alert")
            member_names = [m["name"] for m in sample_data]
            member_dropdown = gr.Dropdown(
                choices=member_names,
                label="Select Member",
                value="Ravi"
            )
            member_output = gr.Markdown()
            member_dropdown.change(show_member, inputs=member_dropdown, outputs=member_output)
            app.load(lambda: show_member("Ravi"), outputs=member_output)

        # TAB 3 - Auction Calculator
        with gr.TabItem("🔨 Auction Calculator"):
            gr.Markdown("### Calculate dividend and prized amount for any winning bid")
            bid_input = gr.Number(
                label="Enter Winning Bid (₹)",
                value=15000,
                minimum=1000,
                maximum=99000
            )
            calc_btn = gr.Button("Calculate", variant="primary")
            auction_output = gr.Markdown()
            calc_btn.click(calculate_auction, inputs=bid_input, outputs=auction_output)
            app.load(lambda: calculate_auction(15000), outputs=auction_output)

app.launch()