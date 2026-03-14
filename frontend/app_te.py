import gradio as gr
import pandas as pd

sample_data = [
    {"name": "రవి",    "amount": 5000, "paid": True,  "dividend": 500, "due": 0,    "months_paid": 3, "missed": 0},
    {"name": "లక్ష్మి","amount": 5000, "paid": True,  "dividend": 500, "due": 0,    "months_paid": 3, "missed": 0},
    {"name": "సురేష్", "amount": 5000, "paid": False, "dividend": 500, "due": 5000, "months_paid": 2, "missed": 2},
    {"name": "ప్రియ",  "amount": 5000, "paid": True,  "dividend": 500, "due": 0,    "months_paid": 3, "missed": 0},
    {"name": "రమేష్", "amount": 5000, "paid": False, "dividend": 500, "due": 5000, "months_paid": 1, "missed": 3},
    {"name": "సీత",   "amount": 5000, "paid": True,  "dividend": 500, "due": 0,    "months_paid": 3, "missed": 0},
    {"name": "కిరణ్",  "amount": 5000, "paid": True,  "dividend": 500, "due": 0,    "months_paid": 3, "missed": 0},
    {"name": "దీప",  "amount": 5000, "paid": False, "dividend": 500, "due": 5000, "months_paid": 2, "missed": 2},
    {"name": "అర్జున్",  "amount": 5000, "paid": True,  "dividend": 500, "due": 0,    "months_paid": 3, "missed": 0},
    {"name": "మీన",  "amount": 5000, "paid": True,  "dividend": 500, "due": 0,    "months_paid": 3, "missed": 0},
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
            status = "⚠️ హెచ్చరిక"
        elif m["paid"]:
            status = "✅ చెల్లించారు"
        else:
            status = "❌ చెల్లించలేదు"
        rows.append({
            "సభ్యుడు": m["name"],
            "నెలవారీ (₹)": f"₹{m['amount']:,}",
            "స్థితి": status,
            "డివిడెండ్ (₹)": f"₹{m['dividend']:,}",
            "బకాయి (₹)": f"₹{m['due']:,}",
            "చెల్లించిన నెలలు": f"{m['months_paid']}/{CURRENT_MONTH}",
            "మిస్": m["missed"]
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
### 🔨 వేలం ఫలితం

| వివరాలు | మొత్తం |
|---|---|
| చిట్ విలువ | ₹{CHIT_VALUE:,} |
| గెలిచిన బిడ్ | ₹{winning_bid:,.0f} |
| **ప్రైజ్డ్ మొత్తం** | **₹{prized_amount:,.0f}** |
| ఫోర్‌మన్ కమీషన్ (5%) | ₹{commission:,.0f} |
| **సభ్యుడికి డివిడెండ్** | **₹{dividend:,.0f}** |
| చెల్లించాల్సిన నికర మొత్తం | ₹{net_installment:,.0f} |

> 💡 ప్రతి సభ్యుడు ఈ నెల ₹5,000 బదులు ₹{net_installment:,.0f} చెల్లిస్తారు
"""

def show_member(name):
    if not name:
        return "", gr.update(visible=False)
    for m in sample_data:
        if m["name"] == name:
            commission, dividend, prized_amount, _, _, _ = calculate_summary()
            status_text = "✅ చెల్లించారు" if m["paid"] else "❌ చెల్లించలేదు"
            flag_text = f"\n> ⚠️ **హెచ్చరిక:** ఈ సభ్యుడు {m['missed']} చెల్లింపులు మిస్ చేశాడు!" if m["missed"] >= 2 else ""
            whatsapp = f"""📱 *వాట్సాప్ అలర్ట్ ప్రివ్యూ*

నమస్కారం {m['name']} గారు! 🙏

మీ చిట్ ఫండ్ వివరాలు:
- నెలవారీ చెల్లింపు: ₹{m['amount']:,}
- డివిడెండ్: ₹{dividend:.0f}
- చెల్లించాల్సిన మొత్తం: ₹{m['amount'] - dividend:.0f}
- స్థితి: {status_text}

_చిట్‌సింక్_ ✨"""

            info = f"""
## 👤 {m['name']}
{flag_text}

| వివరాలు | విలువ |
|--------|-------|
| నెలవారీ చందా | ₹{m['amount']:,} |
| చెల్లింపు స్థితి | {'✅ చెల్లించారు' if m['paid'] else '❌ చెల్లించలేదు'} |
| చెల్లించిన నెలలు | {m['months_paid']} లో {CURRENT_MONTH} |
| మిస్ అయిన చెల్లింపులు | {m['missed']} |
| ఈ నెల డివిడెండ్ | ₹{dividend:.0f} |
| చెల్లించాల్సిన నికర మొత్తం | ₹{m['amount'] - dividend:.0f} |
| మొత్తం బకాయి | ₹{m['due']:,} |

---

{whatsapp}
"""
            return info, gr.update(visible=True)
    return "సభ్యుడు కనుగొనబడలేదు", gr.update(visible=False)

def send_alert(name):
    if not name:
        return "⚠️ దయచేసి ముందు సభ్యుడిని ఎంచుకోండి"
    return f"✅ {name} కి వాట్సాప్ అలర్ట్ పంపబడింది!"

def edit_member(name, new_amount, new_status):
    if not name:
        return "⚠️ దయచేసి ముందు సభ్యుడిని ఎంచుకోండి"
    for m in sample_data:
        if m["name"] == name:
            if new_amount:
                m["amount"] = int(new_amount)
            if new_status == "చెల్లించారు":
                m["paid"] = True
                m["due"] = 0
            elif new_status == "చెల్లించలేదు":
                m["paid"] = False
                m["due"] = m["amount"]
            return f"✅ {name} రికార్డ్ అప్‌డేట్ అయింది!"
    return "సభ్యుడు కనుగొనబడలేదు"

commission, dividend, prized_amount, total_collected, pending, paid_count = calculate_summary()

def get_home_cards():
    return f"""
<div style='display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px'>
    <div style='background:#f0f9ff;padding:20px;border-radius:12px;text-align:center;border:1px solid #bae6fd'>
        <div style='font-size:32px;font-weight:bold;color:#0369a1'>{MEMBERS}</div>
        <div style='color:#64748b;font-size:13px;margin-top:4px'>మొత్తం సభ్యులు</div>
    </div>
    <div style='background:#f0fdf4;padding:20px;border-radius:12px;text-align:center;border:1px solid #86efac'>
        <div style='font-size:32px;font-weight:bold;color:#15803d'>₹{total_collected:,}</div>
        <div style='color:#64748b;font-size:13px;margin-top:4px'>మొత్తం సేకరించినది</div>
    </div>
    <div style='background:#fff7ed;padding:20px;border-radius:12px;text-align:center;border:1px solid #fed7aa'>
        <div style='font-size:32px;font-weight:bold;color:#c2410c'>₹{pending:,}</div>
        <div style='color:#64748b;font-size:13px;margin-top:4px'>పెండింగ్ బకాయిలు</div>
    </div>
    <div style='background:#fdf4ff;padding:20px;border-radius:12px;text-align:center;border:1px solid #e9d5ff'>
        <div style='font-size:32px;font-weight:bold;color:#7e22ce'>₹{dividend:.0f}</div>
        <div style='color:#64748b;font-size:13px;margin-top:4px'>డివిడెండ్ / సభ్యుడు</div>
    </div>
</div>"""

with gr.Blocks(
    title="చిట్‌సింక్",
    theme=gr.themes.Soft(),
    css="""
    .gradio-container { max-width: 1100px !important; margin: auto !important; padding: 24px !important; }
    footer { display: none !important; }
    .tab-nav button { font-size: 14px !important; padding: 10px 16px !important; }
    """
) as te_app:

    with gr.Row(equal_height=True):
        with gr.Column(scale=8):
            gr.Markdown("# 🏦 చిట్‌సింక్")
            gr.Markdown("### పారదర్శకంగా. డిజిటల్‌గా. తక్షణమే. — భారతదేశం కోసం")
        with gr.Column(scale=1, min_width=120):
            gr.Markdown("<div style='text-align:right;margin-top:12px;font-size:13px;color:#64748b'>🌐 తెలుగు</div>")

    with gr.Tabs():

        with gr.TabItem("🏠 హోమ్"):
            gr.Markdown(get_home_cards())
            gr.Markdown(f"**నెల {CURRENT_MONTH}** &nbsp;|&nbsp; **{paid_count}/{MEMBERS} సభ్యులు చెల్లించారు** &nbsp;|&nbsp; చిట్ విలువ: ₹{CHIT_VALUE:,} &nbsp;|&nbsp; గెలిచిన బిడ్: ₹{WINNING_BID:,}")
            gr.Markdown("---")
            gr.Markdown(f"""
<div style='display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:8px'>
    <div onclick="document.querySelectorAll('.tab-nav button')[1].click()"
    style='background:#ffffff;border:1px solid #e2e8f0;border-radius:16px;padding:28px 20px;text-align:center;cursor:pointer;box-shadow:0 1px 3px rgba(0,0,0,0.05)'>
        <div style='font-size:40px'>📤</div>
        <div style='font-size:16px;font-weight:600;margin-top:12px;color:#1e293b'>అప్‌లోడ్ & డిజిటైజ్</div>
        <div style='font-size:12px;color:#64748b;margin-top:6px;line-height:1.5'>మీ చిట్ బుక్ ఫోటో అప్‌లోడ్ చేయండి, వెంటనే డిజిటల్ లెడ్జర్ పొందండి</div>
    </div>
    <div onclick="document.querySelectorAll('.tab-nav button')[2].click()"
    style='background:#ffffff;border:1px solid #e2e8f0;border-radius:16px;padding:28px 20px;text-align:center;cursor:pointer;box-shadow:0 1px 3px rgba(0,0,0,0.05)'>
        <div style='font-size:40px'>👤</div>
        <div style='font-size:16px;font-weight:600;margin-top:12px;color:#1e293b'>సభ్యుల డాష్‌బోర్డ్</div>
        <div style='font-size:12px;color:#64748b;margin-top:6px;line-height:1.5'>సభ్యుని చెల్లింపు చరిత్ర మరియు వాట్సాప్ అలర్ట్ చూడండి</div>
    </div>
    <div onclick="document.querySelectorAll('.tab-nav button')[3].click()"
    style='background:#ffffff;border:1px solid #e2e8f0;border-radius:16px;padding:28px 20px;text-align:center;cursor:pointer;box-shadow:0 1px 3px rgba(0,0,0,0.05)'>
        <div style='font-size:40px'>🔨</div>
        <div style='font-size:16px;font-weight:600;margin-top:12px;color:#1e293b'>వేలం కాలిక్యులేటర్</div>
        <div style='font-size:12px;color:#64748b;margin-top:6px;line-height:1.5'>ఏదైనా బిడ్‌కు డివిడెండ్ మరియు ప్రైజ్డ్ మొత్తం లెక్కించండి</div>
    </div>
</div>""")
            gr.Markdown("<div style='text-align:center;margin-top:24px;color:#94a3b8;font-size:12px'>Ollama + EasyOCR + Gradio తో నిర్మించబడింది</div>")

        with gr.TabItem("📤 అప్‌లోడ్ & డిజిటైజ్"):
            gr.Markdown("### మీ చిట్ బుక్ ఫోటో అప్‌లోడ్ చేయండి")
            gr.Markdown("*AI ఏజెంట్ స్వయంచాలకంగా అన్ని సభ్యుల డేటాను చదువుతుంది*")
            search_input = gr.Textbox(label="🔍 పేరు ద్వారా వెతకండి", placeholder="పేరు టైప్ చేయండి...")
            image_input = gr.Image(label="చిట్ బుక్ ఫోటో", height=250)
            submit_btn = gr.Button("✨ AI తో డిజిటైజ్ చేయండి", variant="primary", size="lg")
            output_table = gr.Dataframe(label="📊 డిజిటల్ లెడ్జర్", wrap=True)
            submit_btn.click(show_ledger, inputs=[image_input, search_input], outputs=output_table)
            search_input.change(show_ledger, inputs=[image_input, search_input], outputs=output_table)
            te_app.load(lambda: show_ledger(None, ""), outputs=output_table)

        with gr.TabItem("👤 సభ్యుల డాష్‌బోర్డ్"):
            gr.Markdown("### సభ్యుడిని ఎంచుకోండి")
            member_names = [m["name"] for m in sample_data]
            member_dropdown = gr.Dropdown(choices=member_names, label="సభ్యుడిని ఎంచుకోండి", value="రవి")
            member_output = gr.Markdown()
            with gr.Row():
                send_btn = gr.Button("📱 వాట్సాప్ అలర్ట్ పంపండి", variant="primary", visible=False)
            alert_output = gr.Markdown()
            gr.Markdown("---")
            gr.Markdown("### ✏️ రికార్డ్ సవరించు")
            with gr.Row():
                edit_amount = gr.Number(label="నెలవారీ మొత్తం అప్‌డేట్ చేయండి (₹)", precision=0)
                edit_status = gr.Dropdown(choices=["చెల్లించారు", "చెల్లించలేదు"], label="చెల్లింపు స్థితి అప్‌డేట్ చేయండి")
            edit_btn = gr.Button("💾 మార్పులు సేవ్ చేయండి", variant="secondary")
            edit_output = gr.Markdown()
            member_dropdown.change(show_member, inputs=member_dropdown, outputs=[member_output, send_btn])
            send_btn.click(send_alert, inputs=member_dropdown, outputs=alert_output)
            edit_btn.click(edit_member, inputs=[member_dropdown, edit_amount, edit_status], outputs=edit_output)
            te_app.load(lambda: show_member("రవి"), outputs=[member_output, send_btn])

        with gr.TabItem("🔨 వేలం కాలిక్యులేటర్"):
            gr.Markdown("### గెలిచిన బిడ్‌కు డివిడెండ్ లెక్కించండి")
            bid_input = gr.Number(label="గెలిచిన బిడ్ నమోదు చేయండి (₹)", value=15000, minimum=1000, maximum=99000)
            calc_btn = gr.Button("లెక్కించండి", variant="primary")
            auction_output = gr.Markdown()
            calc_btn.click(calculate_auction, inputs=bid_input, outputs=auction_output)
            te_app.load(lambda: calculate_auction(15000), outputs=auction_output)

if __name__ == "__main__":
    te_app.launch(server_port=7862)