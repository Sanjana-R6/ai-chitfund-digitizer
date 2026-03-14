"""
agent/agent.py
Chit Fund Backend Agent
-----------------------
Pipeline:
  1. OCR  → EasyOCR reads a chit-book image (Telugu + English)
  2. LLM  → Ollama structures the raw text into JSON
  3. Calc → Dividend, commission, bid-loss calculations
  4. Expose process_image(image_path) as the single public entry point

Dependencies (add to requirements.txt):
    easyocr
    requests
    pillow
"""

import json
import re
import requests
from pathlib import Path

# ── Optional: suppress EasyOCR/torch noise on import ──────────────────────────
import warnings
warnings.filterwarnings("ignore")
import easyocr

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG  (edit these if needed)
# ─────────────────────────────────────────────────────────────────────────────
OLLAMA_URL   = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"          # swap for any model you have pulled, e.g. "mistral"
OCR_LANGS    = ["en", "te"]      # English + Telugu
FOREMAN_COMMISSION_RATE = 0.05   # 5 % — standard under Chit Funds Act 1982

# ─────────────────────────────────────────────────────────────────────────────
# 1. OCR PIPELINE
# ─────────────────────────────────────────────────────────────────────────────

# Lazy-load the reader once (heavy init)
_reader = None

def _get_reader() -> easyocr.Reader:
    global _reader
    if _reader is None:
        print("[OCR] Loading EasyOCR model (first run may take a moment)…")
        _reader = easyocr.Reader(OCR_LANGS, gpu=False)
    return _reader


def run_ocr(image_path: str) -> str:
    """
    Read a chit-book image (JPEG / PNG / PDF page) with EasyOCR.
    Returns a single string of all detected text, one detection per line.
    """
    reader = _get_reader()
    results = reader.readtext(image_path, detail=0, paragraph=True)
    raw_text = "\n".join(results)
    print(f"[OCR] Extracted {len(raw_text)} chars from {Path(image_path).name}")
    return raw_text


# ─────────────────────────────────────────────────────────────────────────────
# 2. OLLAMA LLM — structure raw OCR text into JSON
# ─────────────────────────────────────────────────────────────────────────────

EXTRACTION_PROMPT = """You are a chit-fund data extractor for Indian chit funds regulated under the Chit Funds Act 1982.

Given the raw OCR text below (may contain Telugu and English), extract the following fields into a JSON object.
If a field is not present, use null.

Fields to extract:
- chit_value        : total chit value in ₹ (integer)
- num_members       : number of members in the chit group (integer)
- month_number      : auction month/installment number (integer)
- winning_bid       : lowest bid amount in ₹ (integer)  — this is what the prize winner bid
- member_name       : name of the prized/winning member (string)
- monthly_sub       : monthly subscription per member in ₹ (integer)
- foreman_name      : name of the foreman if mentioned (string)
- auction_date      : date of auction (string, any format found)
- members           : list of objects with name, amount_paid, month fields if individual entries present

Return ONLY valid JSON. No explanation, no markdown fences.

OCR TEXT:
\"\"\"
{ocr_text}
\"\"\"
"""

def run_llm_extraction(ocr_text: str) -> dict:
    """
    Send OCR text to local Ollama model.
    Returns a Python dict of structured chit-fund fields.
    """
    prompt = EXTRACTION_PROMPT.format(ocr_text=ocr_text)

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        raw_response = response.json().get("response", "")
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "[LLM] Cannot reach Ollama. Make sure it's running: `ollama serve`"
        )

    # Strip markdown fences if the model wraps in ```json … ```
    cleaned = re.sub(r"```(?:json)?|```", "", raw_response).strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        print(f"[LLM] Warning: could not parse JSON. Raw response:\n{raw_response}")
        data = {"_raw_llm_response": raw_response}

    print(f"[LLM] Structured fields: {list(data.keys())}")
    return data


# ─────────────────────────────────────────────────────────────────────────────
# 3. CALCULATION ENGINE
# ─────────────────────────────────────────────────────────────────────────────

def calculate_chit_figures(data: dict) -> dict:
    """
    Given structured LLM output, compute:
      - foreman_commission
      - prized_amount
      - dividend_per_member
      - net_installment_per_member
      - bid_loss  (what the winner foregoes vs full chit value)

    Formulas (Chit Funds Act 1982 standard):
      Prized Amount        = Chit Value − Winning Bid
      Foreman Commission   = Winning Bid × commission_rate
      Dividend per Member  = (Winning Bid − Foreman Commission) ÷ Num Members
      Net Installment      = Monthly Subscription − Dividend per Member
      Bid Loss             = Chit Value − Prized Amount  (= Winning Bid)
    """
    calcs = {}

    chit_value   = data.get("chit_value")
    winning_bid  = data.get("winning_bid")
    num_members  = data.get("num_members")
    monthly_sub  = data.get("monthly_sub")

    if None in (chit_value, winning_bid, num_members):
        calcs["calc_error"] = (
            "Missing one or more required fields: chit_value, winning_bid, num_members"
        )
        return {**data, **calcs}

    foreman_commission   = round(winning_bid * FOREMAN_COMMISSION_RATE, 2)
    prized_amount        = chit_value - winning_bid
    dividend_per_member  = round((winning_bid - foreman_commission) / num_members, 2)
    bid_loss             = winning_bid  # the discount the winner accepted

    calcs["foreman_commission"]   = foreman_commission
    calcs["prized_amount"]        = prized_amount
    calcs["dividend_per_member"]  = dividend_per_member
    calcs["bid_loss"]             = bid_loss

    if monthly_sub is not None:
        net_installment = round(monthly_sub - dividend_per_member, 2)
        calcs["net_installment_per_member"] = net_installment

    print(
        f"[CALC] Prized=₹{prized_amount} | "
        f"Commission=₹{foreman_commission} | "
        f"Dividend/member=₹{dividend_per_member}"
    )
    return {**data, **calcs}


# ─────────────────────────────────────────────────────────────────────────────
# 4. PUBLIC ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def process_image(image_path: str) -> dict:
    """
    Full pipeline:  image → OCR → LLM extraction → calculations → result dict

    Args:
        image_path: path to a chit-book image (JPEG, PNG, etc.)

    Returns:
        dict with all extracted + calculated fields, e.g.:
        {
            "chit_value": 100000,
            "winning_bid": 20000,
            "num_members": 20,
            "prized_amount": 80000,
            "dividend_per_member": 950.0,
            "foreman_commission": 1000.0,
            "net_installment_per_member": 4050.0,
            ...
        }
    """
    if not Path(image_path).exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    print(f"\n{'='*55}")
    print(f"  Processing: {Path(image_path).name}")
    print(f"{'='*55}")

    # Step 1 — OCR
    ocr_text = run_ocr(image_path)

    # Step 2 — LLM extraction
    structured = run_llm_extraction(ocr_text)

    # Step 3 — Calculations
    result = calculate_chit_figures(structured)

    print(f"[DONE] Result keys: {list(result.keys())}\n")
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Quick CLI test  →  python agent/agent.py path/to/image.jpg
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys, pprint
    if len(sys.argv) < 2:
        print("Usage: python agent/agent.py <image_path>")
        sys.exit(1)

    output = process_image(sys.argv[1])
    print("\n── Final Output ──")
    pprint.pprint(output, sort_dicts=False)