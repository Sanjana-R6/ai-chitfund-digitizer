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

DATA_DIR = "../data"
INDEX_FILE = os.path.join(DATA_DIR, "chits_index.json")
SUGGESTED_FIELDS = ["ఫోన్", "చిరునామా", "గ్యారెంటర్", "అప్పు తీసుకున్నారా", "గమనికలు",
                    "వృత్తి", "ఆధార్ నంబర్", "బ్యాంక్ అకౌంట్", "ఇమెయిల్", "అత్యవసర సంప్రదింపు"]

os.makedirs(DATA_DIR, exist_ok=True)

DEFAULT_CHIT = {
    "chit_name": "నమూనా చిట్ ఫండ్",
    "chit_value": 100000,
    "members": 10,
    "monthly_sub": 5000,
    "commission_pct": 5,
    "winning_bid": 15000,
    "current_month": 3,
    "start_date": "2024-01-01",
    "custom_fields": ["ఫోన్", "చిరునామా", "గ్యారెంటర్", "అప్పు తీసుకున్నారా", "గమనికలు"],
    "members_list": [
        {"name": "రవి",     "paid": True,  "due": 0,    "months_paid": 3, "missed": 0, "ఫోన్": "", "చిరునామా": "", "గ్యారెంటర్": "", "అప్పు తీసుకున్నారా": "లేదు", "గమనికలు": ""},
        {"name": "లక్ష్మి", "paid": True,  "due": 0,    "months_paid": 3, "missed": 0, "ఫోన్": "", "చిరునామా": "", "గ్యారెంటర్": "", "అప్పు తీసుకున్నారా": "లేదు", "గమనికలు": ""},
        {"name": "సురేష్",  "paid": False, "due": 5000, "months_paid": 2, "missed": 2, "ఫోన్": "", "చిరునామా": "", "గ్యారెంటర్": "", "అప్పు తీసుకున్నారా": "అవును", "గమనికలు": ""},
        {"name": "ప్రియ",   "paid": True,  "due": 0,    "months_paid": 3, "missed": 0, "ఫోన్": "", "చిరునామా": "", "గ్యారెంటర్": "", "అప్పు తీసుకున్నారా": "లేదు", "గమనికలు": ""},
        {"name": "రమేష్",  "paid": False, "due": 5000, "months_paid": 1, "missed": 3, "ఫోన్": "", "చిరునామా": "", "గ్యారెంటర్": "", "అప్పు తీసుకున్నారా": "అవును", "గమనికలు": ""},
        {"name": "సీత",    "paid": True,  "due": 0,    "months_paid": 3, "missed": 0, "ఫోన్": "", "చిరునామా": "", "గ్యారెంటర్": "", "అప్పు తీసుకున్నారా": "లేదు", "గమనికలు": ""},
        {"name": "కిరణ్",   "paid": True,  "due": 0,    "months_paid": 3, "missed": 0, "ఫోన్": "", "చిరునామా": "", "గ్యారెంటర్": "", "అప్పు తీసుకున్నారా": "లేదు", "గమనికలు": ""},
        {"name": "దీప",    "paid": False, "due": 5000, "months_paid": 2, "missed": 2, "ఫోన్": "", "చిరునామా": "", "గ్యారెంటర్": "", "అప్పు తీసుకున్నారా": "లేదు", "గమనికలు": ""},
        {"name": "అర్జున్", "paid": True,  "due": 0,    "months_paid": 3, "missed": 0, "ఫోన్": "", "చిరునామా": "", "గ్యారెంటర్": "", "అప్పు తీసుకున్నారా": "లేదు", "గమనికలు": ""},
        {"name": "మీన",    "paid": True,  "due": 0,    "months_paid": 3, "missed": 0, "ఫోన్": "", "చిరునామా": "", "గ్యారెంటర్": "", "అప్పు తీసుకున్నారా": "లేదు", "గమనికలు": ""},
    ]
}

def load_index():
    if os.path.exists(INDEX_FILE):
        try:
            with open(INDEX_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
        except:
            pass
    index = {"chits": ["నమూనా చిట్ ఫండ్"], "active": "నమూనా చిట్ ఫండ్"}
    save_index(index)
    save_chit("నమూనా చిట్ ఫండ్", DEFAULT_CHIT)
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
    return DEFAULT_CHIT.copy()

def save_chit(name, data):
    with open(chit_filename(name), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_all_chits():
    return load_index().get("chits", ["నమూనా చిట్ ఫండ్"])

def get_active_chit():
    return load_index().get("active", "నమూనా చిట్ ఫండ్")

def set_active_chit(name):
    index = load_index()
    index["active"] = name
    save_index(index)

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

def get_home_cards(chit_name=None):
    if not chit_name:
        chit_name = get_active_chit()
    data = load_chit(chit_name)
    commission, dividend, prized_amount, total_collected, pending, paid_count = calculate_summary(data)
    return f"""
<div style='display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:24px'>
    <div class='metric-box'>
        <div class='metric-value'>₹{total_collected:,.0f}</div>
        <div style='font-size:13px;margin-top:4px;color:var(--text-muted);font-weight:500'>మొత్తం సేకరించినది</div>
    </div>
    <div class='metric-box'>
        <div class='metric-value'>₹{pending:,.0f}</div>
        <div style='font-size:13px;margin-top:4px;color:var(--text-muted);font-weight:500'>పెండింగ్ బకాయిలు</div>
    </div>
    <div class='metric-box'>
        <div class='metric-value'>₹{prized_amount:,.0f}</div>
        <div style='font-size:13px;margin-top:4px;color:var(--text-muted);font-weight:500'>ప్రైజ్డ్ మొత్తం</div>
    </div>
    <div class='metric-box'>
        <div class='metric-value'>₹{dividend:,.0f}</div>
        <div style='font-size:13px;margin-top:4px;color:var(--text-muted);font-weight:500'>డివిడెండ్ / సభ్యుడు</div>
    </div>
</div>
<div style='background:rgba(0, 242, 254, 0.05);border:1px solid var(--primary);border-radius:12px;padding:12px 20px;font-size:14px;color:var(--text-main)'>
    <span style="color: var(--primary)">●</span> <b>{data['chit_name']}</b> &nbsp;|&nbsp; నెల {data['current_month']} &nbsp;|&nbsp;
    {paid_count}/{data['members']} సభ్యులు చెల్లించారు &nbsp;|&nbsp; విలువ: ₹{data['chit_value']:,}
</div>"""

def make_excel_table(chit_name=None, search=""):
    if not chit_name:
        chit_name = get_active_chit()
    data = load_chit(chit_name)
    commission, dividend, _, _, _, _ = calculate_summary(data)
    members_list = data["members_list"]
    custom_fields = data.get("custom_fields", [])
    monthly_sub = data["monthly_sub"]
    current_month = data["current_month"]
    if search:
        members_list = [m for m in members_list if search.lower() in m["name"].lower()]
    header_cols = ["#", "సభ్యుని పేరు", "నెలవారీ (₹)", "స్థితి", "డివిడెండ్ (₹)", "బకాయి (₹)", "చెల్లించిన నెలలు"] + custom_fields
    headers = "".join([
        f"<th style='background:#2a9d8f;color:#ffffff;padding:12px 16px;text-align:left;font-weight:600;font-size:13px;white-space:nowrap;border-right:1px solid #1e7d72'>{h}</th>"
        for h in header_cols
    ])
    rows_html = ""
    for i, m in enumerate(members_list):
        if m["missed"] >= 2:
            status_badge = "<span style='background:#fff3cd;color:#856404;padding:4px 12px;border-radius:12px;font-size:12px;font-weight:600'>⚠️ హెచ్చరిక</span>"
        elif m["paid"]:
            status_badge = "<span style='background:#d1fae5;color:#065f46;padding:4px 12px;border-radius:12px;font-size:12px;font-weight:600'>✅ చెల్లించారు</span>"
        else:
            status_badge = "<span style='background:#fee2e2;color:#991b1b;padding:4px 12px;border-radius:12px;font-size:12px;font-weight:600'>❌ చెల్లించలేదు</span>"
        row_bg = "#ffffff" if i % 2 == 0 else "#f8fffe"
        custom_cells = "".join([
            f"<td style='padding:12px 16px;font-size:13px;color:#1a1a1a;border-bottom:1px solid #e2f4f1;border-right:1px solid #e2f4f1'>{m.get(field, '')}</td>"
            for field in custom_fields
        ])
        due_color = "#e76f51" if m["due"] > 0 else "#2a9d8f"
        rows_html += f"""
        <tr style='background:{row_bg};cursor:pointer'
            onmouseover="this.style.background='#e8f5f3'"
            onmouseout="this.style.background='{row_bg}'"
            onclick="
                var dd = document.querySelector('#member_select_te input');
                if(dd) {{
                    var lastValue = dd.value;
                    dd.value = '{m['name']}';
                    var event = new Event('input', {{ bubbles: true }});
                    event.simulated = true;
                    var tracker = dd._valueTracker;
                    if (tracker) {{ tracker.setValue(lastValue); }}
                    dd.dispatchEvent(event);
                }}
            ">
            <td style='padding:12px 16px;font-size:13px;color:#2a9d8f;font-weight:700;border-bottom:1px solid #e2f4f1;border-right:1px solid #e2f4f1'>{i+1}</td>
            <td style='padding:12px 16px;font-size:13px;color:#1a1a1a;font-weight:600;border-bottom:1px solid #e2f4f1;border-right:1px solid #e2f4f1'>{m['name']}</td>
            <td style='padding:12px 16px;font-size:13px;color:#1a1a1a;border-bottom:1px solid #e2f4f1;border-right:1px solid #e2f4f1'>₹{monthly_sub:,}</td>
            <td style='padding:12px 16px;border-bottom:1px solid #e2f4f1;border-right:1px solid #e2f4f1'>{status_badge}</td>
            <td style='padding:12px 16px;font-size:13px;color:#2a9d8f;font-weight:600;border-bottom:1px solid #e2f4f1;border-right:1px solid #e2f4f1'>₹{dividend:,.0f}</td>
            <td style='padding:12px 16px;font-size:13px;color:{due_color};font-weight:600;border-bottom:1px solid #e2f4f1;border-right:1px solid #e2f4f1'>₹{m["due"]:,}</td>
            <td style='padding:12px 16px;font-size:13px;color:#1a1a1a;border-bottom:1px solid #e2f4f1;border-right:1px solid #e2f4f1'>{m["months_paid"]}/{current_month}</td>
            {custom_cells}
        </tr>"""
    return f"""
<div style='overflow-x:auto;border-radius:12px;border:1.5px solid #2a9d8f;margin-top:8px;box-shadow:0 2px 8px rgba(42,157,143,0.1)'>
    <table style='width:100%;border-collapse:collapse;font-family:sans-serif'>
        <thead><tr>{headers}</tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
</div>
<p style='font-size:12px;color:#64748b;margin-top:6px'>💡 ఏదైనా వరుసపై క్లిక్ చేయండి సభ్యుని వివరాలు చూడటానికి</p>"""

def switch_chit(chit_name):
    if not chit_name:
        return [gr.update()]*6
    set_active_chit(chit_name)
    data = load_chit(chit_name)
    member_names = [m["name"] for m in data["members_list"]]
    first = member_names[0] if member_names else None
    return (
        get_home_cards(chit_name),
        make_excel_table(chit_name),
        make_excel_table(chit_name),
        gr.update(choices=member_names, value=first),
        calculate_auction_for(chit_name, data.get("winning_bid", 15000)),
        f"**{chit_name}** కి మారారు"
    )

def calculate_auction_for(chit_name, winning_bid):
    if not winning_bid:
        return ""
    data = load_chit(chit_name)
    winning_bid = float(winning_bid)
    commission = round(data["chit_value"] * data["commission_pct"] / 100, 2)
    dividend = round((winning_bid - commission) / data["members"], 2)
    prized_amount = data["chit_value"] - winning_bid
    net_installment = data["monthly_sub"] - dividend
    data["winning_bid"] = int(winning_bid)
    save_chit(chit_name, data)
    return f"""
### 🔨 వేలం ఫలితం

| వివరాలు | మొత్తం |
|---|---|
| చిట్ విలువ | ₹{data['chit_value']:,} |
| గెలిచిన బిడ్ | ₹{winning_bid:,.0f} |
| **ప్రైజ్డ్ మొత్తం** | **₹{prized_amount:,.0f}** |
| ఫోర్‌మన్ కమీషన్ ({data['commission_pct']}%) | ₹{commission:,.0f} |
| **సభ్యుడికి డివిడెండ్** | **₹{dividend:,.0f}** |
| చెల్లించాల్సిన నికర మొత్తం | ₹{net_installment:,.0f} |

> 💡 ప్రతి సభ్యుడు ఈ నెల ₹{data['monthly_sub']:,} బదులు ₹{net_installment:,.0f} చెల్లిస్తారు
"""

def calculate_auction(winning_bid, chit_name=None):
    if not chit_name:
        chit_name = get_active_chit()
    return calculate_auction_for(chit_name, winning_bid)

def show_member(name, chit_name=None):
    if not name:
        return "", gr.update(visible=False), None, "చెల్లించారు", "{}"
    if not chit_name:
        chit_name = get_active_chit()
    data = load_chit(chit_name)
    commission, dividend, _, _, _, _ = calculate_summary(data)
    for m in data["members_list"]:
        if m["name"] == name:
            flag_text = f"\n> ⚠️ **హెచ్చరిక:** ఈ సభ్యుడు {m['missed']} చెల్లింపులు మిస్ చేశాడు!" if m["missed"] >= 2 else ""
            custom_rows = "".join([f"| {field} | {m.get(field, '-')} |\n" for field in data.get("custom_fields", [])])
            whatsapp = f"""📱 *వాట్సాప్ అలర్ట్ ప్రివ్యూ*

నమస్కారం {m['name']} గారు! 🙏

మీ చిట్ ఫండ్ వివరాలు:
- నెలవారీ చెల్లింపు: ₹{data['monthly_sub']:,}
- డివిడెండ్: ₹{dividend:.0f}
- బకాయి: ₹{m['due']:,}
- స్థితి: {'✅ చెల్లించారు' if m['paid'] else '❌ చెల్లించలేదు'}

_చిట్‌సింక్_ ✨"""
            info = f"""
## 👤 {m['name']}
{flag_text}

| వివరాలు | విలువ |
|--------|-------|
| నెలవారీ చందా | ₹{data['monthly_sub']:,} |
| చెల్లింపు స్థితి | {'✅ చెల్లించారు' if m['paid'] else '❌ చెల్లించలేదు'} |
| చెల్లించిన నెలలు | {m['months_paid']} లో {data['current_month']} |
| మిస్ అయిన చెల్లింపులు | {m['missed']} |
| ఈ నెల డివిడెండ్ | ₹{dividend:.0f} |
| చెల్లించాల్సిన నికర మొత్తం | ₹{m['due']:,} |
{custom_rows}
---
{whatsapp}
"""
            custom_vals = json.dumps({f: m.get(f, "") for f in data.get("custom_fields", [])}, ensure_ascii=False)
            return info, gr.update(visible=True), data['monthly_sub'], "చెల్లించారు" if m['paid'] else "చెల్లించలేదు", custom_vals
    return "సభ్యుడు కనుగొనబడలేదు", gr.update(visible=False), None, "చెల్లించారు", "{}"

def send_alert(name):
    if not name:
        return "⚠️ దయచేసి ముందు సభ్యుడిని ఎంచుకోండి"
    return f"✅ {name} కి వాట్సాప్ అలర్ట్ పంపబడింది!"

def edit_member(name, new_amount, new_status, custom_vals_json, chit_name=None):
    if not name:
        return "⚠️ దయచేసి ముందు సభ్యుడిని ఎంచుకోండి", make_excel_table()
    if not chit_name:
        chit_name = get_active_chit()
    data = load_chit(chit_name)
    for m in data["members_list"]:
        if m["name"] == name:
            if new_amount:
                data["monthly_sub"] = int(new_amount)
            if new_status == "చెల్లించారు":
                m["paid"] = True
                m["due"] = 0
                m["months_paid"] += 1
                m["missed"] = 0
            elif new_status == "చెల్లించలేదు":
                m["paid"] = False
                m["due"] = data["monthly_sub"]
                m["missed"] += 1
            try:
                custom_vals = json.loads(custom_vals_json) if custom_vals_json else {}
                for field, val in custom_vals.items():
                    if field in data["custom_fields"]:
                        m[field] = val
            except:
                pass
            save_chit(chit_name, data)
            return f"✅ {name} రికార్డ్ అప్‌డేట్ అయింది!", make_excel_table(chit_name)
    return "సభ్యుడు కనుగొనబడలేదు", make_excel_table(chit_name)

def show_ledger_ai(image, search="", chit_name=None):
    if not chit_name:
        chit_name = get_active_chit()
    data = load_chit(chit_name)
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
                save_chit(chit_name, data)
        except Exception as e:
            print(f"AI processing failed: {e}")
    return make_excel_table(chit_name, search)

def create_new_chit(chit_name, chit_value, num_members, monthly_sub, commission_pct, start_date, member_names_text):
    if not all([chit_name, chit_value, num_members, monthly_sub, member_names_text]):
        return "⚠️ దయచేసి అన్ని అవసరమైన ఫీల్డ్‌లను పూరించండి!", "", gr.update()
    names = [n.strip() for n in member_names_text.strip().split("\n") if n.strip()]
    if len(names) != int(num_members):
        return f"⚠️ మీరు {len(names)} పేర్లు నమోదు చేశారు కానీ {int(num_members)} సభ్యులు పేర్కొన్నారు!", "", gr.update()
    members_list = [{"name": n, "paid": False, "due": int(monthly_sub), "months_paid": 0, "missed": 0,
                     "ఫోన్": "", "చిరునామా": "", "గ్యారెంటర్": "", "అప్పు తీసుకున్నారా": "లేదు", "గమనికలు": ""} for n in names]
    new_data = {
        "chit_name": chit_name,
        "chit_value": int(chit_value),
        "members": int(num_members),
        "monthly_sub": int(monthly_sub),
        "commission_pct": float(commission_pct),
        "winning_bid": 0,
        "current_month": 1,
        "start_date": str(start_date),
        "custom_fields": ["ఫోన్", "చిరునామా", "గ్యారెంటర్", "అప్పు తీసుకున్నారా", "గమనికలు"],
        "members_list": members_list
    }
    save_chit(chit_name, new_data)
    index = load_index()
    if chit_name not in index["chits"]:
        index["chits"].append(chit_name)
    index["active"] = chit_name
    save_index(index)
    table = make_excel_table(chit_name)
    all_chits = get_all_chits()
    return f"✅ '{chit_name}' {int(num_members)} సభ్యులతో సృష్టించబడింది!", table, gr.update(choices=all_chits, value=chit_name)

def add_custom_field(field_name, suggested, chit_name=None):
    field = field_name.strip() if field_name and field_name.strip() else suggested
    if not field:
        return "⚠️ ముందు ఫీల్డ్ పేరు నమోదు చేయండి!", gr.update(), gr.update(), make_excel_table()
    if not chit_name:
        chit_name = get_active_chit()
    data = load_chit(chit_name)
    if field in data["custom_fields"]:
        return f"⚠️ '{field}' ఇప్పటికే ఉంది!", gr.update(), gr.update(), make_excel_table(chit_name)
    data["custom_fields"].append(field)
    for m in data["members_list"]:
        m[field] = ""
    save_chit(chit_name, data)
    fields = data["custom_fields"]
    return f"✅ ఫీల్డ్ '{field}' జోడించబడింది!", gr.update(choices=fields), gr.update(choices=fields), make_excel_table(chit_name)

def remove_custom_field(field_name, chit_name=None):
    if not field_name:
        return "⚠️ తొలగించడానికి ఫీల్డ్ ఎంచుకోండి!", gr.update(), gr.update(), make_excel_table()
    if not chit_name:
        chit_name = get_active_chit()
    data = load_chit(chit_name)
    if field_name not in data["custom_fields"]:
        return "ఫీల్డ్ కనుగొనబడలేదు!", gr.update(), gr.update(), make_excel_table(chit_name)
    data["custom_fields"].remove(field_name)
    for m in data["members_list"]:
        m.pop(field_name, None)
    save_chit(chit_name, data)
    fields = data["custom_fields"]
    return f"✅ ఫీల్డ్ '{field_name}' తొలగించబడింది!", gr.update(choices=fields), gr.update(choices=fields), make_excel_table(chit_name)

def get_custom_fields_list(chit_name=None):
    if not chit_name:
        chit_name = get_active_chit()
    return load_chit(chit_name).get("custom_fields", [])

CSS = """
/* Professor CSS Refinement - Advanced India-Fintech Aesthetic */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

:root {
    --primary: #00f2fe;    /* Neon Cyan */
    --secondary: #3a7bd5;  /* Deep Blue */
    --bg-dark: #0b0e14;    /* Deep Navy */
    --card-bg: rgba(255, 255, 255, 0.04);
    --glass-border: rgba(255, 255, 255, 0.1);
    --accent: #f59e0b;     /* Amber */
    --text-main: #f8fafc;
    --text-muted: #94a3b8;
}

body, .gradio-container {
    background: radial-gradient(circle at top right, #1e293b 0%, var(--bg-dark) 100%) !important;
    font-family: 'Times New Roman', Times, serif !important;
    color: var(--text-main) !important;
}

/* Big Action Cards */
.action-card {
    background: var(--card-bg) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 20px !important;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
    cursor: pointer !important;
    padding: 30px 20px !important;
    text-align: center;
    height: 100% !important;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

.action-card:hover {
    transform: translateY(-10px) scale(1.02);
    background: rgba(255, 255, 255, 0.08) !important;
    border-color: var(--primary) !important;
    box-shadow: 0 15px 40px rgba(0, 242, 254, 0.15) !important;
}

.action-card .icon {
    font-size: 48px;
    margin-bottom: 16px;
    filter: drop-shadow(0 0 10px rgba(0, 242, 254, 0.3));
}

.action-card .title {
    font-size: 20px;
    font-weight: 700;
    color: var(--primary);
    margin-bottom: 8px;
}

.action-card .desc {
    font-size: 13px;
    color: var(--text-muted);
}

/* Navigation & Tabs */
.nav-bar button, .tab-nav button {
    border: none !important;
    background: transparent !important;
    color: var(--text-muted) !important;
    font-weight: 600 !important;
    transition: 0.3s !important;
}

.nav-bar button:hover, .tab-nav button:hover {
    color: var(--primary) !important;
}

.tab-nav button[aria-selected="true"] {
    color: var(--primary) !important;
    border-bottom: 2px solid var(--primary) !important;
}

/* Metric Boxes */
.metric-box {
    background: rgba(255, 255, 255, 0.03) !important;
    border-radius: 16px !important;
    border-left: 4px solid var(--primary) !important;
    padding: 20px !important;
    border: 1px solid var(--glass-border);
}

.metric-value {
    color: var(--primary);
    font-size: 28px;
    font-weight: 800;
}

/* Form Elements Styling */
.gr-textbox, .gr-number, .gr-dropdown {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 12px !important;
    color: white !important;
}

.gr-button-primary {
    background: linear-gradient(135deg, var(--secondary) 0%, #2563eb 100%) !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(37, 99, 235, 0.2) !important;
    border-radius: 12px !important;
}

.gr-button-primary:hover {
    box-shadow: 0 8px 20px rgba(37, 99, 235, 0.4) !important;
    transform: translateY(-2px);
}

#chit-selector-te {
    background: rgba(0, 242, 254, 0.05) !important;
    border: 1.5px solid var(--primary) !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    color: var(--primary) !important;
}

footer { display: none !important; }
"""

_index = load_index()
_active = _index.get("active", "నమూనా చిట్ ఫండ్")
_all_chits = _index.get("chits", ["నమూనా చిట్ ఫండ్"])
_data = load_chit(_active)
_member_names = [m["name"] for m in _data["members_list"]]

with gr.Blocks(title="చిట్‌ఫండ్ — తెలుగు", css=CSS) as te_app:

    with gr.Row(equal_height=True):
        with gr.Column(scale=6):
            gr.HTML("<div style='font-size:32px; font-weight:800; color:var(--primary); font-family: \"Times New Roman\", serif'>🏦 చిట్‌ఫండ్</div>")
            gr.Markdown("### పారదర్శకంగా. డిజిటల్‌గా. తక్షణమే. — భారతదేశం కోసం")
        with gr.Column(scale=3):
            chit_selector = gr.Dropdown(
                choices=_all_chits,
                value=_active,
                label="ప్రస్తుతం చూస్తున్నది",
                elem_id="chit-selector-te"
            )
        with gr.Column(scale=1, min_width=60):
            gr.HTML("<div style='text-align:right;margin-top:12px;font-size:14px;font-weight:700;color:var(--primary); font-family: \"Times New Roman\", serif'>తెలుగు</div>")

    switch_status = gr.Markdown()

    with gr.Tabs() as main_tabs:

        # HOME
        with gr.TabItem("🏠 హోమ్", id=0):
            home_cards_md = gr.HTML(get_home_cards(_active))
            gr.Markdown("---")
            
            with gr.Row():
                with gr.Column(elem_classes=["action-card"]):
                    nc_btn = gr.Button("➕\n\nకొత్త చిట్ ఫండ్\nస్కీమా మరియు సభ్యుల సెటప్", variant="secondary", elem_classes=["action-card"])
                with gr.Column(elem_classes=["action-card"]):
                    ul_btn = gr.Button("📤\n\nఅప్‌లోడ్ & డిజిటైజ్\nAI ద్వారా లెడ్జర్ వెలికితీత", variant="secondary", elem_classes=["action-card"])
            
            with gr.Row():
                with gr.Column(elem_classes=["action-card"]):
                    db_btn = gr.Button("👤\n\nసభ్యుల డాష్‌బోర్డ్\nచెల్లింపులు మరియు హెచ్చరికలు", variant="secondary", elem_classes=["action-card"])
                with gr.Column(elem_classes=["action-card"]):
                    ac_btn = gr.Button("🔨\n\nవేలం కాలిక్యులేటర్\nబిడ్‌లు మరియు డివిడెండ్‌లు", variant="secondary", elem_classes=["action-card"])

            nc_btn.click(lambda: gr.Tabs(selected=1), None, main_tabs)
            ul_btn.click(lambda: gr.Tabs(selected=2), None, main_tabs)
            db_btn.click(lambda: gr.Tabs(selected=3), None, main_tabs)
            ac_btn.click(lambda: gr.Tabs(selected=4), None, main_tabs)

            gr.Markdown("<div style='text-align:center;margin-top:24px;color:var(--text-muted);font-size:12px'>Ollama + EasyOCR + Gradio తో నిర్మించబడింది</div>")

        # NEW CHIT FUND
        with gr.TabItem("➕ కొత్త చిట్ ఫండ్", id=1):
            gr.Markdown("### కొత్త చిట్ ఫండ్ సృష్టించండి")
            with gr.Row():
                chit_name_input = gr.Textbox(label="చిట్ ఫండ్ పేరు", placeholder="ఉదా: లక్ష్మి చిట్ ఫండ్")
                start_date_input = gr.Textbox(label="ప్రారంభ తేదీ", value=str(date.today()))
            with gr.Row():
                chit_value_input = gr.Number(label="చిట్ విలువ (₹)", value=100000)
                num_members_input = gr.Number(label="సభ్యుల సంఖ్య", value=10, precision=0)
            with gr.Row():
                monthly_sub_input = gr.Number(label="నెలవారీ చందా (₹)", value=5000)
                commission_input = gr.Number(label="ఫోర్‌మన్ కమీషన్ (%)", value=5)
            # member names label
            gr.Markdown("### సభ్యుల పేర్లు *(ఒక్కో వరుసలో)*")
            member_names_input = gr.Textbox(label="సభ్యుల పేర్లు", placeholder="రవి\nలక్ష్మి\nసురేష్\n...", lines=10)
            create_btn = gr.Button("✅ చిట్ ఫండ్ సృష్టించండి", variant="primary", size="lg")
            create_output = gr.Markdown()
            new_chit_table = gr.HTML()
            gr.Markdown("---")
            gr.Markdown("### ⚙️ ఫీల్డ్‌లు నిర్వహించండి")
            with gr.Row():
                suggested_dd = gr.Dropdown(choices=SUGGESTED_FIELDS, label="సూచనల నుండి ఎంచుకోండి", scale=2)
                custom_field_input = gr.Textbox(label="లేదా మీ స్వంత ఫీల్డ్ పేరు టైప్ చేయండి", scale=2)
                add_field_btn = gr.Button("➕ ఫీల్డ్ జోడించు", variant="primary", scale=1)
            with gr.Row():
                remove_field_dd = gr.Dropdown(choices=get_custom_fields_list(_active), label="తొలగించడానికి ఫీల్డ్ ఎంచుకోండి")
                remove_field_btn = gr.Button("🗑️ ఫీల్డ్ తొలగించు", variant="stop")
            field_output = gr.Markdown()
            fields_table = gr.HTML()

            create_btn.click(create_new_chit,
                inputs=[chit_name_input, chit_value_input, num_members_input,
                        monthly_sub_input, commission_input, start_date_input, member_names_input],
                outputs=[create_output, new_chit_table, chit_selector])
            add_field_btn.click(add_custom_field,
                inputs=[custom_field_input, suggested_dd, chit_selector],
                outputs=[field_output, suggested_dd, remove_field_dd, fields_table])
            remove_field_btn.click(remove_custom_field,
                inputs=[remove_field_dd, chit_selector],
                outputs=[field_output, suggested_dd, remove_field_dd, fields_table])

        # UPLOAD & DIGITIZE
        with gr.TabItem("📤 అప్‌లోడ్ & డిజిటైజ్", id=2):
            gr.Markdown("### మీ చిట్ బుక్ ఫోటో అప్‌లోడ్ చేయండి")
            search_input = gr.Textbox(label="🔍 పేరు ద్వారా వెతకండి", placeholder="పేరు టైప్ చేయండి...")
            image_input = gr.Image(label="చిట్ బుక్ ఫోటో", height=250)
            submit_btn = gr.Button("✨ AI తో డిజిటైజ్ చేయండి", variant="primary", size="lg")
            upload_ledger = gr.HTML()
            submit_btn.click(show_ledger_ai,
                inputs=[image_input, search_input, chit_selector],
                outputs=upload_ledger)
            search_input.change(
                lambda s, c: make_excel_table(c, s),
                inputs=[search_input, chit_selector],
                outputs=upload_ledger)
            te_app.load(lambda: make_excel_table(), outputs=upload_ledger)

        # MEMBER DASHBOARD
        with gr.TabItem("👤 సభ్యుల డాష్‌బోర్డ్", id=3):
            gr.Markdown("### సభ్యుల లెడ్జర్")
            gr.Markdown("*ఏదైనా వరుసపై క్లిక్ చేయండి సభ్యుని వివరాలు చూడటానికి*")
            dashboard_ledger = gr.HTML()
            gr.Markdown("---")
            member_dropdown = gr.Dropdown(
                choices=_member_names,
                label="సభ్యుడిని ఎంచుకోండి",
                value=_member_names[0] if _member_names else None,
                elem_id="member_select_te"
            )
            member_output = gr.Markdown()
            with gr.Row():
                send_btn = gr.Button("📱 వాట్సాప్ అలర్ట్ పంపండి", variant="primary", visible=False)
            alert_output = gr.Markdown()
            gr.Markdown("---")
            gr.Markdown("### ✏️ రికార్డ్ సవరించు")
            with gr.Row():
                edit_amount = gr.Number(label="నెలవారీ మొత్తం (₹)", precision=0)
                edit_status = gr.Dropdown(choices=["చెల్లించారు", "చెల్లించలేదు"], label="చెల్లింపు స్థితి")
            custom_fields_editor = gr.Textbox(
                label="కస్టమ్ ఫీల్డ్ విలువలు (JSON)",
                lines=3,
                placeholder='{"ఫోన్": "9999999999"}'
            )
            edit_btn = gr.Button("💾 మార్పులు సేవ్ చేయండి", variant="primary")
            edit_output = gr.Markdown()

            member_dropdown.change(
                lambda name, chit: show_member(name, chit),
                inputs=[member_dropdown, chit_selector],
                outputs=[member_output, send_btn, edit_amount, edit_status, custom_fields_editor]
            )
            send_btn.click(send_alert, inputs=member_dropdown, outputs=alert_output)
            edit_btn.click(edit_member,
                inputs=[member_dropdown, edit_amount, edit_status, custom_fields_editor, chit_selector],
                outputs=[edit_output, dashboard_ledger])
            te_app.load(lambda: make_excel_table(), outputs=dashboard_ledger)
            te_app.load(
                lambda: show_member(_member_names[0] if _member_names else "", _active),
                outputs=[member_output, send_btn, edit_amount, edit_status, custom_fields_editor]
            )

        # AUCTION CALCULATOR
        with gr.TabItem("🔨 వేలం కాలిక్యులేటర్", id=4):
            gr.Markdown("### గెలిచిన బిడ్‌కు డివిడెండ్ లెక్కించండి")
            bid_input = gr.Number(label="గెలిచిన బిడ్ నమోదు చేయండి (₹)", value=15000, minimum=1000, maximum=99000)
            calc_btn = gr.Button("లెక్కించండి", variant="primary")
            auction_output = gr.Markdown()
            calc_btn.click(calculate_auction,
                inputs=[bid_input, chit_selector],
                outputs=auction_output)
            te_app.load(lambda: calculate_auction(15000), outputs=auction_output)

    chit_selector.change(
        switch_chit,
        inputs=chit_selector,
        outputs=[home_cards_md, upload_ledger, dashboard_ledger,
                 member_dropdown, auction_output, switch_status]
    )

if __name__ == "__main__":
    landing.launch(server_port=7862, share=True)